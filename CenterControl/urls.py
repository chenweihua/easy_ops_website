#-*- coding: utf-8 -*-

'''
CenterControl
20170316
'''

from django.conf.urls import patterns, include, url

urlpatterns = patterns('CenterControl.views',
    url(r'^framework_health/$','frameworkHealth',name='framework_health_url'),
    url(r'^framework_health_get_data/$','frameworkHealthGetData',name='framework_health_get_data_url'),
)