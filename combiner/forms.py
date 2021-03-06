from django import forms

from .models import InputDocument, CKANResource, CKANField
from django.forms import formset_factory

class DocumentForm(forms.Form):
    csv_file = forms.FileField(label='Select a file',
                               widget=forms.FileInput(attrs={'class':'show-for-sr'}))
    x_field = forms.CharField()
    y_field = forms.CharField()

class MetadataForm(forms.Form):
    geo_field = forms.CharField(
        max_length=200,
    label="Field with geo data (e.g. Lat/Lon): ")



class CombinationForm(forms.Form):
    field = forms.ModelChoiceField(queryset=CKANField.objects.all().order_by('name'), label='Pick a field')
    radius = forms.FloatField()

