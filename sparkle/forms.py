from django import forms
from django.forms import ModelForm, Select
from models import *
from validators import *


class AppcastForm(forms.ModelForm):
    fields = '__all__'

    class Meta:
        model = Version

    application = forms.ModelChoiceField(
        widget=forms.HiddenInput(),
        queryset=Application.objects.all())


class PrivateKeyForm(forms.ModelForm):
    fields = '__all__'

    class Meta:
        model = PrivateKey

    private_key = forms.FileField(label='Private Key', required=True)

    def clean(self):
        cleaned_data = super(PrivateKeyForm, self).clean()
        validate_private_key(cleaned_data.get('private_key'))
        return cleaned_data
