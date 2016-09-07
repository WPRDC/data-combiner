from django.conf.urls import url
from .views import index, upload, options, results, progress, poll_state

app_name = 'combiner'

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^upload/$', upload, name='upload'),
    url(r'^options/$', options, name='options'),
    url(r'^results/$', results, name='results'),
    url(r'^progress/$', progress, name='progress'),
    url(r'^poll_state/$', poll_state, name='poll_state')
]
