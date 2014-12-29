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
        queryset=Option.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False)

    new_option = forms.CharField(max_length=50,
                                 required=False)


class PrinterListForm(forms.ModelForm):

    class Meta:
        model = PrinterList
        exclude = ()

    printers = forms.ModelMultipleChoiceField(
        label='Included Printers',
        queryset=Printer.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
        )

    public = forms.Select()


class SubscriptionPrinterListForm(forms.ModelForm):

    class Meta:
        model = SubscriptionPrinterList
        exclude = ()

    printers = forms.ModelMultipleChoiceField(
        queryset=Printer.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False)

    subnet = forms.CharField(
        max_length=50,
        required=False,
        validators = [validate_subnet],
        )
