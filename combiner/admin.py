from django.contrib import admin

from .models import CKANInstance, CKANResource, InputDocument, CKANField, CKANIntField, CKANStringField

admin.site.register(CKANInstance)
admin.site.register(CKANResource)
admin.site.register(InputDocument)
admin.site.register(CKANIntField)
admin.site.register(CKANStringField)