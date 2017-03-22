#!/usr/bin/env python
#-*- coding: utf-8 -*-
#update:2014-09-12 by liufeily@163.com

from django.core.urlresolvers import reverse
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response,RequestContext
from django.contrib.auth.decorators import login_required
from easy_ops_website.common.CommonPaginator import SelfPaginator
from UserManage.views.permission import PermissionVerify

from django.contrib import auth
from django.contrib.auth import get_user_model
from UserManage.forms import LoginUserForm,ChangePasswordForm,AddUserForm,EditUserForm

import json

from util.utilfunc import *
from util.utilvar import *
from util.utilmodels import *

def LoginUser(request):
    '''用户登录view'''
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')

    if request.method == 'GET' and request.GET.has_key('next'):
        next = request.GET['next']
    else:
        next = '/'

    if request.method == "POST":
        form = LoginUserForm(request, data=request.POST)
        if form.is_valid():
            auth.login(request, form.get_user())
            
            return HttpResponseRedirect(request.POST['next'])
    else:
        form = LoginUserForm(request)

    kwvars = {
        'request':request,
        'form':form,
        'next':next,
    }

    return render_to_response('UserManage/login.html',kwvars,RequestContext(request))

@login_required
def LogoutUser(request):
    auth.logout(request)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def ChangePassword(request):
    if request.method=='POST':
        form = ChangePasswordForm(user=request.user,data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('logouturl'))
    else:
        form = ChangePasswordForm(user=request.user)

    kwvars = {
        'form':form,
        'request':request,
    }

    return render_to_response('UserManage/password.change.html',kwvars,RequestContext(request))

@login_required
@PermissionVerify()
def ListUser(request):
    mList = get_user_model().objects.all().order_by('-last_login')

    #分页功能
    lst = SelfPaginator(request,mList, 20)

    kwvars = {
        'lPage':lst,
        'request':request,
    }

    return render_to_response('UserManage/user.list.html',kwvars,RequestContext(request))

@login_required
@PermissionVerify()
def AddUser(request):

    if request.method=='POST':
        form = AddUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])

            form.save()
            return HttpResponseRedirect(reverse('listuserurl'))
    else:
        form = AddUserForm()

    kwvars = {
        'form':form,
        'request':request,
    }

    return render_to_response('UserManage/user.add.html',kwvars,RequestContext(request))

@login_required
@PermissionVerify()
def EditUser(request,ID):
    user = get_user_model().objects.get(id = ID)

    if request.method=='POST':
        form = EditUserForm(request.POST,instance=user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('listuserurl'))
        return HttpResponseRedirect(reverse('listuserurl')) 
    else:
        form = EditUserForm(instance=user)
        kwvars = {
            'id':ID,
            'form':form,
            'request':request,
        }
        #return HttpResponse(form,content_type = 'text/html')    
        return render_to_response('UserManage/user.edit.html',kwvars,RequestContext(request))

@login_required
@PermissionVerify()
def DeleteUser(request,ID):
    if ID == '1':
        return HttpResponse(u'超级管理员不允许删除!!!')
    else:
        get_user_model().objects.filter(id = ID).delete()

    return HttpResponseRedirect(reverse('listuserurl'))

@login_required
@PermissionVerify()
def ResetPassword(request,ID):
    user = get_user_model().objects.get(id = ID)

    newpassword = get_user_model().objects.make_random_password(length=10,allowed_chars='abcdefghjklmnpqrstuvwxyABCDEFGHJKLMNPQRSTUVWXY3456789')
    print '====>ResetPassword:%s-->%s' %(user.username,newpassword)
    user.set_password(newpassword)
    user.save()

    kwvars = {
        'object':user,
        'newpassword':newpassword,
        'request':request,
    }

    return render_to_response('UserManage/password.reset.html',kwvars,RequestContext(request))
    
    
@login_required
@PermissionVerify()
def AccLog(request):
    kwvars = {
        'request':request,
    }
    return render_to_response('UserManage/user.acc_log.html',kwvars,RequestContext(request))

@login_required
@PermissionVerify()
def GetAccLog(request,Qwords):
    lDataRet = []
    if request.method == 'GET':
        if Qwords == 'empty_flag':
            lData = UtilAccessInfo.objects.values('insert_time','id','username','method','url','info','remote_addr').order_by('-id')[:200]
        else:            
            lData = UtilAccessInfo.objects.filter(
                    Q(username__contains = Qwords)
                    |Q(url__contains = Qwords)                    
                    |Q(info__contains = Qwords)
                    |Q(remote_addr__contains = Qwords)
                ).values('insert_time','id','username','method','url','info','remote_addr')
        
        for dKv in lData:
            lDataRet.append({
                'insert_time':dKv['insert_time'].strftime("%Y-%m-%d %H:%M:%S"),
                'id':dKv['id'],
                'username':dKv['username'],
                'method':dKv['method'],
                'url':dKv['url'],
                'info':dKv['info'],                    
                'remote_addr':dKv['remote_addr'],                    
            })        
    
    return HttpResponse(json.dumps(lDataRet),content_type = 'application/json')

