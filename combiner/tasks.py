from __future__ import absolute_import

import csv
import builtins

import sys

from .models import InputDocument, CKANField, CKANInstance, CKANResource
from .utils.ckan import get_ckan_info, get_ckan_data
from .utils.combine import contains

from data_combiner.celery import app
from celery import current_task

# Projections
WGS84 = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'
PA_SP_SOUTH = '+proj=lcc +lat_1=39.93333333333333 +lat_2=40.96666666666667 +lat_0=39.33333333333334 +lon_0=-77.75 +x_0=600000.0000000001 +y_0=0 +ellps=GRS80 +datum=NAD83 +to_meter=0.3048006096012192 +no_defs'

# Conversions
MILES = 5280


def update_progress(total, i1, i2):
    current = i1 * i2
    process_percent = int((current/total) * 100)

    current_task.update_state(state='PROGRESS', meta={'process_percent': process_percent})


@app.task
def combine_data(input_file_id, ckan_field_ids, radii, measure, input_projection=WGS84):
    measure = getattr(builtins, measure)
    input_file = InputDocument.objects.get(pk=input_file_id)
    field_count = len(ckan_field_ids)
    row_count = input_file.rows

    total_iterations = field_count * row_count

    with open(input_file.file.path) as f:
        rows = []

        for row in csv.DictReader(f):
            rows.append(row)

        for i in range(field_count):
            ckan_field = CKANField.objects.get(pk=ckan_field_ids[i])
            ckan_resource, ckan_instance = get_ckan_info(ckan_field)
            ckan_data = get_ckan_data(ckan_field)

            for j in range(row_count):
                row = rows[j]
                matched_pts = []
                x1, y1 = row[input_file.x_field], row[input_file.y_field]

                for ckan_row in ckan_data:
                    x2, y2 = ckan_row[ckan_resource.lon_heading], ckan_row[ckan_resource.lat_heading]
                    if contains(x1, y1, x2, y2, radii[i]):
                        matched_pts.append(ckan_row)

                row[ckan_field.name + "_" + measure.__name__ + "_" + str(radii[i])] = measure(matched_pts)

                update_progress(total_iterations, i+1, j+2)

    return (rows)



