from os import path as os_path

from django import template
from django.conf import settings

from django.template.defaultfilters import stringfilter
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

from urlparse import urlunparse
from urllib2 import quote
register = template.Library()

def _gen_url(site_info, value):
    scheme = site_info.get('scheme')
    host = site_info.get('host')
    path = quote(os_path.join(site_info.get('subpath'), value))
    return scheme, host, path

@register.filter(is_safe=True)
def client_open_url(value, site_info):
    '''Link to open the url in the client application'''
    url_type = settings.CLIENT_URL_TYPE
    scheme, host, path = _gen_url(site_info, value)
    scheme = scheme.replace('http', url_type)
    return mark_safe(
        urlunparse([scheme, host, path, None, None, None])
    )

@register.filter(is_safe=True)
def xml_display_url(value, site_info):
    '''Link to open the xml in a browser'''
    scheme, host, path = _gen_url(site_info, value)
    return mark_safe(
        urlunparse([scheme, host, os_path.join(path, 'view'), None, None, None])
    )
