from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^login/$', 'django.contrib.auth.views.login', kwargs=dict(template_name='crashes/login.html'), name='login'),

    url(r'^$', 'crashes.views.index', name='index'),
    url(r'^crashes/new/', 'crashes.views.new_crash', name='crash_new'),
    url(r'^crashes/u/(?P<username>[A-Za-z0-9-_]+)/', 'crashes.views.crashes_by_user', name='crashes_by_user'),
    url(r'^crashes/u/(?P<username>[A-Za-z0-9-_]+)/(?P<crash_id>\d+)/', 'crashes.views.crash_by_user', name='crash_by_user'),
)

