from django.conf.urls import url
from .views import index, upload, options, results, progress, poll_state, get_fields, update_geo_fields

app_name = 'combiner'

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^upload/$', upload, name='upload'),
    url(r'^options/$', options, name='options'),
    url(r'^results/$', results, name='results'),
    url(r'^progress/$', progress, name='progress'),
    url(r'^poll_state/$', poll_state, name='poll_state'),
    url(r'^fields/$', get_fields, name='get_fields'),
    url(r'^update_geo_fields/$', update_geo_fields, name='update_geo_fields')
]
