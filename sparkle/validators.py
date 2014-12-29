from django.core.exceptions import ValidationError

def supportedExtensions():
    return ('.pem', '.key')

def validate_private_key(filename):
    '''Check that the private key format is somewhat sane'''
    if filename is None:
        raise ValidationError(u'No file selected')

    if not filename.name.endswith(supportedExtensions()):
        raise ValidationError(
            u'The file must be one of the following file Types: %s' %
            (supportedExtensions(), ))

    contents = filename.readline().strip()
    if not contents == '-----BEGIN DSA PRIVATE KEY-----':
        raise ValidationError(
            u'%s is not a DSA private key file' %
            (filename,))
    else:
        return True

def validate_only_one_instance(obj):
    '''Make sure there is only instance of a given object'''
    model = obj.__class__
    if (model.objects.count() > 0 and
            obj.id != model.objects.get().id):
        raise ValidationError("Can only create 1 %s instance" % model.__name__)
