from django import forms
from django.forms import ModelForm, Select
from models import *
from validators import *


class AppcastForm(forms.ModelForm):
    fields = '__all__'

    class Meta:
        model = Version
        exclude = ()

    application = forms.ModelChoiceField(
        widget = forms.HiddenInput(),
        queryset = None)

    def __init__(self, *args, **kwargs):
        super(AppcastForm, self).__init__(*args, **kwargs)
        self.fields['application'].queryset = Application.objects.all()


class PrivateKeyForm(forms.ModelForm):
    fields = '__all__'

    class Meta:
        model = PrivateKey
        exclude = ()

    private_key = forms.FileField(label='Private Key', required=True)

    def clean(self):
        cleaned_data = super(PrivateKeyForm, self).clean()
        validate_private_key(cleaned_data.get('private_key'))
        return cleaned_data
