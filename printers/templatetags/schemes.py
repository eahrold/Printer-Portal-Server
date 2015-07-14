from os import path as os_path

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

from urlparse import urlunparse
from urllib2 import quote

register = template.Library()

def _expand_url_dict(site_info, request_path):
    '''Expand a site info dictionary into a tuple to be
    passed into urlunparse, and construct the correct path
    parameter based on the subpath key.
    '''
    scheme = site_info.get('scheme')
    host = site_info.get('host')
    path = quote(os_path.join(site_info.get('subpath'), request_path))
    return scheme, host, path

@register.filter(is_safe=True)
def client_open_url(request_path, site_info):
    '''Construct the url that triggers in the client application to open'''

    url_type = settings.CLIENT_URL_TYPE
    scheme, host, path = _expand_url_dict(site_info, request_path)
    scheme = scheme.replace('http', url_type)
    return mark_safe(
        urlunparse([scheme, host, path, None, None, None])
    )

@register.filter(is_safe=True)
def xml_display_url(request_path, site_info):
    '''Construct the url that will display the xml document tree in a browser'''

    scheme, host, path = _expand_url_dict(site_info, request_path)

    # 'view' is the path registered in the app's urls.py that will
    # cause the content-type header to be set to application/xml
    path = os_path.join(path, 'view')

    return mark_safe(
        urlunparse([scheme, host, path, None, None, None])
    )
