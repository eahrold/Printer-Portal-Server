'''Forms For Printers app'''
from django import forms
from django.conf import settings

from models import Printer, Option, PrinterList, SubscriptionPrinterList
from validators import validate_printer_name, validate_protocol, validate_subnet


class OptionForm(forms.ModelForm):

    class Meta:
        model = Option
        exclude = ()

    option = forms.CharField(
        max_length=50,
        label='Option*',
        help_text='should conform to syntax from lpoptions -l')


class PrinterForm(forms.ModelForm):

    class Meta:
        model = Printer
        exclude = ()
        if not settings.SERVE_FILES:
            exclude = ('ppd_file',)

    name = forms.CharField(
        max_length=50,
        label='Priner Name*',
        validators=[validate_printer_name],
        help_text='CUPS compliant name, No spaces or CAPS, must start with letter')

    protocol = forms.ChoiceField(
        choices=Printer.supported_protocols,
        label='Protocol*',
        validators=[validate_protocol]
        )

    host = forms.CharField(
        max_length=50,
        label='Host*',
        help_text='(FQDN or IP Address of printer or server)')

    model = forms.CharField(
        max_length=50,
        label='Printer Model',
        help_text='(As Listed with lpinfo -m)',
        required=False)

    options = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple,
        required=False)

    new_option = forms.CharField(max_length=50,
                                 required=False)

    def __init__(self, *args, **kwargs):
        super(PrinterForm, self).__init__(*args, **kwargs)
        self.fields['options'].queryset = Option.objects.all()


class BasePrinterListForm(forms.ModelForm):
    printers = forms.ModelMultipleChoiceField(
        label='Included Printers',
        queryset=None,
        widget=forms.CheckboxSelectMultiple,
        required=False
        )

    def __init__(self, *args, **kwargs):
        super(BasePrinterListForm, self).__init__(*args, **kwargs)
        self.fields['printers'].queryset = Printer.objects.all()

class PrinterListForm(BasePrinterListForm):
    '''Form for a standard printer list'''

    class Meta:
        model = PrinterList
        exclude = ()

    public = forms.Select()

    def __init__(self, *args, **kwargs):
        super(PrinterListForm, self).__init__(*args, **kwargs)


class SubscriptionPrinterListForm(BasePrinterListForm):
    '''Form for a subscription printer list'''
    class Meta:
        model = SubscriptionPrinterList
        exclude = ()

    printers = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple,
        required=False)

    subnet = forms.CharField(
        max_length=50,
        required=False,
        validators = [validate_subnet],
        )

    def __init__(self, *args, **kwargs):
        super(SubscriptionPrinterListForm, self).__init__(*args, **kwargs)
