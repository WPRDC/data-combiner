import os
import csv
import json

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.forms import formset_factory

from data_combiner import settings

from .models import InputDocument, CKANField, CKANResource, CKANInstance, Measure
from .forms import DocumentForm, CombinationForm, GeoHeadingForm

from .utils.csv import parse_csv, get_csv_data
from .tasks import combine_data

from django.views.decorators.csrf import csrf_exempt


# from .utils.combine import combine_data

### PAGES ##############################################################################################################

def index(request):
    input_form = DocumentForm()  # File upload form
    FieldFormset = formset_factory(CombinationForm, extra=1, max_num=5)
    field_formset = FieldFormset()

    return render(
        request,
        'combiner/index.html',
        {'input_form': input_form,
         'field_formset': field_formset}
    )


def results(request):
    job = combine_data.AsyncResult(request.session['celery_job'])
    data = job.result
    input_file_id = request.session['file_id']
    new_file = os.path.join(settings.MEDIA_ROOT, input_file_id + ".csv")
    with open(new_file, 'w', newline="\n") as f:
        dw = csv.DictWriter(f, fieldnames=data[0].keys())
        dw.writeheader()
        for row in data:
            dw.writerow(row)

    new_table, headings = get_csv_data(new_file, 10)
    table = [headings]
    for row in new_table:
        table.append([row[h] for h in headings])

    return render(
        request,
        'combiner/results.html',
        {
            "table_data": table
        }
    )

### API ENDPOINTS #######################################################################################################

def upload(request):
    """
    Uploads file into media folder, and returns `file_id` and a small sample of the data uploaded.

    URL: /combine/upload/

    :param request: HttpRequest object
    :return: JsonResponse
    {
        status  : success/fail,
        file_id : internal id for uploaded file,
        sample  : an array of objects representing a sample of the data,
        fields  : ordered array of field names
    }
    """
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)

        if form.is_valid():
            # Get metadata from csv file as well and store it in /media/
            file = request.FILES['csv_file']
            file_id = parse_csv(file)
            uploaded_file = InputDocument.objects.get(pk=file_id)
            if file_id:
                request.session['file_id'] = str(file_id)
                sample, fields = get_csv_data(uploaded_file.file.path, 10)
                return JsonResponse({'status': 'success',
                                     'file_id': str(file_id),
                                     'sample': sample,
                                     'fields': fields}
                                    )

    return JsonResponse({'status': 'fail',
                         'file_id': None,
                         'sample': None,
                         'fields': None},
                        status=400)


def update_geo_fields(request):
    if request.method == 'POST':
        try:
            lat, lon = request.POST['lat'], request.POST['lon']
        except KeyError:
            # missing parameters
            return JsonResponse({'error': "missing parameters"}, status=400)

        # TODO: separate this from session
        file_id = request.session['file_id']
        doc = InputDocument.objects.get(pk=file_id)
        doc.x_field = lon
        doc.y_field = lat
        doc.save()
        return JsonResponse({'status': 'successfully update',
                             'x': lon, 'y': lat})

    else:
        return JsonResponse({'error': 'wrong request type - must be POST'}, status=400)


def submit_combination_job(request):
    if request.method == "POST":
        formset_data = []
        for k,v in request.POST.items():
            if "measure_val" in k:
                formset_data.append(v)

        input_file_id = request.session['file_id']

        # Parse fieldset data
        ckan_field_ids, radii, measures = [], [], []

        for item in formset_data:
            f_id = int(item.split('-')[1])
            ckan_field_ids.append(f_id)
            radii.append(5)
            m_id = int(item.split('-')[2])
            measures.append(Measure.objects.get(pk=m_id).function)


        # Start celery job to combine the data
        combiner = combine_data.delay(input_file_id, ckan_field_ids, radii, measures)
        return JsonResponse({'combiner_id': combiner.id})

    else:
        return JsonResponse({'error': 'invalid'}, status=400)


def progress(request):
    # Check if job is currently being run
    # if so, set job_id
    try:
        job_id = request.GET['job']
    except:
        job_id = None

    return render(
        request,
        'combiner/progress.html',
        {
            'job_id': job_id
        }
    )




def poll_state(request):
    """ A view to report the progress to the user """
    if request.is_ajax() and 'job' in request.GET:
        job_id = request.GET['job']

    else:
        return HttpResponse('No job id given.')
    request.session['celery_job'] = job_id
    job = combine_data.AsyncResult(job_id)

    if job.state == "PROGRESS":
        data = job.result
    elif job.state == "SUCCESS":
        data = {'process_percent': 100}
    else:
        data = {'process_percent': 1}

    return HttpResponse(json.dumps(data))


def get_resources(request):
    resp = []
    for resource in CKANResource.objects.all():
        resp.append(
            {'pk': resource.pk,
             'name': resource.name}
        )

    return JsonResponse({'resources': resp, 'count': len(resp)})

def get_fields(request):
    if 'resource' in request.GET:
        id = request.GET['resource']
    else:
        return HttpResponse('No resource id given.')

    # Get fields within that resource
    fields = CKANField.objects.filter(ckan_resource_id=id)
    resp = []
    for field in fields:
        resp.append({'pk': field.pk, 'name': field.name})
    result = {'fields': resp, 'count': len(resp)}
    return JsonResponse(result)

def get_measures(request):
    if 'field' in request.GET:
        id = request.GET['field']
    else:
        return JsonResponse({'error': 'invalid request'}, status=400)

    field = CKANField.objects.get(pk=id)
    datatype = field.data_type
    measures = Measure.objects.filter(data_type__contains=datatype)
    resp = []
    for measure in measures:
        resp.append({'pk': measure.pk, 'name':measure.name})

    return JsonResponse({'measures': resp, 'count': len(resp)})

