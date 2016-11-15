from django.conf.urls import url
from .views import index, upload, results, progress, poll_state, get_fields, update_geo_fields, submit_combination_job, get_resources, get_measures
app_name = 'combiner'

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^upload/$', upload, name='upload'),
    url(r'^results/$', results, name='results'),
    url(r'^progress/$', progress, name='progress'),
    url(r'^poll_state/$', poll_state, name='poll_state'),
    url(r'^fields/$', get_fields, name='get_fields'),
    url(r'^update_geo_fields/$', update_geo_fields, name='update_geo_fields'),
    url(r'^submit/$',submit_combination_job, name='submit_job'),
    url(r'^resources/$',get_resources, name='get_resources'),
    url(r'^measures/$', get_measures, name='get_measures')
]
