# !/usr/bin/env python
# encoding: utf-8
"""
:copyright (c) 2014 - 2017, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Department of Energy) and contributors. All rights reserved.  # NOQA
:author
"""
from django.conf import settings
from django.conf.urls import include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.static import serve

from config.views import robots_txt
from seed.api.base.urls import urlpatterns as api
from seed.views.main import angular_js_tests

urlpatterns = [
    # Application
    url(r'^', include('seed.landing.urls', namespace="landing", app_name="landing")),
    url(r'^audit_logs/',
        include('seed.audit_logs.urls', namespace="audit_logs", app_name="audit_logs")),
    url(r'^app/', include('seed.urls', namespace="seed", app_name="seed")),

    # root configuration items
    url(r'^eula/', include('tos.urls', namespace='tos', app_name='tos')),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^robots\.txt', robots_txt, name='robots_txt'),

    # API
    url(r'^api/swagger/', include('rest_framework_swagger.urls'), name='swagger'),
    url(r'^api/', include(api, namespace='api')),
]

# TODO: 8/8/17 fix media root for docker deployments. Need to have uploads live somewhere other than the compiled assets
if settings.DEBUG:
    from django.contrib import admin

    admin.autodiscover()
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += [
        # test URLs
        url(r'^angular_js_tests/$', angular_js_tests, name='angular_js_tests'),

        # admin
        url(r'^admin/', include(admin.site.urls)),
        url(
            r'^media/(?P<path>.*)$',
            serve,
            {
                'document_root': settings.MEDIA_ROOT,
            }
        ),
    ]
