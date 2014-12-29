import os
import subprocess
import zipfile
import tempfile
import shutil
import plistlib
import platform

from django.db import models
from django.conf import settings
from django.dispatch import receiver
from validators import validate_only_one_instance

from sparkle.utils import get_dsa_signature


class PrivateKey(models.Model):

    def clean(self):
        validate_only_one_instance(self)

    #The DSA Key to sign the update
    private_key = models.FileField(upload_to='private/')


class Application(models.Model):
    """A sparkle application"""

    name = models.CharField(max_length=50)

    def __unicode__(self):
        return u'%s' % self.name


class GitHubVersion(models.Model):
    url = models.URLField(max_length=200)
    last_checked = models.DateField()


class Version(models.Model):
    """A version for a given application"""

    application = models.ForeignKey(Application)

    title = models.CharField(max_length=100)
    version = models.CharField(blank=True, null=True, max_length=10)
    short_version = models.CharField(blank=True, null=True, max_length=50)
    dsa_signature = models.CharField(blank=True, null=True, max_length=80)
    length = models.CharField(blank=True, null=True, max_length=20)
    release_notes = models.TextField(blank=True, null=True)
    minimum_system_version = models.CharField(
        blank=True,
        null=True,
        max_length=10)
    published = models.DateTimeField(auto_now_add=True)
    update = models.FileField(upload_to='sparkle/')
    active = models.BooleanField(default=False)

    def __unicode__(self):
        return u'%s' % self.title

    def mark_length(self, app_bundle_path, updated_fields_array):
        total_size = 0
        for walked in os.walk(app_bundle_path):
            # walked is a tuple when unpacked is (dirpath, dirnames, filenames)
            filenames = walked[2]
            dirpath = walked[0]
            for a_file in filenames:
                file_path = os.path.join(dirpath, a_file)
                total_size += os.path.getsize(file_path)

        self.length = total_size
        updated_fields_array.append('length')

    def mark_version(self, app_bundle_path, updated_fields_array):
        '''Mark version fields to update based on a app bundle path'''
        info_plist = os.path.join(app_bundle_path, 'Contents/Info.plist')
        if os.path.exists(info_plist):
            plist = plistlib.readPlist(info_plist)

            if not self.version and 'CFBundleVersion' in plist:
                self.version = plist.get('CFBundleVersion')
                updated_fields_array.append('version')

            if not self.short_version and 'CFBundleShortVersionString' in plist:
                self.short_version = plist.get('CFBundleShortVersionString')
                updated_fields_array.append('short_version')

            if not self.minimum_system_version and 'LSMinimumSystemVersion' in plist:
                self.minimum_system_version = plist.get(
                    'LSMinimumSystemVersion')
                updated_fields_array.append('minimum_system_version')

    def save(self, *args, **kwargs):
        pre_update_path = self.update.path
        super(Version, self).save(*args, **kwargs)

        update_fields = []
        is_tmp_dir = False
        if not pre_update_path == self.update.path:

            # It's only required to have a private key
            # when the applicaiton is not otherwise codesigned.
            # If there's no key, don't update the fields.
            private_key = PrivateKey.objects.all()
            if private_key.count():
                pks = PrivateKey.objects.all()[:1].get()
                if pks:
                    spk = pks.private_key.path

                    # If we've found a private key, and a dsa_signature hasn't been
                    # explicitly set, generate it now, and mark it to get
                    # updated.
                    if spk and not self.dsa_signature:
                        if os.path.exists(spk):
                            self.dsa_signature = get_dsa_signature(
                                self.update.path,
                                spk)
                            update_fields.append('dsa_signature')

            # If there is no length and it is a zip file
            # extract it to a tempdir and calculate the length
            # also parse the plist file for versions
            update_extension = os.path.splitext(self.update.path)[1]

            app_bundle_path = None
            if update_extension == '.app':
                app_bundle_path = self.update.path

            # If it's a DMG and we're running on osx open the dmg
            if update_extension == '.dmg' and platform.system() is "Darwin":
                pass

            if update_extension == '.zip':
                # Unzip the file first, then
                zip_file = zipfile.ZipFile(self.update.path)
                tempdir = tempfile.mkdtemp()
                files = zip_file.namelist()

                for a_file in files:
                    if a_file.endswith('/'):
                        the_direcotry = os.path.join(tempdir, a_file)
                        if not app_bundle_path:
                            is_tmp_dir = True
                            app_bundle_path = the_direcotry
                            os.makedirs(the_direcotry)
                    else:
                        zip_file.extract(a_file, tempdir)

            self.mark_version(app_bundle_path, update_fields)
            self.mark_length(app_bundle_path, update_fields)

            # Clean up.
            if is_tmp_dir:
                shutil.rmtree(app_bundle_path)

            print("Updating version signing for %s", update_fields)
            super(Version, self).save(update_fields=update_fields)


class SystemProfileReport(models.Model):

    """A system profile report"""

    ip_address = models.IPAddressField()
    added = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'SystemProfileReport'


class SystemProfileReportRecord(models.Model):

    """A key/value pair for a system profile report"""

    report = models.ForeignKey(SystemProfileReport)
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=80)

    def __unicode__(self):
        return u'%s: %s' % (self.key, self.value)


def get_file_attr(sender):
    if sender == Version:
        attr = 'update'
    elif sender == PrivateKey:
        attr = 'private_key'
    else:
        return None

    return attr


@receiver(models.signals.post_delete)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    attr = get_file_attr(sender)
    if attr:
        the_file = getattr(instance, attr, None)
        if the_file and os.path.isfile(the_file.path):
            os.remove(the_file.path)


@receiver(models.signals.pre_save)
def auto_delete_file_on_change(sender, instance, **kwargs):
    '''If the appcast version file has changed delete the old one'''
    try:
        pre_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return False

    attr = get_file_attr(sender)
    if attr:
        old_file = getattr(pre_instance, attr, None)
        new_file = getattr(instance, attr, None)

        if old_file and not old_file == new_file:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)

    return True
