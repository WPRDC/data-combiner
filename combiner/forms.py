from django import forms

from .models import InputDocument

class DocumentForm(forms.Form):
    csv_file = forms.FileField(
        label='Select a file: '
    )

class MetadataForm(forms.Form):
    geo_field = forms.CharField(
        max_length=200,
    label="Field with geo data (e.g. Lat/Lon): ")