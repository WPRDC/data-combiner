from wsgiref.util import FileWrapper

import os
import io
import csv

import shapely
from shapely.geometry.point import Point

WGS84 = "EPSG:4326"
PA_SP_SOUTH = "EPSG:102729"


from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.utils.encoding import smart_str
from django.contrib import messages

from data_combiner import settings

from .models import InputDocument
from .forms import DocumentForm, CKANDatasetForm, CKANFieldForm


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
    data = None  # get_csv_data(dl_doc.file.path, 10)

    # Generate and handle form
    form = CKANFieldForm()
    if request.method == "POST":
        form = CKANDatasetForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse("combiner:results"))

    errors = form.errors or None

    return render(
        request,
        'combiner/options.html',
        {'form': form,
         'table_data': data,
         'file_name': file_name}
    )


def join_data(request):
    if request.method == "POST":
        print("HEY")
        pass
    else:
        messages.error(request, 'Error Merging Files')

    return HttpResponseRedirect(reverse("combiner:options"))


def results(request):
    return render(
        request,
        'combiner/results.html',
        {

        }
    )


def ConcentricCircle(x, y, radius, projection=PA_SP_SOUTH):
    p = Point(x, y)
    circle = p.buffer(1)
