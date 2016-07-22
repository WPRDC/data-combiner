from django.db import models
from django.utils import timezone

from data_combiner.settings import CKAN_ROOT
import uuid


def get_expiration():
    return timezone.now() + timezone.timedelta(minutes=20)


class InputDocument(models.Model):
    POINT = 'PNT'
    POLYGON = 'PLY'
    GEO_CHOICES = ((POINT, 'Point'),(POLYGON, 'Polygon'))

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to='uploads/%Y/%m/%d')
    headings = models.CharField(max_length=512)
    rows = models.IntegerField()
    expires = models.DateTimeField(default=get_expiration)
    geo_field = models.CharField(max_length=50)
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
    ckan_instance = models.ForeignKey(CKANInstance, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    resource_id = models.UUIDField('resource id', default=None)
    added_date = models.DateTimeField('date added')

    def __str__(self):
        return self.name

    class Meta():
        verbose_name = 'CKAN Resource'
