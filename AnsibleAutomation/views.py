#-*- coding: utf-8 -*-

'''
AnsibleAutomation
20160809
'''

from django.shortcuts import render
# Create your views here.

from util.utilfunc import *
from util.utilvar import *
from util.utilmodels import *

from AnsibleAutomation.models import *
from AnsibleAutomation.forms import *

from UserManage.views.permission import PermissionVerify
from UserManage.models import User

reload(sys)
sys.setdefaultencoding('utf-8')

#----------功能入口函数----------

@login_required
@access_logging
@PermissionVerify()
def MainPage(request):
    #主页面
    kwvars = {
        'request':request,
    }
    return render_to_response('AnsibleAutomation/main_page.html',kwvars,RequestContext(request))

    
@login_required
@access_logging
def UserGroupPage(request):
    #用户组管理页面
    kwvars = {
        'request':request,
    }
    return render_to_response('AnsibleAutomation/user_group_page.html',kwvars,RequestContext(request))
    
@login_required
@access_logging
def AtomTaskPage(request):
    #原子操作管理页面
    
    kwvars = {
        'request':request,
    }
    return render_to_response('AnsibleAutomation/atom_task_page.html',kwvars,RequestContext(request))
    
@login_required
@access_logging
def HostGroupPage(request):
    #主机组管理页面
    kwvars = {
        'request':request,
    }
    return render_to_response('AnsibleAutomation/host_group_page.html',kwvars,RequestContext(request))
    
@login_required
@access_logging
def PlaybookPage(request):
    #playbook管理页面
    kwvars = {
        'request':request,
    }
    return render_to_response('AnsibleAutomation/playbook_page.html',kwvars,RequestContext(request))
    
    
@login_required
@access_logging
def HostPage(request):
    #设备管理页面
    kwvars = {
        'request':request,
    }
    return render_to_response('AnsibleAutomation/host_page.html',kwvars,RequestContext(request))
    
    
@login_required
@access_logging
def FilePage(request):
    #上传文件管理页面
    kwvars = {
        'request':request,
    }
    return render_to_response('AnsibleAutomation/file_page.html',kwvars,RequestContext(request))
    
    
#----------内部公用函数----------
def _GetGroupIdFromSuperUser(sSuperUser):
    #根据用户名，获得其对应组ID
    iGroupId = AsbUserGroupInfo.objects.filter(superuser = sSuperUser).values('user_group_id')[0]['user_group_id']
    return str(iGroupId)

def _GetSuperUserFromGroupId(iGroupId):
    sSuperUser = AsbUserGroupInfo.objects.filter(user_group_id = iGroupId).values('superuser')[0]['superuser']
    return sSuperUser
    

def _GetUserGroup(sUserName):
    #根据用户名获取到其对应的组等信息，dict返回
    dData = {}
    #get user user_group_id
    lData = AsbUserGroupUserMap.objects.filter(username = sUserName).filter(del_flag = 0).values('username','user_group_id')
    for dKv in lData:        
        if dData.has_key(dKv['username']):            
            if not dData[dKv['username']].has_key(dKv['user_group_id']):
                dData[dKv['username']][dKv['user_group_id']] = {}
        else:
            dData[dKv['username']] = {}
            dData[dKv['username']][dKv['user_group_id']] = {}
            
    lData = AsbUserGroupInfo.objects.filter(superuser = sUserName).values('superuser','user_group_id')
    for dKv in lData:
        if dData.has_key(dKv['superuser']):
            if not dData[dKv['superuser']].has_key(dKv['user_group_id']):
                dData[dKv['superuser']][dKv['user_group_id']] = {}
        else:
            dData[dKv['superuser']] = {}
            dData[dKv['superuser']][dKv['user_group_id']] = {}
            
    #Log(gLogFile,'DEBUG',str(dData))
    return dData

def _JudgeUserInUserGroup(sUserName):
    iCnt = AsbUserGroupInfo.objects.filter(superuser = sUserName).count()
    return iCnt 

def _GetHostGroupHostCnt(iHostGroupId):
    iCnt = AsbHostGroupHostMap.objects.filter(host_group_id = iHostGroupId).count()
    return iCnt
    
    
#----------页面数据处理函数----------
'''
####################################
原子任务管理模块
####################################
'''
    
    
@login_required
@access_logging
def AddAtomTask(request):
    #新增原子操作
    try:
        sUserName = request.user.username
        if request.method == 'POST':    
            if _JudgeUserInUserGroup(sUserName) == 0:
                AsbUserGroupInfo(superuser = sUserName, statement = 'auto create,default user',del_flag = 0).save()
                
            iuser_group_id = AsbUserGroupInfo.objects.filter(superuser = sUserName).values('user_group_id')[0]['user_group_id']
            
            #Log(gLogFile,'DEBUG',str(request.POST))
            
            #在任务表中新增任务
            Obj = AsbAtomTaskInfo(
                atom_task = request.POST['atom_task'],
                statement = request.POST['statement'],
                del_flag = 0
            )
            Obj.save()
            iatom_task_id = Obj.atom_task_id
            
            #关联至user_group表
            AsbUserGroupAtomTaskMap(user_group_id = iuser_group_id,atom_task_id = iatom_task_id,del_flag = 0).save()
    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))
    
    return HttpResponse(json.dumps({'ret':0}),content_type = 'application/json')
    
    
@login_required
@access_logging
def EditAtomTask(request):
    #编辑原子操作
    try:
        if request.method == 'POST':
            sUserName = request.user.username
            sUserGroupId = _GetGroupIdFromSuperUser(sUserName)
            iEditFlag = 0
            
            if sUserGroupId == str(request.POST['user_group_id']):
                iEditFlag = 1
                
                AsbAtomTaskInfo.objects.filter(atom_task_id = request.POST['atom_task_id'])\
                    .update(atom_task = request.POST['atom_task'],statement = request.POST['statement'])            
            
    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))
    
    return HttpResponse(json.dumps({'ret':iEditFlag}),content_type = 'application/json')
        
        
@login_required
@access_logging
def DelAtomTask(request):
    #删除原子操作
    #需要判定是否有权限删除（只有原子操作的属主才可以删除）
    try:
        if request.method == 'POST':
            #获取用户的superuser组ID
            lData = AsbUserGroupInfo.objects.filter(superuser = request.user.username).values('user_group_id')
            
            #可以支持一个用户是多个group的superuser
            iDelFlag = 0
            for dKv in lData:
                if str(dKv['user_group_id']) == str(request.POST['user_group_id']):
                    iDelFlag = 1
                
            if iDelFlag == 1:
                AsbAtomTaskInfo.objects.filter(atom_task_id = request.POST['atom_task_id']).update(del_flag = 1)
            
    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))
        
    return HttpResponse(json.dumps({'ret':iDelFlag}),content_type = 'application/json')

@login_required
@access_logging
def RestoreDelAtomTask(request):
    #恢复已经删除的原子操作
    try:
        if request.method == 'POST':
            #获取用户的superuser组ID
            lData = AsbUserGroupInfo.objects.filter(superuser = request.user.username).values('user_group_id')
            
            #可以支持一个用户是多个group的superuser
            iRestoreFlag = 0
            for dKv in lData:
                if str(dKv['user_group_id']) == str(request.POST['user_group_id']):
                    iRestoreFlag = 1
                
            if iRestoreFlag == 1:
                AsbAtomTaskInfo.objects.filter(atom_task_id = request.POST['atom_task_id']).update(del_flag = 0)
            
    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))
        
    return HttpResponse(json.dumps({'ret':iRestoreFlag}),content_type = 'application/json')

    
@login_required
@access_logging
#def SearchAtomTask(request,SearchFlag,Qwords):
def GetAtomTaskData(request,SearchFlag,Qwords):
    try:
        lDataRet = []
        if request.method == "GET":
            sUserName = request.user.username
            dData = _GetUserGroup(sUserName)
            
            #get user_group_id atom_task_id
            lAtomTaskId = []
            lData = AsbUserGroupAtomTaskMap.objects.filter(user_group_id__in = dData[sUserName].keys())\
                .filter(del_flag = 0).values('user_group_id','atom_task_id')
            for dKv in lData:
                lAtomTaskId.append(dKv['atom_task_id'])
                if dData[sUserName].has_key(dKv['user_group_id']):
                    if not dData[sUserName][dKv['user_group_id']].has_key(dKv['atom_task_id']):
                        dData[sUserName][dKv['user_group_id']][dKv['atom_task_id']] = {}
                else:
                    dData[sUserName][dKv['user_group_id']] = {}
                    dData[sUserName][dKv['user_group_id']][dKv['atom_task_id']] = {}
            
            if SearchFlag == 'using':
                iDelFlag = 0
            elif SearchFlag == 'del':
                iDelFlag = 1
            
            #get atom_task_id atom_task
            if Qwords == 'empty_flag':
                lData = AsbAtomTaskInfo.objects.filter(atom_task_id__in = lAtomTaskId).filter(del_flag = iDelFlag)\
                .values('insert_time','atom_task_id','atom_task','statement')
            elif Qwords == 'cnt_flag':
                iCnt = AsbAtomTaskInfo.objects.filter(atom_task_id__in = lAtomTaskId).filter(del_flag = iDelFlag).count()
            else:
                #普通的search
                lData = AsbAtomTaskInfo.objects.filter(atom_task_id__in = lAtomTaskId).filter(del_flag = iDelFlag)\
                    .filter(atom_task__contains = Qwords)\
                    .values('insert_time','atom_task_id','atom_task','statement')
            
            #生产返回数据
            if Qwords == 'cnt_flag':
                lDataRet.append({'cnt':iCnt})
            else:
                #用于json格式生成
                dAtomTaskInfo = {}
                for dKv in lData:
                    dAtomTaskInfo[dKv['atom_task_id']] = {
                        'insert_time':dKv['insert_time'].strftime("%Y-%m-%d %H:%M:%S"),
                        'atom_task':dKv['atom_task'],
                        'statement':dKv['statement'],
                    }
                #Log(gLogFile,'DEBUG',str(dAtomTaskInfo))
                
                #生成json格式数据
                for user_group_id in dData[sUserName]:
                    for atom_task_id in dData[sUserName][user_group_id]:
                        if dAtomTaskInfo.has_key(atom_task_id):                    
                            lDataRet.append({
                                'username':_GetSuperUserFromGroupId(user_group_id),
                                'user_group_id':user_group_id,
                                'atom_task_id':atom_task_id,
                                'insert_time':dAtomTaskInfo[atom_task_id]['insert_time'],
                                'atom_task':dAtomTaskInfo[atom_task_id]['atom_task'],
                                'statement':dAtomTaskInfo[atom_task_id]['statement'],                       
                            })
            
    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))
    
    return HttpResponse(json.dumps(lDataRet),content_type = 'application/json')

   
'''
####################################
设备管理模块
####################################
'''
@login_required
@access_logging
def AddHost(request):
    try:
        sUserName = request.user.username
        if request.method == 'POST':
            if _JudgeUserInUserGroup(sUserName) == 0:
                AsbUserGroupInfo(superuser = sUserName, statement = 'auto create,default user',del_flag = 0).save()
            
            iuser_group_id = AsbUserGroupInfo.objects.filter(superuser = sUserName).values('user_group_id')[0]['user_group_id']
            
            #在主机表中新增主机信息
            Obj = AsbHostInfo(
                host = request.POST['host'],
                host_port = request.POST['host_port'],
                host_user = request.POST['host_user'],
                host_passwd = request.POST['host_passwd'],
                host_su_user = request.POST['host_su_user'],
                host_su_passwd = request.POST['host_su_passwd'],
                statement = request.POST['statement'],
                asb_agent = 'none',
                connect_flag = 0,
                del_flag = 0,
            )
            Obj.save()
            ihost_id = Obj.host_id
            
            Log(gLogFile,'DEBUG','user_id:%s,host_id:%s'%(str(iuser_group_id),str(ihost_id)))
            
            #关联至user_group表
            AsbUserGroupHostMap(
                user_group_id = iuser_group_id,
                host_id = ihost_id,
                del_flag = 0
            ).save()        
    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))
        
    return HttpResponse(json.dumps({'ret':0}),content_type = 'application/json')

@login_required
@access_logging
def EditHost(request):
    try:
        if request.method == 'POST':
            sUserName = request.user.username
            sUserGroupId = _GetGroupIdFromSuperUser(sUserName)
            iEditFlag = 0
            
            if sUserGroupId == str(request.POST['user_group_id']):
                iEditFlag = 1
        
                AsbHostInfo.objects.filter(host_id = request.POST['host_id'])\
                    .update(
                        host = request.POST['host'],
                        host_port = request.POST['host_port'],
                        host_user = request.POST['host_user'],
                        host_passwd = request.POST['host_passwd'],
                        host_su_user = request.POST['host_su_user'],
                        host_su_passwd = request.POST['host_su_passwd'],
                        statement = request.POST['statement'],
                    )
    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))
    return HttpResponse(json.dumps({'ret':iEditFlag}),content_type = 'application/json')
    
@login_required
@access_logging
def DelHost(request):
    try:
        if request.method == 'POST':
            #获取用户的superuser组ID
            lData = AsbUserGroupInfo.objects.filter(superuser = request.user.username).values('user_group_id')
            
            #可以支持一个用户是多个group的superuser
            iDelFlag = 0
            for dKv in lData:
                if str(dKv['user_group_id']) == str(request.POST['user_group_id']):
                    iDelFlag = 1
                
            if iDelFlag == 1:
                AsbHostInfo.objects.filter(host_id = request.POST['host_id']).update(del_flag = 1)
        
    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))
    return HttpResponse(json.dumps({'ret':iDelFlag}),content_type = 'application/json')


@login_required
@access_logging
def RestoreDelHost(request):
    #恢复已经删除的设备
    try:
        if request.method == 'POST':
            #获取用户的superuser组ID
            lData = AsbUserGroupInfo.objects.filter(superuser = request.user.username).values('user_group_id')
            
            #可以支持一个用户是多个group的superuser
            iRestoreFlag = 0
            for dKv in lData:
                if str(dKv['user_group_id']) == str(request.POST['user_group_id']):
                    iRestoreFlag = 1
                
            if iRestoreFlag == 1:
                AsbHostInfo.objects.filter(host_id = request.POST['host_id']).update(del_flag = 0)
            
    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))
        
    return HttpResponse(json.dumps({'ret':iRestoreFlag}),content_type = 'application/json')

    
@login_required
@access_logging
def GetHostData(request,SearchFlag,Qwords):
    #获取host数据，用于表格展示
    #
    #和search的功能合并（ 包含使用中、已删除数据的全量查询、部分查询操作、cnt操作 ）
    #
    '''
        map               map
    user -> user_group_id -> host_id -> host
    '''
    
    try:
        if request.method == 'GET':
            sUserName = request.user.username
            
            dData = _GetUserGroup(sUserName)
            lDataRet = []
            
            #step 1: get user_group_id host_id
            lHostId = []
            lData = AsbUserGroupHostMap.objects\
                .filter(user_group_id__in = dData[sUserName].keys())\
                .filter(del_flag = 0).values('user_group_id','host_id')

            for dKv in lData:
                lHostId.append(dKv['host_id'])
                if dData[sUserName].has_key(dKv['user_group_id']):
                    if not dData[sUserName][dKv['user_group_id']].has_key(dKv['host_id']):
                        dData[sUserName][dKv['user_group_id']][dKv['host_id']] = {}
                else:
                    dData[sUserName][dKv['user_group_id']] = {}
                    dData[sUserName][dKv['user_group_id']][dKv['host_id']] = {}
            Log(gLogFile,'DEBUG',str(dData))
            
            if SearchFlag == 'using':
                iDelFlag = 0
            elif SearchFlag == 'del':
                iDelFlag = 1
            
            #step 2:
            if Qwords == 'empty_flag':
                #全量查找
                lData = AsbHostInfo.objects.filter(host_id__in = lHostId).filter(del_flag = iDelFlag)\
                    .values('insert_time','host_id','host','host_port','host_user',\
                    'host_passwd','host_su_user','host_su_passwd','statement','asb_agent','connect_flag')
                
            elif Qwords == 'cnt_flag':
                #cnt查找
                iCnt = AsbHostInfo.objects.filter(host_id__in = lHostId).filter(del_flag = iDelFlag).count()
            else:
                #普通查找
                lData = AsbHostInfo.objects.filter(host_id__in = lHostId).filter(del_flag = iDelFlag)\
                    .filter(host__contains = Qwords)\
                    .values('insert_time','host_id','host','host_port','host_user',\
                    'host_passwd','host_su_user','host_su_passwd','statement','asb_agent','connect_flag')
    
            Log(gLogFile,'DEBUG',str(lData))
            
            #step 3: 生成json格式数据
            if Qwords == 'cnt_flag':
                lDataRet.append({'cnt':iCnt})
            else:
                #用于json格式生成
                dHostInfo = {}
                for dKv in lData:
                    dHostInfo[dKv['host_id']] = {
                        'insert_time':dKv['insert_time'].strftime("%Y-%m-%d %H:%M:%S"),
                        'host_id':dKv['host_id'],
                        'host':dKv['host'],
                        'host_port':dKv['host_port'],
                        'host_user':dKv['host_user'],
                        'host_passwd':dKv['host_passwd'],
                        'host_su_user':dKv['host_su_user'],
                        'host_su_passwd':dKv['host_su_passwd'],
                        'statement':dKv['statement'],
                        'asb_agent':dKv['asb_agent'],
                        'connect_flag':dKv['connect_flag'],
                    }
                Log(gLogFile,'DEBUG',str(dHostInfo))
            
                for user_group_id in dData[sUserName]:
                    for host_id in dData[sUserName][user_group_id]:
                        if dHostInfo.has_key(host_id):                    
                            lDataRet.append({
                                'username':_GetSuperUserFromGroupId(user_group_id),
                                'user_group_id':user_group_id,
                                'host_id':host_id,
                                'insert_time':dHostInfo[host_id]['insert_time'],                      
                                'host':dHostInfo[host_id]['host'],                      
                                'host_port':dHostInfo[host_id]['host_port'],                      
                                'host_user':dHostInfo[host_id]['host_user'],                      
                                'host_passwd':dHostInfo[host_id]['host_passwd'],                      
                                'host_su_user':dHostInfo[host_id]['host_su_user'],                      
                                'host_su_passwd':dHostInfo[host_id]['host_su_passwd'],                      
                                'statement':dHostInfo[host_id]['statement'],                      
                                'asb_agent':dHostInfo[host_id]['asb_agent'],                      
                                'connect_flag':dHostInfo[host_id]['connect_flag'],                      
                            })
        
    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))
    
    return HttpResponse(json.dumps(lDataRet),content_type = 'application/json')

    
'''
####################################
用户管理模块
####################################
'''

@login_required
@access_logging
def GetAddUserData(request):
    try:
        if request.method == 'GET':
            sUserName = request.user.username
            sUserGroupId = _GetGroupIdFromSuperUser(sUserName)
            #刨除已经在该用户组中的
            lData = User.objects\
                .exclude(username__in = AsbUserGroupUserMap.objects.filter(user_group_id = int(sUserGroupId)).values('username'))\
                .values('id','username')
    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))
    return HttpResponse(json.dumps(list(lData)),content_type = 'application/json')

def GetUserData(request,SearchFlag,Qwords):
    try:
        if request.method == 'GET':
            sUserName = request.user.username
            iUserGroupId = int(_GetGroupIdFromSuperUser(sUserName))
            lDataRet = []
            
            #search flag: using|del
            if SearchFlag == 'using':
                iDelFlag = 0
            elif SearchFlag == 'del':
                iDelFlag = 1
            
            #qword: empty_flag|cnt_flag 
            if Qwords == 'empty_flag':
                #全量查询
                lData = AsbUserGroupUserMap.objects.filter(user_group_id = iUserGroupId)\
                    .filter(del_flag = iDelFlag)\
                    .values('insert_time','map_id','username')
                
            elif Qwords == 'cnt_flag':
                #数量查询
                iCnt = AsbUserGroupUserMap.objects.filter(user_group_id = iUserGroupId)\
                    .filter(del_flag = iDelFlag).count()
            else:
                #检索查询
                lData = AsbUserGroupUserMap.objects.filter(user_group_id = iUserGroupId)\
                    .filter(del_flag = iDelFlag)\
                    .filter(username__contains = Qwords)\
                    .values('insert_time','map_id','username')
                    
            #生成json格式数据
            if Qwords == 'cnt_flag':
                lDataRet.append({'cnt':iCnt})
            else:
                for dKv in lData:
                    lDataRet.append({
                        'username':dKv['username'],
                        'map_id':dKv['map_id'],
                        'user_group_id':iUserGroupId,
                        'insert_time':dKv['insert_time'].strftime("%Y-%m-%d %H:%M:%S"),
                    })
                    
    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))
        
    return HttpResponse(json.dumps(lDataRet),content_type = 'application/json')

        
    
@login_required
@access_logging
def AddUser(request):
    try:
        if request.method == 'POST':
            sUserName = request.user.username
            
            luser_id = request.POST.getlist("luser_id[]") #接收ajax传递arr的方法
            Log(gLogFile,'DEBUG',str(luser_id))
            #get username
            lData = User.objects.filter(id__in = luser_id).values('username')
            Log(gLogFile,'DEBUG',str(lData))
            
            #get user_group_id
            iUserGroupId = AsbUserGroupInfo.objects.filter(superuser = sUserName).values('user_group_id')[0]['user_group_id']

            
            #添加进user_group_user_map表
            for dKv in lData:
                AsbUserGroupUserMap(
                    username = dKv['username'],
                    user_group_id = iUserGroupId,
                    del_flag = 0
                ).save()
    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))

    return HttpResponse(json.dumps({'ret':0}),content_type = 'application/json')
    

@login_required
@access_logging
def DelUser(request):
    try:
        if request.method == 'POST':
            sUserName = request.user.username
            sUserGroupId = _GetGroupIdFromSuperUser(sUserName)
        
            iDelFlag = 0
            if sUserGroupId == str(request.POST['user_group_id']):
                iDelFlag = 1
            
            if sUserName == request.POST['username']:
                iDelFlag = 2
            
            if iDelFlag == 1:
                AsbUserGroupUserMap.objects.filter(map_id = request.POST['map_id']).update(del_flag = 1)
    
    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))
    return HttpResponse(json.dumps({'ret':iDelFlag}),content_type = 'application/json')

@login_required
@access_logging
def RestoreDelUser(request):
    try:
        if request.method == 'POST':
            sUserName = request.user.username
            sUserGroupId = _GetGroupIdFromSuperUser(sUserName)
            Log(gLogFile,'DEBUG',sUserName)
            Log(gLogFile,'DEBUG',request.POST['username'])
            iRestoreFlag = 0
            if sUserGroupId == str(request.POST['user_group_id']):
                iRestoreFlag = 1
            
            if sUserName == request.POST['username']:
                iRestoreFlag = 2
            
            if iRestoreFlag == 1:
                AsbUserGroupUserMap.objects.filter(map_id = request.POST['map_id']).update(del_flag = 0)

    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))
    
    return HttpResponse(json.dumps({'ret':iRestoreFlag}),content_type = 'application/json')

    
'''
####################################
设备分组管理模块（暂时先不做）
####################################
'''
@login_required
@access_logging
def AddHostGroup(request):
    try:
        if request.method == 'POST':
            sUserName = request.user.username
            
            if _JudgeUserInUserGroup(sUserName) == 0:
                AsbUserGroupInfo(superuser = sUserName, statement = 'auto create,default user',del_flag = 0).save()
            
            iUserGroupId = AsbUserGroupInfo.objects.filter(superuser = sUserName).values('user_group_id')[0]['user_group_id']
            
            #在host_group表中新增组
            AsbHostGroupInfo(
                statement = request.POST['statement'],
                del_flag = 0
            ).save()
            
            iHostGroupId = (AsbHostGroupInfo.objects.filter(
                statement = request.POST['statement'],
            )).order_by('-host_group_id').values('host_group_id')[:1][0]['host_group_id']
            
            #关联至user_group表
            AsbUserGroupHostGroupMap(
                user_group_id = iUserGroupId,
                host_group_id = iHostGroupId,
                del_flag = 0,
            ).save()
            
    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))
    
    return HttpResponse(json.dumps({'ret':0}),content_type = 'application/json')
    
@login_required
@access_logging
def GetHostGroupData(request,SearchFlag,Qwords):
    try:
        if request.method == "GET":
            
            sUserName = request.user.username
            dData = _GetUserGroup(sUserName)
            lDataRet = []
            
            #get user_group_id host_group_id
            lData = AsbUserGroupHostGroupMap.objects\
                .filter(user_group_id__in = dData[sUserName].keys())\
                .filter(del_flag = 0).values('user_group_id','host_group_id')
            
            lHostGroupId = []
            for dKv in lData:
                lHostGroupId.append(dKv['host_group_id'])
                if dData[sUserName].has_key(dKv['user_group_id']):
                    if not dData[sUserName][dKv['user_group_id']].has_key(dKv['host_group_id']):
                        dData[sUserName][dKv['user_group_id']][dKv['host_group_id']] = {}
                else:
                    dData[sUserName][dKv['user_group_id']] = {}
                    dData[sUserName][dKv['user_group_id']][dKv['host_group_id']] = {}
            
            if SearchFlag == 'using':
                iDelFlag = 0
            elif SearchFlag == 'del':
                iDelFlag = 1
                
            #get host_group_id host_group
            if Qwords == 'empty_flag':
                lData = AsbHostGroupInfo.objects.filter(host_group_id__in = lHostGroupId)\
                    .filter(del_flag = iDelFlag)\
                    .values('insert_time','host_group_id','statement')
                    
            elif Qwords == 'cnt_flag':
                iCnt = AsbHostGroupInfo.objects.filter(host_group_id__in = lHostGroupId)\
                    .filter(del_flag = iDelFlag).count()
            else:
                lData = AsbHostGroupInfo.objects.filter(host_group_id__in = lHostGroupId)\
                    .filter(del_flag = iDelFlag).filter(statement__contains = Qwords)\
                    .values('insert_time','host_group_id','statement')
            
            #返回数据
            if Qwords == 'cnt_flag':
                lDataRet.append({'cnt':iCnt})
            else:
                dHostGroupInfo = {}
                for dKv in lData:
                    dHostGroupInfo[dKv['host_group_id']] = {
                        'insert_time': dKv['insert_time'].strftime("%Y-%m-%d %H:%M:%S"),
                        'statement': dKv['statement'],
                    }
                
                #生成json格式数据
                for user_group_id in dData[sUserName]:
                    for host_group_id in dData[sUserName][user_group_id]:
                        if dHostGroupInfo.has_key(host_group_id):
                            lDataRet.append({
                                'username':_GetSuperUserFromGroupId(user_group_id),
                                'user_group_id':user_group_id,
                                'host_group_id':host_group_id,
                                'insert_time':dHostGroupInfo[host_group_id]['insert_time'],
                                'statement':dHostGroupInfo[host_group_id]['statement'],
                                'host_cnt':_GetHostGroupHostCnt(host_group_id),
                            })
    
    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))
    
    return HttpResponse(json.dumps(lDataRet),content_type = 'application/json')
   

'''
####################################
playbook编排模块
####################################
'''

@login_required
@access_logging
def AddPlaybook(request):
    '''
    两种场景：
    1、新增保存；无playbook_id
    2、编辑更新；有playbook_id
    '''
    try:
        if request.method == 'POST':
            sUserName = request.user.username
            
            if _JudgeUserInUserGroup(sUserName) == 0:
                AsbUserGroupInfo(superuser = sUserName, 
                    statement = 'auto create,default user',del_flag = 0).save()
            
            iuser_group_id = AsbUserGroupInfo.objects\
                .filter(superuser = sUserName)\
                .values('user_group_id')[0]['user_group_id']
            
            sPlaybook = request.POST['json_data']
            sPlaybookId = request.POST['playbook_id']
            sPlaybookName = request.POST['playbook_name']
            sMd5 = GetStrMd5(request.POST['json_data'])
            Log(gLogFile,'DEBUG','%s %s %s %s'
                %(sPlaybook,sPlaybookId,sPlaybookName,sMd5))
            
            if sPlaybookId == 'none':
                #新增
                #在playbook表中新增            
                Obj = AsbPlaybookInfo(
                    playbook_info_json = sPlaybook,
                    playbook_info_yml = 'none',
                    statement = sPlaybookName,
                    playbook_md5_info = sMd5,
                    del_flag = 0,
                )
                Obj.save()
                
                iplaybook_id = Obj.playbook_id
                
                #关联至user_group表
                AsbUserGroupPlaybookMap(
                    user_group_id = iuser_group_id,
                    playbook_id = iplaybook_id,
                    del_flag = 0,
                    proc_flag = 1,
                    proc_type = 'step',
                ).save()
                return HttpResponse(json.dumps({'ret':0}),content_type = 'application/json')
            else:
                #编辑
                #判断是否有权限编辑
                sUserGroupId = _GetGroupIdFromSuperUser(sUserName)
                iEditFlag = 0
                if sUserGroupId == request.POST['user_group_id']:
                    iEditFlag = 1
                    AsbPlaybookInfo.objects.filter(playbook_id = str(request.POST['playbook_id']))\
                        .update(
                            playbook_info_json = sPlaybook,
                            statement = sPlaybookName,
                            playbook_md5_info = sMd5,
                        )
                return HttpResponse(json.dumps({'ret':iEditFlag}),content_type = 'application/json')            
    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))
    return HttpResponse(json.dumps({'ret':0}),content_type = 'application/json')


@login_required
@access_logging
def DelPlaybook(request):
    try:
        #获取用户的superuser组ID
        lData = AsbUserGroupInfo.objects.filter(superuser = request.user.username).values('user_group_id')
        
        #可以支持一个用户是多个group的superuser
        iDelFlag = 0
        for dKv in lData:
            if str(dKv['user_group_id']) == str(request.POST['user_group_id']):
                iDelFlag = 1
            
        if iDelFlag == 1:
            AsbPlaybookInfo.objects.filter(playbook_id = request.POST['playbook_id']).update(del_flag = 1)

    
    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))
    return HttpResponse(json.dumps({'ret':iDelFlag}),content_type = 'application/json')
    
@login_required
@access_logging
def RunPlaybook(request):
    try:
        AsbUserGroupPlaybookMap.objects.filter(map_id = request.POST['map_id'])\
            .update(proc_flag = 0,proc_type = request.POST['proc_type'])
    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))
    return HttpResponse(json.dumps({'ret':1}),content_type = 'application/json')
    
    
@login_required
@access_logging
def RunPlaybookByStep(request):
    try:
        AsbPbStepProcInfo.objects.filter(proc_id = request.POST['proc_id'])\
            .update(proc_flag = 0)
    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))
    return HttpResponse(json.dumps({'ret':1}),content_type = 'application/json')

    
@login_required
@access_logging
def RestoreDelPlaybook(request):
    try:
        if request.method == 'POST':
            #获取用户的superuser组ID
            lData = AsbUserGroupInfo.objects.filter(superuser = request.user.username).values('user_group_id')
            
            #可以支持一个用户是多个group的superuser
            iRestoreFlag = 0
            for dKv in lData:
                if str(dKv['user_group_id']) == str(request.POST['user_group_id']):
                    iRestoreFlag = 1
                
            if iRestoreFlag == 1:
                AsbPlaybookInfo.objects.filter(playbook_id = request.POST['playbook_id']).update(del_flag = 0)
            
    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))
        
    return HttpResponse(json.dumps({'ret':iRestoreFlag}),content_type = 'application/json')
    
    
@login_required
@access_logging
def GetPlaybookTableData(request,SearchFlag,Qwords):
    #获取playbook列表数据
    #
    #
    '''
        map               map
    user -> user_group_id -> playbook_id -> playbook
    '''
    try:
        if request.method == 'GET':
            sUserName = request.user.username
            
            dData = _GetUserGroup(sUserName)
            lDataRet = []
            
            #step 1: get user_group_id playbook_id
            lPlaybookId = []
            lData = AsbUserGroupPlaybookMap.objects\
                .filter(user_group_id__in = dData[sUserName].keys())\
                .filter(del_flag = 0).values('user_group_id','playbook_id'
                    ,'proc_type','proc_flag','map_id')
                
            for dKv in lData:
                lPlaybookId.append(dKv['playbook_id'])
                if dData[sUserName].has_key(dKv['user_group_id']):
                    if not dData[sUserName][dKv['user_group_id']].has_key(dKv['playbook_id']):
                        dData[sUserName][dKv['user_group_id']][dKv['playbook_id']] \
                            = {
                                'proc_type':dKv['proc_type'],
                                'proc_flag':dKv['proc_flag'],
                                'map_id':dKv['map_id'],
                            }
                else:
                    dData[sUserName][dKv['user_group_id']] = {}
                    dData[sUserName][dKv['user_group_id']][dKv['playbook_id']] \
                        = {
                            'proc_type':dKv['proc_type'],
                            'proc_flag':dKv['proc_flag'],
                            'map_id':dKv['map_id'],
                        }
            Log(gLogFile,'DEBUG',str(dData))
            
            if SearchFlag == 'using':
                iDelFlag = 0
            elif SearchFlag == 'del':
                iDelFlag = 1
            
            #step 2:
            if Qwords == 'empty_flag':
                #全量查找
                Log(gLogFile,'DEBUG',str(lPlaybookId))
                lData = AsbPlaybookInfo.objects.filter(playbook_id__in = lPlaybookId)\
                    .filter(del_flag = iDelFlag).values('insert_time','playbook_id','playbook_md5_info','statement')
            elif Qwords == 'cnt_flag':
                #cnt查找
                iCnt = AsbPlaybookInfo.objects.filter(playbook_id__in = lPlaybookId).count()
            else:
                #普通查找
                lData = AsbPlaybookInfo.objects.filter(playbook_id__in = lPlaybookId)\
                    .filter(del_flag = iDelFlag)\
                    .filter( Q(playbook_id__contains = Qwords)|Q(statement__contains = Qwords) )\
                    .values('insert_time','playbook_id','playbook_md5_info','statement')
            Log(gLogFile,'DEBUG',str(lData))
                        
            #step 3: 生成json格式数据
            if Qwords == 'cnt_flag':
                lDataRet.append({'cnt':iCnt})
            else:
                #用于json格式生成
                dPlaybookInfo = {}
                for dKv in lData:
                    dPlaybookInfo[dKv['playbook_id']] = {
                        'insert_time':dKv['insert_time'].strftime("%Y-%m-%d %H:%M:%S"),                   
                        'playbook_id':dKv['playbook_id'],
                        'playbook_md5_info':dKv['playbook_md5_info'],
                        'statement':dKv['statement'],
                    }
                    
                for user_group_id in dData[sUserName]:
                    for playbook_id in dData[sUserName][user_group_id]:
                        if dPlaybookInfo.has_key(playbook_id):
                            lDataRet.append({
                                'username':_GetSuperUserFromGroupId(user_group_id),
                                'user_group_id':user_group_id,
                                'playbook_id':dPlaybookInfo[playbook_id]['playbook_id'],
                                'insert_time':dPlaybookInfo[playbook_id]['insert_time'],
                                'playbook_md5_info':dPlaybookInfo[playbook_id]['playbook_md5_info'],
                                'statement':dPlaybookInfo[playbook_id]['statement'],
                                'proc_type':dData[sUserName][user_group_id][playbook_id]['proc_type'],
                                'proc_flag':dData[sUserName][user_group_id][playbook_id]['proc_flag'],
                                'map_id':dData[sUserName][user_group_id][playbook_id]['map_id'],
                            })
                            
    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))
        
    return HttpResponse(json.dumps(lDataRet),content_type = 'application/json')
    
    
@login_required
@access_logging
def GetPlaybookEditData(request):
    '''
    获取playbook存储的json数据，用于前端恢复
    '''
    try:
        dDataRet = {}
        sPlaybook = ''
        if request.method == 'POST':
            sPlaybook = (AsbPlaybookInfo.objects.filter(playbook_id = request.POST['playbook_id'])\
                .values('playbook_info_json'))[0]['playbook_info_json']
             
            dDataRet = {
                'playbook':sPlaybook,          
            }
            
    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))
    return HttpResponse(json.dumps(dDataRet),content_type = 'application/json')

    
'''
####################################
文件上传管理模块
####################################
'''    

#文件上传
def TestFilePage(request):
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile = request.FILES['docfile'])
            newdoc.save()

            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('file_page_url'))
    else:
        form = DocumentForm() # A empty, unbound form

    # Load documents for the list page
    documents = Document.objects.all()

    # Render list page with the documents and the form
    '''
    return render_to_response(
        'AnsibleAutomation/file_page.html',
        {'documents': documents, 'form': form},
        context_instance=RequestContext(request)
    )
    '''
    return render(
        request,
        'AnsibleAutomation/file_page.html',
        {'documents': documents, 'form': form},
    )

@login_required
@access_logging
def AddFile(request):
    '''
    上传文件
    '''
    try:
        sUserName = request.user.username
        if request.method == 'POST':    
            if _JudgeUserInUserGroup(sUserName) == 0:
                AsbUserGroupInfo(superuser = sUserName, statement = 'auto create,default user',del_flag = 0).save()
                
            iuser_group_id = AsbUserGroupInfo.objects.filter(superuser = sUserName).values('user_group_id')[0]['user_group_id']
            
            Log(gLogFile,'DEBUG',str(request.POST))
            Log(gLogFile,'DEBUG',str(request.FILES['load_file']))
            
            #新增文件
            
            Obj = AsbFileInfo(
                file_name = str(request.FILES['load_file']),
                file_path = request.FILES['load_file'],
                file_flag = request.POST['file_flag'],
                statement = request.POST['statement'],
                del_flag = 0,
            )
            Obj.save()            
            Log(gLogFile,'DEBUG',str(Obj.id))
            
            #关联至user_group表
            AsbUserGroupFileMap(
                user_group_id = iuser_group_id,
                file_id = Obj.id,
                del_flag = 0,
            ).save()
        
    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))
    return HttpResponseRedirect(reverse('file_page_url'))
        
@login_required
@access_logging
def DelFile(request):
    try:
        if request.method == 'POST':
            #获取用户的superuser组ID
            lData = AsbUserGroupInfo.objects.filter(superuser = request.user.username).values('user_group_id')
            
            #可以支持一个用户是多个group的superuser
            iDelFlag = 0
            for dKv in lData:
                if str(dKv['user_group_id']) == str(request.POST['user_group_id']):
                    iDelFlag = 1
                
            if iDelFlag == 1:
                AsbFileInfo.objects.filter(id = request.POST['file_id']).update(del_flag = 1)
                #将其对应的文件删掉
                sPath = AsbFileInfo.objects.filter(id = request.POST['file_id']).values('file_path')[0]['file_path']
                sPath = settings.MEDIA_ROOT + '/' + sPath
                os.remove(sPath)
            
    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))
        
    return HttpResponse(json.dumps({'ret':iDelFlag}),content_type = 'application/json')




@login_required
@access_logging
def GetFileData(request,SearchFlag,Qwords):
    try:
        lDataRet = []
        if request.method == "GET":
            sUserName = request.user.username
            dData = _GetUserGroup(sUserName)
            
            #get user_group_id file_id
            lFileId = []
            lData = AsbUserGroupFileMap.objects.filter(user_group_id__in = dData[sUserName].keys())\
                .filter(del_flag = 0).values('user_group_id','file_id')
                
            for dKv in lData:
                lFileId.append(dKv['file_id'])
                if dData[sUserName].has_key(dKv['user_group_id']):
                    if not dData[sUserName][dKv['user_group_id']].has_key(dKv['file_id']):
                        dData[sUserName][dKv['user_group_id']][dKv['file_id']] = {}
                else:
                    dData[sUserName][dKv['user_group_id']] = {}
                    dData[sUserName][dKv['user_group_id']][dKv['file_id']] = {}
            
            if SearchFlag == 'using':
                iDelFlag = 0
            elif SearchFlag == 'del':
                iDelFlag = 1
                
            #get file_id file_path
            if Qwords == 'empty_flag':
                lData = AsbFileInfo.objects.filter(id__in = lFileId).filter(del_flag = iDelFlag)\
                .values('insert_time','id','file_name','file_path','file_flag','statement')
            elif Qwords == 'cnt_flag':
                iCnt = AsbFileInfo.objects.filter(id__in = lFileId).filter(del_flag = iDelFlag).count()
            else:
                #普通的search
                lData = AsbFileInfo.objects.filter(id__in = lFileId).filter(del_flag = iDelFlag)\
                    .filter(Q(file_path__contains = Qwords)\
                        |Q(file_flag__contains = Qwords)\
                        |Q(statement__contains = Qwords))\
                    .values('insert_time','id','file_name','file_path','file_flag','statement')
            
            #生产返回数据 
            if Qwords == 'cnt_flag':
                lDataRet.append({'cnt':iCnt})
            else:
                #用于json格式生成
                dFileInfo = {}
                for dKv in lData:
                    dFileInfo[dKv['id']] = {
                        'insert_time':dKv['insert_time'].strftime("%Y-%m-%d %H:%M:%S"),
                        'file_name':dKv['file_name'],
                        'file_path':dKv['file_path'],
                        'file_flag':dKv['file_flag'],
                        'statement':dKv['statement'],
                    }
                
                #生成json格式数据
                for user_group_id in dData[sUserName]:
                    for file_id in dData[sUserName][user_group_id]:
                        if dFileInfo.has_key(file_id):                    
                            lDataRet.append({
                                'username':_GetSuperUserFromGroupId(user_group_id),
                                'user_group_id':user_group_id,
                                'file_id':file_id,
                                'insert_time':dFileInfo[file_id]['insert_time'],
                                'file_name':dFileInfo[file_id]['file_name'],
                                'file_path':dFileInfo[file_id]['file_path'],
                                'file_flag':dFileInfo[file_id]['file_flag'],
                                'statement':dFileInfo[file_id]['statement'],                       
                            })
                
    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))
        
    return HttpResponse(json.dumps(lDataRet),content_type = 'application/json')

    
'''
####################################
playbook执行结果展示
####################################
'''   
    
@login_required
@access_logging
def CheckPlaybookResult(request,MAPID):
    kwvars = {
        'request':request,
    }
    try:
        kwvars['map_or_proc_id'] = MAPID
        kwvars['check_type'] = 'all'
    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))
    
    return render_to_response('AnsibleAutomation/playbook_result.html',
        kwvars,RequestContext(request))

        

@login_required
@access_logging
def CheckPlaybookResultByStep(request,PROCID,MAPID):
    kwvars = {
        'request':request,
    }
    try:
        kwvars['map_or_proc_id'] = PROCID
        kwvars['mapid'] = MAPID #用于在step的场景下返回页面的转跳
        kwvars['check_type'] = 'step'
    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))
    
    return render_to_response('AnsibleAutomation/playbook_result.html',
        kwvars,RequestContext(request))
        
        
@login_required
@access_logging
def GetPlaybookResult(request,Type,ID,SearchFlag):
    lDataRet = []
    try:
        if Type == 'step':
            if SearchFlag == 'asb':
                lData = AsbPbProcResult.objects\
                    .filter(proc_id = ID)\
                    .filter(host = '0.0.0.0')\
                    .values('result_id','insert_time','step_id'
                        ,'obj_id','host','result_info')\
                    .order_by('-insert_time','step_id')
            elif SearchFlag == 'proc':
                lData = AsbPbProcResult.objects\
                    .filter(proc_id = ID)\
                    .exclude(host = '0.0.0.0')\
                    .values('result_id','insert_time','step_id'
                        ,'obj_id','host','result_info')\
                    .order_by('-insert_time','step_id')
        elif Type == 'all':
            if SearchFlag == 'asb':
                lData = AsbPbProcResult.objects\
                    .filter(user_group_playbook_map_id = ID)\
                    .filter(host = '0.0.0.0')\
                    .filter(proc_id = 0)\
                    .values('result_id','insert_time','step_id'
                        ,'obj_id','host','result_info')\
                    .order_by('-insert_time','step_id')
            elif SearchFlag == 'proc':
                lData = AsbPbProcResult.objects\
                    .filter(user_group_playbook_map_id = ID)\
                    .filter(proc_id = 0)\
                    .exclude(host = '0.0.0.0')\
                    .values('result_id','insert_time','step_id'
                        ,'obj_id','host','result_info')\
                    .order_by('-insert_time','step_id')
        
        for dKv in lData:
            lDataRet.append({
                'insert_time':dKv['insert_time'].strftime("%Y-%m-%d %H:%M:%S"),
                'result_id':dKv['result_id'],
                'step_id':dKv['step_id'],
                'obj_id':dKv['obj_id'],
                'host':dKv['host'],
                'result_info':dKv['result_info'],
            })
        
        
    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))
    
    return HttpResponse(json.dumps(lDataRet),content_type = 'application/json')




@login_required
@access_logging
def GetPlaybookData(request,MAPID):
    '''
    获取playbook存储的json数据，用于前端恢复
    '''
    try:
        dDataRet = {}
        sPlaybook = ''
        if request.method == 'POST':
            sPlaybook = (AsbPlaybookInfo.objects.filter(playbook_id = request.POST['playbook_id'])\
                .values('playbook_info_json'))[0]['playbook_info_json']
             
            dDataRet = {
                'playbook':sPlaybook,          
            }
            
    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))
    return HttpResponse(json.dumps(dDataRet),content_type = 'application/json')

    
    
@login_required
@access_logging
def ProcPlaybookByStep(request,MAPID):
    '''
    逐步执行页面
    '''
    kwvars = {
        'request':request,
    }
    try:
        kwvars['mapid'] = MAPID
    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))
    
    return render_to_response('AnsibleAutomation/playbook_result_by_step.html',
        kwvars,RequestContext(request))
    
@login_required
@access_logging
def GetPbStepProcInfo(request,MAPID):
    '''
    获取step proc 列表
    '''
    
    #找到map id对应的playbook MD5
    #select playbook_md5_info from asb_playbook_info where playbook_id = 
    #(select playbook_id from asb_user_group_playbook_map where map_id = '29');
    
    try:
        lDataRet = []
        sMd5Info = AsbPlaybookInfo.objects.filter(playbook_id = \
            AsbUserGroupPlaybookMap.objects\
            .filter(map_id = MAPID).values('playbook_id'))\
            .values('playbook_md5_info')[0]['playbook_md5_info']
        
        Log(gLogFile,'DEBUG',sMd5Info)
        #获取md5与其相同的step信息
        lData = AsbPbStepProcInfo.objects.filter(playbook_md5_info = sMd5Info)\
            .values('proc_id','insert_time','user_group_playbook_map_id',
            'playbook_id','step_id','obj_id','step_info_json','proc_flag')\
            .order_by('-insert_time','step_id')
        
        for dKv in lData:
            lDataRet.append({
                'proc_id':dKv['proc_id'],
                'insert_time':dKv['insert_time'].strftime("%Y-%m-%d %H:%M:%S"),
                'map_id':dKv['user_group_playbook_map_id'],
                'playbook_id':dKv['playbook_id'],
                'step_id':dKv['step_id'],
                'obj_id':dKv['obj_id'],
                'step_info_json':dKv['step_info_json'],
                'proc_flag':dKv['proc_flag'],
            })
        
        
        Log(gLogFile,'DEBUG',str(lDataRet))
        
    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))
    return HttpResponse(json.dumps(lDataRet),content_type = 'application/json')
    


'''
####################################
API模块实现
####################################
'''   
@csrf_exempt
@access_logging
def AsbApi(request):
    try:
        dRet = {
            "status": "failed",
            "status_info": "none",
        }
        
        if request.method == 'POST':
            #解析post内容
            dPayload = json.loads(request.body)
            
            #将源IP写入dPayload中
            dPayload['src_ip'] = request.META['REMOTE_ADDR']
            sPayload = json.dumps(dPayload)
            
            #鉴权
            if JudgeApiAuth(request) == False:
                dRet['status_info'] = "authenticate failed"
            else:
                (JudgeRet,Info) = JudgeApiFormat(dPayload)
                if JudgeRet == False:
                    dRet['status_info'] = Info
                else:
                    if dPayload['type'] == 'process':                
                        #下发任务
                        cRedis = redis.Redis(host = settings.REDIS_HOST,
                            port = settings.REDIS_PORT)
                        cRedis.lpush('asb_api_queue',sPayload)
                        
                        dRet.update({
                            "status":"success",
                            "status_info":"put process into task queue done",
                        })
                    elif dPayload['type'] == 'query':
                        #回调函数，供查询
                        dRet = QueryResult(dPayload)
        
    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))
    return HttpResponse(json.dumps(dRet),content_type = 'application/json')


def QueryResult(dPayload):
    # 查询调用接口的执行结果
    try:
        dRet = {
            'result':[],
        }
        dArg = {}
        
        dArg['opt_time'] = dPayload['opt_time']
        
        if 'username' in dPayload:
            dArg['api_username'] = dPayload['username']
        
        if 'host_ip' in dPayload:
            dArg['host'] = dPayload['host_ip']
            
        if 'src_ip' in dPayload:
            dArg['src_ip'] = dPayload['src_ip']

        qArg = Q()
        for k,v in dArg.items():
            qArg.add( Q( **{k:v} ),Q.AND )
        
        lData = AsbApiProcInfo.objects.filter(qArg)\
            .values('opt_time','cmd_info','ret_info','host')
            
        
        for dKv in lData:
            dTmp = {}
            for K,V in dKv.items():
                if K == 'opt_time':
                    dTmp[K] = V.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    dTmp[K] = V
            dRet['result'].append(dTmp)   
        
    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))
    
    return dRet
    
    
def JudgeApiAuth(request):
    #api请求鉴权
    try:
        sSrcIp = request.META['REMOTE_ADDR']
        dPayload = json.loads(request.body)
        sUsername =dPayload.get('username','none')
        sPasswd = dPayload.get('passwd','none')
        if sUsername == 'none':
            iCnt = AsbApiAuthorityInfo.objects.filter(src_ip = sSrcIp).count()
        else:
            iCnt = AsbApiAuthorityInfo.objects.filter(api_username = sUsername,
                api_passwd = sPasswd).count()
        
        if iCnt != 0:
            return True
            
    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))
    return False
    

def JudgeApiFormat(dPayload):
    #校验API的格式
    #(格式校验结果，错误信息)
    try:
        if 'type' not in dPayload:
            return (False,"format error,type not in payload")
        elif dPayload['type'] == 'process':
            if 'opt_time' in dPayload\
                and 'host' in dPayload\
                and 'cmd' in dPayload:
                
                #验证host格式
                for dHost in dPayload['host']:
                    if 'host_ip' in dHost\
                        and 'host_port' in dHost\
                        and 'host_user' in dHost\
                        and 'host_passwd' in dHost\
                        and 'host_su_user' in dHost\
                        and 'host_su_passwd' in dHost:
                        
                        #验证时间格式
                        if JudgeTimeFormat(dPayload['opt_time']) == False:
                            return (False,'format error,opt_time\'s format'\
                                ' must be xxxx-xx-xx xx:xx:xx')
                        
                        #验证IP
                        if JudgeIpFormat(dHost['host_ip']) == False:
                            return (False,'format error,host_ip\'s format '\
                                'must be x.x.x.x')
                    else:
                        return (False,'format error,host_port|host_user|'\
                            'host_passwd|host_su_user|host_su_passwd'\
                            ' not in payload')
            else:
                return (False,"format error,opt_time|host|cmd not in payload")    
        elif dPayload['type'] == 'query':
            #必选
            if 'opt_time' in dPayload:
                if JudgeTimeFormat(dPayload['opt_time']) == False:
                    return (False,'format error,opt_time\'s format'\
                        ' must be xxxx-xx-xx xx:xx:xx')
            else:
                return (False,"format error,opt_time not in payload")
                
            #可选
            if 'host_ip' in dPayload:
                if JudgeIpFormat(dHost['host_ip']) == False:
                    return (False,'format error,host_ip\'s format '\
                        'must be x.x.x.x')
             
    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))
        
    return (True,'')
    
    
def JudgeTimeFormat(sTime):
    try:
        p = re.compile(r'^\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}$')
        r = p.match(sTime)
        if r == None:
            return False
    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))
    
    return True

def JudgeIpFormat(sIp):
    try:
        p = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
        r = p.match(sIp)
        if r == None:
            return False
    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))
    
    return True
