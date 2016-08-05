from django.conf.urls import url
from .views import index, upload, options, results, join_data

app_name = 'combiner'

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^upload/$', upload, name='upload'),
    url(r'^options/$', options, name='options'),
    url(r'^results/$', results, name='results'),
    url(r'^join/$', join_data, name='join')
]
