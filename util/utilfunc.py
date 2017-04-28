#-*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response,RequestContext
from django.contrib.auth.decorators import login_required
from django.db.models import Q,Count,F
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
from django.conf import settings

import os
import datetime
import time
import re
import json
import sys
import hashlib #MD5相关功能

import redis

from easy_ops_website.common.CommonPaginator import SelfPaginator

from utilmodels import *
from utilvar import *

import paramiko
import scp


def GetTimeDayStr_():
    '''
    获取日期，字符串格式
    '''
    iNow = datetime.datetime.now()
    return iNow.strftime('%Y-%m-%d')
    
def Log(sFile,sType,sMsg):
    '''
    打印日志 type【ERROR|INFO|DEBUG】
    '''
    
    #获取函数名和行号
    sLineNum = str(sys._getframe().f_back.f_lineno)
    sFnName = sys._getframe().f_back.f_code.co_name
    #print('%s,%s'%(str(),str(sys._getframe().f_back.f_code.co_name)))
    
    sFile = sFile + '_' + GetTimeDayStr() + '.log'
    sMsg = '[' + GetTimeNowStr() + '][' + sType + '][' + sFnName + '][' + sLineNum + ']' + sMsg + '\n'
    
    try:
        with open(gLogDir + sFile,'a+') as Fd:
            Fd.write(sMsg)
    except BaseException,e:
        print('Log Fn Error:'+str(e))   

def GetTimeDayStr():
    '''
    获取日期，字符串格式
    '''
    iNow = datetime.datetime.now()
    return iNow.strftime('%Y%m%d')
    
def GetTimeNowStr():
    '''
    获取当前时间，字符串格式
    '''
    iNow = datetime.datetime.now()
    return iNow.strftime('%Y-%m-%d %H:%M:%S')
    
    
def access_logging(Fn):
    '''
    记录访问日志
    '''
    def Warp(*args,**kw):
        (request,) = args
        
        sInfo = 'none'
        if request.method == 'GET':
            sInfo = str(json.dumps(request.GET))
        elif request.method == 'POST':
            #todo: 此处有问题。当推送文件时，不能获取到request.body。解决：将requests的参数放在post里。
            try:
                sInfo = str(json.dumps(request.body)) if len(request.POST) == 0 else str(json.dumps(request.POST))
            except BaseException,e:
                sInfo = str(e)
            # sInfo = str(json.dumps(request.POST))

        Obj = UtilAccessInfo(tab_date_time = GetTimeDayStr_(),
            username = request.user.username,
            method = request.method,
            url = request.path,
            remote_addr = request.META['REMOTE_ADDR'],
            info = sInfo
            )
        Obj.save()
        return Fn(*args,**kw)
    return Warp
    
def GetStrMd5(sStr):
    if sStr == '' or sStr is None:
        return 'none'

    m = hashlib.md5()
    m.update(sStr)
    return m.hexdigest()


def getFileMd5(sPath):
    try:
        m = hashlib.md5()
        with open(sPath,'rb') as Fd:
            while True:
                sData = Fd.read(128)
                if not sData:
                    break
                m.update(sData)
            return m.hexdigest()
    except BaseException,e:
        return ''


def myScp(sFileName):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname=settings.DST_HOST, port=22,
                    username=settings.DST_USR, password=settings.DST_PSW, timeout=1)
    except BaseException,e:
        return (False, str(e))

    Scp = scp.SCPClient(ssh.get_transport())
    try:
        Scp.put("%s%s"%(settings.SRC_WEB_DIR,sFileName)
                , '%s%s' % (settings.DST_NAS_DIR,sFileName))
    except BaseException, e:
        return (False, "deb 1 %s"%(str(e)))
    return (True, 'succ')

def JudgeIpFormat(sIp):
    rePattern = re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
    if not rePattern.match(sIp):
        return False
    return True
    
    
    
    
    