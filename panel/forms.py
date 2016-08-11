from django import forms
from .models import *


class BrokerForm(forms.ModelForm):
    password = forms.CharField(label='密码', widget=forms.PasswordInput)

    class Meta:
        model = Broker
        exclude = []
