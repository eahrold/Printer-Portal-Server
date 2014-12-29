'''A collection of helper functions'''
import os
import json
import urllib2

from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.conf import settings

from printer_portal.utils import site_info
from printers.models import SubscriptionPrinterList
from sparkle.models import Version


def github_latest_release(repo_dict):
    """Download the latest release based on a
    a user's repo"""
    user = repo_dict['user']
    repo = repo_dict['repo']
    print repo_dict

    print user
    print repo

    if not user or not repo:
        return None

    supported_file_types = ['dmg', 'zip', 'gz']

    try:
        dest = str(
            u'https://api.github.com/repos/%s/%s/releases' %
            (user, repo))
        data = json.load(urllib2.urlopen(dest))
        latest_release = data[0]['assets'][0]['browser_download_url']
        for file_type in supported_file_types:
            if latest_release.lower().endswith(file_type):
                return latest_release
    except IndexError:
        pass
    except urllib2.HTTPError:
        pass

    return None


def generate_printer_dict_from_list(request, list_object):
    '''constructs an xml/plist from objects.all()'''

    plist = []
    printers = list_object.printers.all()
    pp_site_info = site_info(request)

    if settings.SERVE_FILES and Version.objects.all():
        pp_site_info = site_info(request)
        update_server = os.path.join(pp_site_info['root'],
                                     pp_site_info['subpath'],
                                     'sparkle/client/appcast.xml',)
    else:
        update_server = settings.GITHUB_APPCAST_URL

    for printer in printers:
        printer_dict = {'name': printer.name,
                        'host': printer.host,
                        'protocol': printer.protocol,
                        'description': printer.description,
                        'location': printer.location,
                        'model': printer.model }

        if printer.ppd_file and 'root' in pp_site_info:
            ppd_url = os.path.join(pp_site_info['root'],\
                            printer.ppd_file.url.lstrip('/'))
            printer_dict["ppd_url"] = ppd_url

        option_objects = printer.options.all()
        options = []
        for opt in option_objects:
            options.append(opt.option)

        if options:
            printer_dict['options'] = options

        # If the class is a subscripton list override
        #  the location property with the subnet variable
        if isinstance(list_object, SubscriptionPrinterList):
            printer_dict['location'] = '%s_pi-printer' % (list_object.subnet)

        plist.append(printer_dict)

    xml = {'printerList': plist, 'updateServer': update_server}
    return xml


def auto_process_form(request, pk, cls, form_cls, template, redir):
    '''Convience function when form needs no special post processing'''
    instance = None
    if id:
        instance = cls.objects.get(id=pk)
    if request.POST:
        form = form_cls(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect(redir)
    else:
        form = form_cls(instance=instance)
    return render_to_response(template,
                              {'form': form, 'instance': instance}, context_instance=RequestContext(request))
