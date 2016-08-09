from django.contrib import admin

from .models import CKANInstance, CKANResource, InputDocument, CKANField

admin.site.register(CKANInstance)
admin.site.register(CKANResource)
admin.site.register(InputDocument)
admin.site.register(CKANField)