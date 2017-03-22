#!/usr/bin/env python
#-*- coding: utf-8 -*-

from django import forms
from django.contrib.admin import widgets
import datetime
from EasyOps.models import *
from pyexpat import model



    
class EditTaskWatchdogForm(forms.ModelForm):
    '''
    编辑配置监控命令
    '''
    class Meta:
        model = WdTaskInfo
        fields = ('task','task_info','mail_recv','operator','del_flag')
    
    task = forms.CharField(
                           label = u'任务',
                           required = True,
                           widget=forms.Textarea(attrs={'class':'form-control'}),
                           max_length=200,               
                           )
    
    task_info = forms.CharField(
                           label = u'说明',
                           required = True,
                           widget=forms.Textarea(attrs={'class':'form-control'}),
                           max_length=200,                   
                           )
    mail_recv = forms.CharField(
                           label = u'告警人(um账号)',
                           required = True,
                           widget=forms.Textarea(attrs={'class':'form-control'}),
                           error_messages = {'required':u'请输入告警接收人（um账号，逗号分隔）'},
                           max_length=200,                   
                           )
    del_flag = forms.CharField()
    operator = forms.CharField()
    
    
class AddTaskWatchdogForm(forms.ModelForm):
    '''
    编辑配置监控命令
    '''
    class Meta:
        model = WdTaskInfo
        fields = ('task','task_info','task_interval','mail_recv','operator','del_flag')
    
    task = forms.CharField(
                           label = u'任务',
                           required = True,
                           widget=forms.Textarea(attrs={'class':'form-control'}),
                           max_length=200,               
                           )
    
    task_info = forms.CharField(
                           label = u'说明',
                           required = True,
                           widget=forms.Textarea(attrs={'class':'form-control'}),
                           max_length=200,                   
                           )
    mail_recv = forms.CharField(
                           label = u'告警人(um账号)',
                           required = True,
                           widget=forms.Textarea(attrs={'class':'form-control'}),
                           error_messages = {'required':u'请输入告警接收人（um账号，逗号分隔）'},
                           max_length=200,                   
                           )
    task_interval = forms.CharField()
    del_flag = forms.CharField()
    operator = forms.CharField()
    
    
class AddAtomTaskWatchdogForm(forms.ModelForm):
    '''
    新增原子命令
    '''
    class Meta:
        model = WdAtomTaskInfo
        fields = ('task','task_info','task_interval','operator','del_flag')
        
    task = forms.CharField(
                           label = u'任务',
                           required = True,
                           widget=forms.Textarea(attrs={'class':'form-control'}),
                           max_length=200,               
                           )
    
    task_info = forms.CharField(
                           label = u'说明',
                           required = True,
                           widget=forms.Textarea(attrs={'class':'form-control'}),
                           max_length=200,                   
                           )
    task_interval = forms.CharField()
    del_flag = forms.CharField()
    operator = forms.CharField()
        
        
    
   