from django import forms

from .models import InputDocument, CKANResource, CKANField
from django.forms import formset_factory

class DocumentForm(forms.Form):
    csv_file = forms.FileField(label='Select a file',
                               widget=forms.FileInput(attrs={'class':'show-for-sr'}))


class MetadataForm(forms.Form):
    geo_field = forms.CharField(
        max_length=200,
    label="Field with geo data (e.g. Lat/Lon): ")


class CombinationForm(forms.Form):
    resource = forms.ModelChoiceField(queryset=CKANResource.objects.all().order_by('name'), label='Select a Dataset')
    field = forms.ModelChoiceField(queryset=CKANField.objects.all(), label='Pick a field')
    radius = forms.FloatField()

class GeoHeadingForm(forms.Form):
    x_field = forms.ChoiceField(choices=[])
    y_field = forms.ChoiceField(choices=[])

    def __init__(self, *args, **kwargs):
        headings = kwargs.pop('headings', None)
        super(GeoHeadingForm, self).__init__(*args, **kwargs)
        if headings:
            self.fields['x_field'].choices = headings
            self.fields['y_field'].choices = headings