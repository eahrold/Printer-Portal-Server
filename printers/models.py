'''Models'''

import os
import datetime
from django.utils import timezone
from django.db import models
from django.dispatch import receiver
from django.conf import settings
from printer_portal.utils import delete_file_on_change, \
    delete_file_on_delete


class PPClientGitHubRelease(models.Model):
    url = models.URLField(max_length=200)
    last_checked = models.DateField()

class Option(models.Model):
    '''Option model object'''
    option = models.CharField(max_length=200, blank=True, unique=True)

    def __unicode__(self):
        return u'%s' % self.option


class Printer(models.Model):
    '''Printer model object'''

    supported_protocols = (
                           ("ipp", "ipp"),
                           ("ipps", "ipps"),
                           ("http", "http"),
                           ("https", "https"),
                           ("socket", "socket"),
                           ("lpd", "lpd"),
                           )

    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200, blank=True)
    host = models.CharField(max_length=200)
    protocol = models.CharField(choices = supported_protocols,
                                default = 'ipp',
                                max_length = 200)
    location = models.CharField(max_length=200, blank=True)
    model = models.CharField(max_length=200, blank=True)
    ppd_file = models.FileField(upload_to='ppds/', blank=True, null=True)
    options = models.ManyToManyField(Option, blank=True, null=True)

    def __unicode__(self):
        return u'%s' % self.description or self.name

    def get_absolute_url(self):
        return "/printers/%i/" % self.id

    def get_details_url(self):
        return "/printer/details/%i/" % self.id


class PrinterList(models.Model):
    '''Printer lists are the core objects '''
    #Name of the printer list. This should not have any spaces.
    name = models.CharField(max_length=200, unique=True)

    # Printer objects to include in the list.
    printers = models.ManyToManyField(Printer, blank=True)

    # Is the list displayed on the front page or does
    # it need to be explicitly requested by URL
    public = models.BooleanField(default=True)

    def __unicode__(self):
        return u'%s' % self.name


class SubscriptionPrinterList(models.Model):
    subnet = models.CharField(max_length=200, unique=True)
    printers = models.ManyToManyField(Printer, blank=True)

    def __unicode__(self):
        return u'%s' % self.subnet

    @classmethod
    def instance_for_ip(cls, client_ip):
        '''return the subscription list for a specific ip address'''

        # inspired by https://lukasklein.com/blog/django-ip-cidr-check/
        byte_to_bits = lambda b: bin(int(b))[2:].rjust(8, '0')
        ip_to_bits = lambda ip: ''.join(
            [byte_to_bits(b) for b in ip.split('.')])
        client_ip_bits = ip_to_bits(client_ip)

        for _list in cls.objects.all():
            ip_addr, snet = _list.subnet.split('/')

            ip_bits = ip_to_bits(ip_addr)
            if client_ip_bits[:int(snet)] == ip_bits[:int(snet)]:
                return _list


@receiver(models.signals.post_delete, sender=Printer)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    return delete_file_on_delete(instance, 'ppd_file')


@receiver(models.signals.pre_save, sender=Printer)
def auto_delete_file_on_change(sender, instance, **kwargs):
    return delete_file_on_change(sender, instance, 'ppd_file')
