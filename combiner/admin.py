from django.contrib import admin

from .models import CKANInstance, CKANResource, InputDocument, CKANField, Measure

admin.site.register(CKANInstance)
admin.site.register(CKANResource)
admin.site.register(InputDocument)
admin.site.register(CKANField)
admin.site.register(Measure)