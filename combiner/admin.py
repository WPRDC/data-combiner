from django.contrib import admin

from .models import CKANInstance, CKANResource, InputDocument

admin.site.register(CKANInstance)
admin.site.register(CKANResource)
admin.site.register(InputDocument)