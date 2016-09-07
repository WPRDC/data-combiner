import csv
import pyproj

from celery import Celery

from shapely.geometry.point import Point

from .ckan import get_ckan_data, get_ckan_info

from data_combiner.settings import BROKER_URL

from combiner.models import InputDocument, CKANField, CKANResource, CKANInstance

app = Celery('tasks', broker=BROKER_URL)

# Projections
WGS84 = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'
PA_SP_SOUTH = '+proj=lcc +lat_1=39.93333333333333 +lat_2=40.96666666666667 +lat_0=39.33333333333334 +lon_0=-77.75 +x_0=600000.0000000001 +y_0=0 +ellps=GRS80 +datum=NAD83 +to_meter=0.3048006096012192 +no_defs'

# Conversions
MILES = 5280


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
