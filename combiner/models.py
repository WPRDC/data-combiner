from django.db import models
from django.utils import timezone
from . import measures

from data_combiner.settings import CKAN_ROOT
import uuid

POINT = 'PNT'
POLYGON = 'PLY'
GEO_CHOICES = ((POINT, 'Point'), (POLYGON, 'Polygon'))

# Type Choices
INTEGER = 'INT'
STRING = 'STR'
FLOAT = 'FLT'

TYPE_CHOICES = ((INTEGER, 'Integer'),
                (STRING, 'String'),
                (FLOAT, 'Float'))

# Generate list of measures
fns = []
measures = dir(measures)
for m in measures:
    if m[0] != '_':
        fns.append((m,m))

FN_CHOICES = tuple(fns)

def get_expiration():
    return timezone.now() + timezone.timedelta(minutes=20)


class InputDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to='uploads/%Y/%m/%d')
    headings = models.CharField(max_length=512)
    rows = models.IntegerField()
    expires = models.DateTimeField(default=get_expiration)
    x_field = models.CharField(max_length=50)
    y_field = models.CharField(max_length=50)
    geo_type = models.CharField(max_length=4, choices=GEO_CHOICES, default=POINT)

    def __str__(self):
        return str(self.id)

    class Meta():
        verbose_name = 'Input Document'


class CKANInstance(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField('url of ckan instance', default=CKAN_ROOT)
    api_key = models.UUIDField('ckan api key', default=None)

    def __str__(self):
        return self.name

    class Meta():
        verbose_name = 'CKAN Instance'


class CKANResource(models.Model):
    name = models.CharField(max_length=200)
    ckan_instance = models.ForeignKey(CKANInstance, on_delete=models.CASCADE)
    resource_id = models.UUIDField('resource id', default=None)
    added_date = models.DateTimeField('date added')
    lat_heading = models.CharField(max_length=30)
    lon_heading = models.CharField(max_length=30)
    geo_type = models.CharField(max_length=4, choices=GEO_CHOICES, default=POINT)

    def __str__(self):
        return self.name

    class Meta():
        verbose_name = 'CKAN Resource'


class CKANField(models.Model):
    name = models.CharField(max_length=200)
    heading = models.CharField(max_length=30)
    ckan_resource = models.ForeignKey(CKANResource, on_delete=models.CASCADE)
    data_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=INTEGER)

    def __str__(self):
        return self.name

    class Meta():
        verbose_name = 'CKAN Field'

class Measure(models.Model):
    name = models.CharField(max_length=200)
    function = models.CharField(max_length=200, choices=FN_CHOICES)
    data_type = models.CharField(max_length=30,default=INTEGER)
    def __str__(self):
        return self.name

    class Meta():
        verbose_name = 'Measure Function'
