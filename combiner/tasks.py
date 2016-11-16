from __future__ import absolute_import

import csv
import builtins

import sys

from .models import InputDocument, CKANField, CKANInstance, CKANResource
from .utils.ckan import get_ckan_info, get_ckan_data
from .utils.combine import contains

from . import measures as Measure

from data_combiner.celery import app
from celery import current_task

# Projections
WGS84 = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'
PA_SP_SOUTH = '+proj=lcc +lat_1=39.93333333333333 +lat_2=40.96666666666667 +lat_0=39.33333333333334 +lon_0=-77.75 +x_0=600000.0000000001 +y_0=0 +ellps=GRS80 +datum=NAD83 +to_meter=0.3048006096012192 +no_defs'

# Conversions
MILES = 5280


def update_progress(i, imax, j, jmax, k, kmax, length):
    process_percent = "{}/{}   {}/{}   {}/{}    [ckan-data length: {}".format(i, imax, j, jmax, k, kmax, length)

    current_task.update_state(state='PROGRESS', meta={'process_percent': process_percent})


@app.task
def combine_data(input_file_id, ckan_field_ids, radii, measures, input_projection=WGS84):

    input_file = InputDocument.objects.get(pk=input_file_id)
    field_count = len(ckan_field_ids)
    row_count = input_file.rows

    total_iterations = field_count * row_count
    counter = 0

    with open(input_file.file.path) as f:
        rows = []

        for row in csv.DictReader(f):
            rows.append(row)

        for i in range(field_count):
            ckan_field = CKANField.objects.get(pk=ckan_field_ids[i])
            ckan_resource, ckan_instance = get_ckan_info(ckan_field)
            ckan_data = get_ckan_data(ckan_field)
            print(measures)
            measure = getattr(Measure, measures[i])
            radius = radii[i]

            for j in range(row_count):
                row = rows[j]
                matched_pts = []
                x1, y1 = row[input_file.x_field], row[input_file.y_field]

                z = 0
                z_max = len(ckan_data)
                for ckan_row in ckan_data:
                    z += 1
                    x2, y2 = ckan_row[ckan_resource.lon_heading], ckan_row[ckan_resource.lat_heading]
                    if contains(x1, y1, x2, y2, radii[i]):
                        matched_pts.append(ckan_row)

                    if not (z % (z_max // 5)):
                        update_progress(i, field_count, j, row_count, z, z_max, len(ckan_data))

                counter += 1

                row[ckan_field.name + "_" + measure.__name__ + "_" + str(radius)] = measure(matched_pts)

    return (rows)
