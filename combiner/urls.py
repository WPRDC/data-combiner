from django.conf.urls import url
from .views import index, upload, options

app_name = 'combiner'

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^upload/$', upload, name='upload'),
    url(r'^options/$', options, name='options')
]
