from wsgiref.util import FileWrapper

import os
import io
import csv
import json
import requests

import shapely
from shapely.geometry.point import Point
import pyproj

# Projections
WGS84 = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'
PA_SP_SOUTH = '+proj=lcc +lat_1=39.93333333333333 +lat_2=40.96666666666667 +lat_0=39.33333333333334 +lon_0=-77.75 +x_0=600000.0000000001 +y_0=0 +ellps=GRS80 +datum=NAD83 +to_meter=0.3048006096012192 +no_defs'

# Conversions
MILES = 5280

from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.utils.encoding import smart_str
from django.contrib import messages
from django.forms import formset_factory

from data_combiner import settings

from .models import InputDocument, CKANField, CKANResource, CKANInstance
from .forms import DocumentForm, CombinationForm, GeoHeadingForm


def parse_csv(file, encoding='utf-8'):
    _file = io.StringIO(file.read().decode(encoding))
    try:
        dr = csv.DictReader(_file)
        rows = 0
        for row in dr:
            rows += 1

        newdoc = InputDocument(file=file,
                               headings=",".join(dr.fieldnames),
                               rows=rows)
        newdoc.save()
        return newdoc.id

    except csv.Error:
        return False


def get_ckan_info(ckan_field):
    ckan_resource = ckan_field.ckan_resource
    ckan_instance = ckan_resource.ckan_instance
    return ckan_resource, ckan_instance


def get_ckan_data(ckan_field):
    ckan_resource, ckan_instance = get_ckan_info(ckan_field)

    url = ckan_instance.url + "/api/action/datastore_search"
    params = {'resource_id': ckan_resource.resource_id}

    response = requests.request("GET", url, params=params)

    return (json.loads(response.text)['result']['records'])


def apply_measure(rows, measure):
    return measure(rows)


def count(items):
    return len(items)


def contains(x1, y1, x2, y2, radius, origin1=WGS84, origin2=WGS84, destination=PA_SP_SOUTH):
    '''
    :param x: x coordinate or longitude
    :param y: y coordiante or latitude
    :param radius: radius in miles
    :param projection:
    :return:
    '''
    # project input x1,y1 to PA state plane
    try:
        x, y = pyproj.transform(pyproj.Proj(origin1),
                                pyproj.Proj(destination, preserve_units=True),
                                x1, y1)
        # get circle from first input
        p = Point(x, y)
        circle = p.buffer(radius * MILES)

        # project x2, y2 to same plane
        x, y = pyproj.transform(pyproj.Proj(origin2),
                                pyproj.Proj(destination, preserve_units=True),
                                x2, y2)
        p = Point(x, y)
        return circle.contains(p)
    except:
        return False


def combine_data(input_file_id, ckan_fields, radii, measure, input_projection=WGS84):
    input_file = InputDocument.objects.get(pk=input_file_id)

    result = []
    with open(input_file.file.path) as f:
        input_rows = list(csv.DictReader(f))
        for i in range(len(ckan_fields)):
            ckan_field = ckan_fields[i]
            ckan_resource, ckan_instance = get_ckan_info(ckan_field)
            ckan_data = get_ckan_data(ckan_field)

            for row in input_rows:
                matched_pts = []
                x1, y1 = row[input_file.x_field], row[input_file.y_field]

                for ckan_row in ckan_data:
                    x2, y2 = ckan_row[ckan_resource.lon_heading], ckan_row[ckan_resource.lat_heading]
                    if contains(x1, y1, x2, y2, radii[i]):
                        matched_pts.append(ckan_row)

                row[ckan_field.name + "_" + measure.__name__ + "_" + str(radii[i])] = apply_measure(matched_pts,
                                                                                                    measure)

            print(input_rows)
    result = input_rows
    print(result)
    return (result)


def get_csv_data(file_path, row_limit=0):
    n = 1
    data = []
    with open(file_path) as f:
        reader = csv.reader(f)
        for row in reader:
            data.append([str(c) for c in row])
            if n == row_limit + 1:  # the extra 1 is for the header
                break
            n += 1

    return data


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
    except:
        messages.error(request, 'Error Uploading File')
        return HttpResponseRedirect(reverse("combiner:index"))

    # get first 10 rows from uploaded file
    data = get_csv_data(dl_doc.file.path, 10)
    headings = tuple(InputDocument.objects.get(pk=file_id).headings.split(','))
    # Generate and handle forms
    heading_form = GeoHeadingForm(headings)

    FieldFormSet = formset_factory(CombinationForm, extra=1, max_num=5)
    if request.method == "POST":
        formset = FieldFormSet(request.POST, request.FILES)
        if formset.is_valid():
            input_file_id = request.session['file_id']
            formset_data = formset.cleaned_data
            ckan_fields, radii = [], []
            for item in formset_data:
                ckan_fields.append(item['field'])
                radii.append(item['radius'])

            new_table = combine_data(input_file_id, ckan_fields, radii, count)
            new_file = os.path.join(settings.MEDIA_ROOT, input_file_id + ".csv")
            with open(new_file, 'w') as f:
                writer = csv.DictWriter(f, fieldnames=new_table[0].keys())
                writer.writeheader()
                writer.writerows(new_table)
            return HttpResponseRedirect(reverse("combiner:results"))

    formset = FieldFormSet()
    errors = formset.errors or None

    return render(
        request,
        'combiner/options.html',
        {'heading_form': heading_form,
         'formset': formset,
         'table_data': data,
         'file_name': file_name}
    )


def join_data(request):
    if request.method == "POST":
        form = CombinationForm(request.POST)
        if form.is_valid():
            ckan_field_id = request.POST['field']
            input_file_id = request.session['file_id']
            radius = request.POST['radius']

            new_table = combine_data(input_file_id, ckan_field_id, radius, count)
            new_file = os.path.join(settings.MEDIA_ROOT, input_file_id + ".csv")
            with open(new_file, 'w') as f:
                writer = csv.DictWriter(f, fieldnames=new_table[0].keys())
                writer.writeheader()
                writer.writerows(new_table)

            return HttpResponseRedirect(reverse("combiner:results"))
    else:
        messages.error(request, 'Error Merging Files')

    return HttpResponseRedirect(reverse("combiner:options"))


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
