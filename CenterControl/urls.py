#-*- coding: utf-8 -*-

'''
CenterControl
20170316
'''

from django.conf.urls import patterns, include, url

urlpatterns = patterns('CenterControl.views',
    url(r'^framework_health/$','frameworkHealth',name='framework_health_url'),
    url(r'^framework_health_get_data/$','frameworkHealthGetData',name='framework_health_get_data_url'),
    url(r'^framework_health_get_the_data/$','frameworkHealthGetTheData',name='framework_health_get_the_data_url'),
    url(r'^send_task/','sendTask',name='send_task_url'),
    url(r'^task_result/(?P<ID>\d+)/','taskResult',name='task_result_url'),
    url(r'^send_result/(?P<ID>\d+)/','taskResult',name='send_result_url'), #与task_result使用同一后端处理函数
    url(r'^get_task_result/(?P<ID>\d+)/','getTaskResult',name='get_task_result_url'),
    #上传文件
    url(r'^send_file/','sendFile',name='send_file_url'),
)