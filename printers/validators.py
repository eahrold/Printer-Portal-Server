'''Validators'''
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from printers.models import Printer
from netaddr import IPNetwork, AddrFormatError

def validate_protocol(value):
    '''Check that the printer uri is a supported type'''
    is_supported = False

    '''supported_protocols retuns an array of
    tuples e.g. (protocol, description)'''

    for protocol in Printer.supported_protocols:
        if protocol[0] == value:
            is_supported = True
            break

    if not is_supported:
        raise ValidationError(
            u'protocol %s is not currently supported' %
            value)

def validate_printer_name(value):
    '''Check that the printer name is safe'''
    if " " in value:
        raise ValidationError(u'printer name can not contain spaces')
    if value[0].isdigit():
        raise ValidationError(u'printer name must start with letter')


def validate_server_address(value):
    '''check that the url is formatted somewhat reasonably'''

    validate = URLValidator(verify_exists=False)
    validate(value)

def validate_subnet(value):
    try:
        IPNetwork(value)
    except AddrFormatError as e:
        raise ValidationError(u'The subnet address is not correctly formatted.')
