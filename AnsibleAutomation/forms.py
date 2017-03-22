#!/usr/bin/env python
#-*- coding: utf-8 -*-

'''
AnsibleAutomation
20160809
'''

from django import forms
from django.contrib.admin import widgets
import datetime
from EasyOps.models import *
from pyexpat import model


#上传文件表单
class DocumentForm(forms.Form):
    docfile = forms.FileField(
        label='Select a file',
        help_text='max. 42 megabytes'
    )
    
class AddFileForm(forms.Form):
    filename = forms.FileField(
        label='选择文件',
        help_text='max. 42 megabytes'
    )