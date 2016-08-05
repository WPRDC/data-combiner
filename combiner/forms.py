from django import forms

from .models import InputDocument, CKANResource, CKANIntField, CKANStringField

class DocumentForm(forms.Form):
    csv_file = forms.FileField(
        label='Select a file'
    )

class MetadataForm(forms.Form):
    geo_field = forms.CharField(
        max_length=200,
    label="Field with geo data (e.g. Lat/Lon): ")

class CKANDatasetForm(forms.Form):
    dataset = forms.ModelChoiceField(queryset=CKANResource.objects.all().order_by('name'))

class CKANFieldForm(forms.Form):
    int_field = forms.ModelChoiceField(queryset=CKANIntField.objects.all().order_by('name'), label='Pick a number field')
    string_field = forms.ModelChoiceField(queryset=CKANStringField.objects.all().order_by('name'), label='Pick a string field')