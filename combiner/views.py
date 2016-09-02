import os
import csv
import json


from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.forms import formset_factory

from data_combiner import settings

from .models import InputDocument, CKANField, CKANResource, CKANInstance
from .forms import DocumentForm, CombinationForm, GeoHeadingForm

from .utils.csv import parse_csv, get_csv_data
from .tasks import combine_data

#from .utils.combine import combine_data

def index(request):
    form = DocumentForm()  # A empty, unbound form

    return render(
        request,
        'combiner/index.html',
        {'form': form}
    )


def upload(request):
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)

        if form.is_valid():
            # Get metadata from csv file as well as store
            file = request.FILES['csv_file']
            id = parse_csv(file)
            if id:
                request.session['file_id'] = str(id)
                return HttpResponseRedirect(reverse("combiner:options"))

    messages.warning(request, 'Please upload a file')
    return HttpResponseRedirect(reverse("combiner:index"))


def options(request):
    # get file information from session
    try:
        file_id = request.session['file_id']
        dl_doc = InputDocument.objects.get(pk=file_id)
        file_name = os.path.split(dl_doc.file.path)[1]
        headings = tuple(InputDocument.objects.get(pk=file_id).headings.split(','))
        headings = list(zip(headings, headings))
    except:
        messages.error(request, 'Error Uploading File')
        return HttpResponseRedirect(reverse("combiner:index"))

    try:
        job_id = request.GET['job']
    except:
        job_id = None
    FieldFormSet = formset_factory(CombinationForm, extra=1, max_num=5)

    if request.method == "POST":
        heading_form = GeoHeadingForm(request.POST, headings=headings)
        formset = FieldFormSet(request.POST)
        if formset.is_valid() and heading_form.is_valid():
            input_file_id = request.session['file_id']
            formset_data = formset.cleaned_data

            input_file = InputDocument.objects.get(pk=input_file_id)
            input_file.x_field = request.POST['x_field']
            input_file.y_field = request.POST['y_field']
            input_file.save()

            ckan_field_ids, radii = [], []
            for item in formset_data:
                ckan_field_ids.append(item['field'].id)
                radii.append(item['radius'])

            combiner = combine_data.delay(input_file_id, ckan_field_ids, radii, 'len')
            return HttpResponseRedirect(reverse("combiner:options") + "?job=" + combiner.id)

    # Build Forms
    heading_form = GeoHeadingForm(headings=headings)
    formset = FieldFormSet()

    errors = formset.errors or None

    # get first 10 rows from uploaded file
    data = get_csv_data(dl_doc.file.path, 10)

    return render(
        request,
        'combiner/options.html',
        {'heading_form': heading_form,
         'formset': formset,
         'table_data': data,
         'job_id': job_id,
         'file_name': file_name}
    )

def poll_state(request):
    """ A view to report the progress to the user """
    if request.is_ajax() and 'job' in request.GET:
        job_id = request.GET['job']
    else:
        return HttpResponse('No job id given.')

    job = combine_data.AsyncResult(job_id)
    data = job.result or job.state
    return HttpResponse(json.dumps(data))


def results(request):
    input_file_id = request.session['file_id']
    new_file = os.path.join(settings.MEDIA_ROOT, input_file_id + ".csv")
    new_table = get_csv_data(new_file, 50)

    return render(
        request,
        'combiner/results.html',
        {
            "table_data": new_table
        }
    )
