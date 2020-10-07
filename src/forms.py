from .models import Audio
from django import forms


class Importdataform(forms.ModelForm):
    class Meta:
        model = Audio
        fields = ('document',)
