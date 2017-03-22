#-*- coding: utf-8 -*-

from util.utilfunc import *
from util.utilvar import *
from util.utilmodels import *

from EasyOps.models import *
from EasyOps.forms import *

from UserManage.views.permission import PermissionVerify

@login_required
@PermissionVerify()
@access_logging
def TaskWatchdog(request):
    '''
    展示任务信息
    '''
    lData = WdTaskInfo.objects.filter(del_flag=0).values('insert_time','id','task','task_info','operator','mail_recv').order_by('-insert_time')[:200]
    
    lst = SelfPaginator(request,lData, 40)
    kwvars = {
        'lPage':lst,
        'request':request,
    }
    return render_to_response('EasyOps/task_watchdog.html',kwvars,RequestContext(request))


@login_required
@access_logging
def AddTaskWatchdog(request):
    '''
    添加监控任务
    '''
    if request.method == 'POST':
        POST1 = request.POST.copy()
        POST1.update({'operator':request.user.username})
        POST1.update({'del_flag':'0'})
        POST1.update({'task_interval':'300'})
        #POST1.pop('name_sel_host_ip')
        form = AddTaskWatchdogForm(POST1)
        if form.is_valid():
            form.save()
            
        #根据编辑的内容调整task_host_map表
        
        #获取插入的task_id
        lID = WdTaskInfo.objects.filter(task = POST1['task']).filter(task_info = POST1['task_info']).filter(mail_recv = POST1['mail_recv']).values('id')
        
        for dKv in lID:
            ID = dKv['id']
        
        
        lWdHostIp = request.POST.getlist('name_sel_host_ip')
        #1、查询host ip对应的host id
        lWdHostId = WdHostInfo.objects.filter(host_ip__in = lWdHostIp).values('id')
        
        #not in task_host_map
        #lWdHostIdNotInMap = lWdHostId.exclude(id__in = (WdTaskHostMap.objects.filter(task_id = ID).values('host_id'))) 
              
        #2、将map表中该task_id的所有任务都标识为del
        #WdTaskHostMap.objects.filter(task_id = ID).update(del_flag = 1)
        
        #3、将包含在select中的任务标识为add
        #WdTaskHostMap.objects.filter(host_id__in = lWdHostId).filter(task_id = ID).update(del_flag = 0)
        
        #4、插入新增的任务
        for dKv in lWdHostId:
            for Key in dKv:
                Obj = WdTaskHostMap(task_id = ID,host_id = dKv[Key],md5_0 = 'none',md5_1 = 'none',del_flag = 0,opt_flag = 0)
                Obj.save()        
        
        #5、最后更新task_id对应的opt_flag
        WdTaskHostMap.objects.filter(task_id = ID).update(opt_flag = 0)

        return HttpResponseRedirect(reverse('task_watchdogurl'))

    else:
        form = EditTaskWatchdogForm()
                
        #检索所有的主机
        lHostData = WdHostInfo.objects.values('host_ip')
        
        lTmp = []
        for dKv in lHostData:
            dTmp = {}
            for Key in dKv:
                dTmp[Key] = dKv[Key]
            lTmp.append(dTmp)
        
        kwvars = {
                  'request':request,
                  'form':form,
                  'lhostdata':json.dumps(lTmp),              
                  }
        
        return render_to_response('EasyOps/add_task_watchdog.html',kwvars,RequestContext(request))
    
    

@login_required
@access_logging
def EditTaskWatchdog(request):
    '''
    编辑监控任务
    '''
    iRet = 1
    if request.method == 'POST':
        lTmp = request.POST.lists();
        for tTmp in lTmp:
            if tTmp[0] == 'sel_host[]':
                tSelHost = tTmp[1]
            if tTmp[0] == 'sel_atom_task[]':
                tSelAtomTask = tTmp[1]
            if tTmp[0] == 'task_id':
                TaskId = tTmp[1][0]
                
        #检索出对应的atom task和host
        lAtomTask = WdAtomTaskInfo.objects.filter(id__in = tSelAtomTask).values('id','task')
        
        #将atomtask拼装成一条命令
        sTask = ''
        sTaskId = 'task_id:'
        for dKv in lAtomTask:
            sTask += dKv['task'] + ';'
            sTaskId += str(dKv['id']) + ';'
        sTaskId += 'host_id:'
        for sHostId in tSelHost:
            sTaskId += sHostId + ';'
        
        #将拼装后的命令更新wd_task_info表
        WdTaskInfo.objects.filter(id = TaskId).update(task = sTask,task_info = sTaskId)
        
        #not in task_host_map
        lWdHostIdInMap = WdTaskHostMap.objects.filter(task_id = TaskId).values('host_id')
        lHostIdNotInMap = []
        for HostId in tSelHost:
            iFindFlag = 0
            for dKv in lWdHostIdInMap:
                if dKv['host_id'] == int(HostId):
                    iFindFlag = 1
            if iFindFlag == 0:
                lHostIdNotInMap.append(HostId)
        
        
        #将map表中该task_id的所有任务都标识为del
        WdTaskHostMap.objects.filter(task_id = TaskId).update(del_flag = 1)
        #将包含在select中的任务标识为add
        WdTaskHostMap.objects.filter(host_id__in = tSelHost).filter(task_id = TaskId).update(del_flag = 0)
        #插入新增的任务
        for HostId in lHostIdNotInMap:
            Obj = WdTaskHostMap(task_id = TaskId,host_id = HostId,md5_0 = 'none',md5_1 = 'none',del_flag = 0,opt_flag = 0)
            Obj.save()
        
        #最后更新task_id对应的opt_flag
        WdTaskHostMap.objects.filter(task_id = TaskId).update(opt_flag = 0)
        iRet = 0
    kwvars = {
        'ldata':iRet,
    }
    
    return HttpResponse(json.dumps(kwvars),content_type = 'application/json')


@login_required
@access_logging
def DelTaskWatchdog(request,ID):
    '''
    删除监控任务
    '''
    #1、将wd_task_info中对应的记录标识为删除
    WdTaskInfo.objects.filter(id = ID).update(del_flag = 1,operator = request.user.username)
    #2、将wd_task_host_map中对应的记录标识为删除
    WdTaskHostMap.objects.filter(task_id = ID).update(del_flag = 1,opt_flag = 0)
    return HttpResponseRedirect(reverse('task_watchdogurl'))
    
    

@login_required
@access_logging
def GetTaskWatchdog(request,ID,FLAG,PRO_FLAG):
    '''
    根据任务ID，获取task_host_map中的记录
    '''
    #1、从task_host_map表中获取指定task id 对应的数据
    if FLAG == '0':
        #获取异常数据
        if PRO_FLAG == '0': #PRO_FLAG区分实时操作和常态操作
            lData = WdTaskHostMap.objects.filter(task_id = ID).filter(del_flag = 0).filter(opt_flag = 1).exclude(md5_0 = F('md5_1')).values('insert_time','update_time','host_id','md5_0','md5_1')
        elif PRO_FLAG == '1':
            lData = WdRealtimeTaskHostMap.objects.filter(task_id = ID).filter(opt_0_flag = 1).filter(opt_1_flag = 1).exclude(md5_0 = F('md5_1')).values('insert_time','update_time','host_id','md5_0','md5_1')
    elif FLAG == '1':
        #获取全部数据
        if PRO_FLAG == '0':
            lData = WdTaskHostMap.objects.filter(task_id = ID).filter(del_flag = 0).filter(opt_flag = 1).values('insert_time','update_time','host_id','md5_0','md5_1')
        elif PRO_FLAG == '1':
            lData = WdRealtimeTaskHostMap.objects.filter(task_id = ID).filter(opt_0_flag = 1).filter(opt_1_flag = 1).values('insert_time','update_time','host_id','md5_0','md5_1')    
    #2、从host_info表中获取host_id对应的host_ip
    if PRO_FLAG == '0':
        lHostIdIp = WdHostInfo.objects.filter(del_flag = 0).values('id','host_ip')
    elif PRO_FLAG == '1':
        lHostIdIp = WdRealtimeHostInfo.objects.filter(del_flag = 0).values('id','host_ip')
        
    #3、数据整理,笨方法（select wd_task_host_map.insert_time,wd_task_host_map.update_time,wd_task_host_map.task_id,wd_host_info.host_ip from wd_task_host_map,wd_host_info where wd_host_info.id = wd_task_host_map.host_id;）
    for dKv in lData:
        dKv['host_ip'] = 'none'
    
    for dKv in lData:
        for Key in dKv:
            if Key == 'host_id':
                for dHostKv in lHostIdIp:
                    if dHostKv['id'] == dKv[Key]:
                        dKv['host_ip'] = dHostKv['host_ip']
                
    
    #2、展示
    lst = SelfPaginator(request,lData, 40)
    
    kwvars = {
        'lPage':lst,
        'request':request,
        'task_id':ID,
        'task_flag':FLAG,
        'pro_flag':PRO_FLAG,
    }
    return render_to_response('EasyOps/get_task_watchdog.html',kwvars,RequestContext(request))

@login_required
@access_logging
def GetTheTaskWatchdog(request,TASK,HOST,PRO_FLAG):
    '''
    获取task_host_map中指定host_ip的ret_0/ret_1信息，并比对
    '''
    if PRO_FLAG == '0':
        lData = WdTaskHostMap.objects.filter(task_id = TASK).filter(host_id = HOST).values('ret_0','ret_1')
        #lData = WdTaskHostMap.objects.filter(task_id = TASK).values('ret_0','ret_1')
    else:
        lData = WdRealtimeTaskHostMap.objects.filter(task_id = TASK).filter(host_id = HOST).values('ret_0','ret_1')   
    
    lDataTmp = []
    for dKv in lData:
        dTmp = {}
        for Key in dKv:
            dTmp[Key] = dKv[Key]
        lDataTmp.append(dTmp)

    kwvars = {
        'ldata':json.dumps(lDataTmp),
    }

    return HttpResponse(json.dumps(kwvars),content_type = 'application/json')

@login_required
@access_logging
def UpdateTheTaskWatchdog(request,TASK,HOST):
    '''
    用户确认后，将实时探测数据更新至监控标准（ret、md5都更新）
    '''
    WdTaskHostMap.objects.filter(task_id = TASK).filter(host_id = HOST).update(ret_0 = F("ret_1"),md5_0 = F("md5_1"))
    return HttpResponseRedirect(reverse('get_task_watchdogurl',args=[TASK,1,0]))

@login_required
@access_logging
def AtomTaskWatchdog(request):
    '''
    原始命令展示
    '''
    lData = WdAtomTaskInfo.objects.filter(del_flag=0).values('insert_time','id','task','task_info','operator').order_by('-insert_time')[:200]
    lst = SelfPaginator(request,lData, 40)

    form = AddAtomTaskWatchdogForm()
    
    kwvars = {
        'lPage':lst,
        'request':request,
        'form':form,
    }
    return render_to_response('EasyOps/atom_task_watchdog.html',kwvars,RequestContext(request))
    

@login_required
@access_logging
def AddAtomTaskWatchdog(request):
    '''
    添加原子操作
    '''
    
    if request.method == 'POST':
        POST1 = request.POST.copy()
        POST1.update({'operator':request.user.username})
        POST1.update({'del_flag':'0'})
        POST1.update({'task_interval':'300'})
        form = AddAtomTaskWatchdogForm(POST1)
        if form.is_valid():
            form.save()
            
    return HttpResponseRedirect(reverse('atom_task_watchdogurl'))
    
    
@login_required
@access_logging
def EditAtomTaskWatchdog(request):
    '''
    编辑原子操作
    '''
    if request.method == 'POST':
        POST1 = request.POST.copy()
        POST1.update({'operator':request.user.username})
        POST1.update({'del_flag':'0'})
        POST1.update({'task_interval':'300'})
        
        Instance = WdAtomTaskInfo.objects.get(id = POST1['id'])
        
        form = AddAtomTaskWatchdogForm(POST1,instance = Instance)
        if form.is_valid():
            form.save()
    
    return HttpResponseRedirect(reverse('atom_task_watchdogurl'))

@login_required
@access_logging
def DelAtomTaskWatchdog(request,ID):
    '''
    删除原子操作
    '''
    WdAtomTaskInfo.objects.filter(id = ID).update(del_flag = 1,operator = request.user.username)
    return HttpResponseRedirect(reverse('atom_task_watchdogurl'))
    
@login_required
@access_logging
def RealTimeTaskWatchdog(request):
    '''
    配置实时维护工具
    '''
    #添加自动化运维接口测试逻辑 ansible_test
    #lData = WdRealtimeTaskInfo.objects.all().order_by('-insert_time')
    lData = WdRealtimeTaskInfo.objects.all().exclude(operator = 'ansible_test').order_by('-insert_time')
    lst = SelfPaginator(request,lData,40)
    
    kwvars = {
        'lPage':lst,
        'request':request,
    }
    return render_to_response('EasyOps/realtime_task_watchdog.html',kwvars,RequestContext(request))

    
@login_required
@access_logging
def GetAtomTaskAndHostWatchdog(request):
    '''
    获取原子命令和host的json数据
    '''
    lData = WdAtomTaskInfo.objects.filter(del_flag = 0).values('insert_time','id','task','task_info','operator').order_by('-insert_time')
    
    #此处operator代表主机类型（大机配置监控、内网探测等不同类型）
    lDataHost = WdHostInfo.objects.filter(del_flag = 0).values('insert_time','id','host_ip','operator').order_by('operator')
    
    dDataTmp = {}
    lDataTmp = []    
    for dKv in lData:
        dTmp = {}
        for Key in dKv:
            if Key == 'insert_time':
                dTmp[Key] = dKv[Key].strftime("%Y-%m-%d %H:%M:%S")
            else:
                dTmp[Key] = dKv[Key]
        lDataTmp.append(dTmp)        
    dDataTmp['task_info'] = lDataTmp
    
    lDataTmp = []    
    for dKv in lDataHost:
        dTmp = {}
        for Key in dKv:
            if Key == 'insert_time':
                dTmp[Key] = dKv[Key].strftime("%Y-%m-%d %H:%M:%S")
            else:
                dTmp[Key] = dKv[Key]
        lDataTmp.append(dTmp)
    dDataTmp['host_info'] = lDataTmp
    
    kwvars = {
        'page_data' :dDataTmp,
    }
    
    return HttpResponse(json.dumps(kwvars),content_type = 'application/json')

    
@login_required
@access_logging
def GetAtomTaskWatchdog(request):
    '''
    获取原子命令，用于实时监控任务
    '''
    lData = WdAtomTaskInfo.objects.filter(del_flag = 0).values('insert_time','id','task','task_info','operator').order_by('-insert_time')
    dDataTmp = {}
    lDataTmp = []    
    for dKv in lData:
        dTmp = {}
        for Key in dKv:
            if Key == 'insert_time':
                dTmp[Key] = dKv[Key].strftime("%Y-%m-%d %H:%M:%S")
            else:
                dTmp[Key] = dKv[Key]
        lDataTmp.append(dTmp)        
    dDataTmp['task_info'] = lDataTmp
    kwvars = {
        'page_data' :dDataTmp,
    }
    
    return HttpResponse(json.dumps(kwvars),content_type = 'application/json')
    
@login_required
@access_logging
def AddRealTimeTaskWatchdog(request):
    if request.method == 'POST':
        
        #获取host和atomtask的id
        lTmp = request.POST.lists()
        for tTmp in lTmp:
            if tTmp[0] == 'sel_host[]':
                tSelHost = tTmp[1]
            if tTmp[0] == 'sel_atom_task[]':
                tSelAtomTask = tTmp[1]
            if tTmp[0] == 'opt_flag':
                OptFlag = tTmp[1][0]
        
        #检索出对应的atom task和host
        lAtomTask = WdAtomTaskInfo.objects.filter(id__in = tSelAtomTask).values('id','task')
        
        #将atomtask拼装成一条命令
        sTask = ''
        sTaskId = 'task_id:'
        for dKv in lAtomTask:
            sTask += dKv['task'] + ';'
            sTaskId += str(dKv['id']) + ';'
        sTaskId += 'host_id:'
        for sHostId in tSelHost:
            sTaskId += sHostId + ';'
        
        if OptFlag == '0':
            #将拼装后的命令插入wd_task_info表
            ObjTmp = WdTaskInfo(task = sTask,task_info = sTaskId,task_interval = 300,operator = request.user.username,del_flag = 0)
            ObjTmp.save()
            
            #获取插入的task_id
            #lID = WdTaskInfo.objects.filter(task_info = sTaskId).filter(del_flag = 0).values('id').order_by('-id')[0:1]
            #ID = lID[0]['id'] #只取一个，可能会有多个重复任务的情况
            ID = ObjTmp.id
            
            #将task和host的映射关系写入wd_realtime_task_host_map表
            for iId in tSelHost:
                ObjTmp = WdTaskHostMap(task_id = ID,host_id = iId,md5_0 = 'none',md5_1 = 'none',del_flag = 0,opt_flag = 0)
                ObjTmp.save()

        
    kwvars = {
        'ldata':OptFlag,
    }
    
    return HttpResponse(json.dumps(kwvars),content_type = 'application/json')

    
@login_required
@access_logging
def AddRealTimeTaskNewWatchdog(request):
    #第三版，允许前台输入host信息
    if request.method == 'POST':
        lTmp = request.POST.lists()
        for tTmp in lTmp:
            if tTmp[0] == 'sel_host':
                tSelHost = json.loads(tTmp[1][0])
            if tTmp[0] == 'sel_atom_task':
                tSelAtomTask = json.loads(tTmp[1][0])
        
        #插入realtimehost表
        lHostId = []
        for dTmp in tSelHost:
            Obj = WdRealtimeHostInfo.objects.create(host_ip = dTmp['host_ip'],host_domain = 'none',host_port = 22,host_user = dTmp['username'],host_passwd = dTmp['passwd'],host_su_user = dTmp['su_username'],host_su_passwd = dTmp['su_passwd'],del_flag = 0,operator = request.user.username)
            lHostId.append(Obj.id)
        
        #检索出对应的atom task和host
        lAtomTask = WdAtomTaskInfo.objects.filter(id__in = tSelAtomTask).values('id','task')
        
        #将atomtask拼装成一条命令
        sTask = ''
        sTaskId = 'task_id:'
        for dKv in lAtomTask:
            sTask += dKv['task'] + ';'
            sTaskId += str(dKv['id']) + ';'
        sTaskId += 'host_id:'
        for sHostId in lHostId:
            sTaskId += str(sHostId) + ';'
            
        #将拼装后的命令插入wd_realtime_task_info表
        Obj = WdRealtimeTaskInfo.objects.create(task = sTask,task_info = sTaskId,task_interval = 300,operator = request.user.username,del_flag = 0,opt_stat = 0)
        ID = Obj.id
        for iId in lHostId:
            ObjTmp = WdRealtimeTaskHostMap(task_id = ID,host_id = iId,md5_0 = 'none',md5_1 = 'none',opt_0_flag = 1,opt_1_flag = 1)
            ObjTmp.save()
            
    kwvars = {
        'ldata':lTmp,
    }
    return HttpResponse(json.dumps(kwvars),content_type = 'application/json')
    
    
@login_required
@access_logging
def SendRealTimeTaskCmdWatchdog(request):
    if request.method == 'POST':
        lTmp = request.POST.lists()
        for tTmp in lTmp:
            if tTmp[0] == 'task_id':
                Id = tTmp[1][0]
            if tTmp[0] == 'task_flag':
                Flag = tTmp[1][0]
        
        if Flag == '0':
            WdRealtimeTaskHostMap.objects.filter(task_id = Id).update(opt_0_flag = 0)
            WdRealtimeTaskInfo.objects.filter(id = Id).filter(opt_stat = 0).update(opt_stat = 1)
        if Flag == '1':
            WdRealtimeTaskHostMap.objects.filter(task_id = Id).update(opt_1_flag = 0)
            WdRealtimeTaskInfo.objects.filter(id = Id).filter(opt_stat = 2).update(opt_stat = 3)
        
    kwvars = {
        'ldata':Id + ' ' + Flag
    }
    
    return HttpResponse(json.dumps(kwvars),content_type = 'application/json')

    
@login_required
@access_logging
def GetTheTaskInfoWatchdog(request):
    '''
    获取指定taskinfo
    '''
    if request.method == 'POST':
        lTmp = request.POST.lists()
        for tTmp in lTmp:
            if tTmp[0] == 'task_id':
                TaskId = tTmp[1][0]
            if tTmp[0] == 'pro_flag':
                ProFlag = tTmp[1][0]
    
        if ProFlag == '0':
            #task_watchdog
            lData = WdTaskInfo.objects.filter(id = TaskId).values('task')
            
        elif ProFlag == '1':
            #realtime
            lData = WdRealtimeTaskInfo.objects.filter(id = TaskId).values('task')
        lDataTmp = []
        for dKv in lData:
            dTmp = {}
            for Key in dKv:
                dTmp[Key] = dKv[Key]
            lDataTmp.append(dTmp)
        sTaskInfo = lData[0]['task']    
        
    kwvars = {
        'task_info':sTaskInfo
    }
    
    return HttpResponse(json.dumps(kwvars),content_type = 'application/json')

@login_required
@access_logging
def GetTaskByIpWatchdog(request):
    '''
    根据host ip获取指定taskinfo
    '''
    if request.method == 'POST':
        sHostIp = request.POST['input_sel_ip']
        
        #select * from wd_task_host_map where host_id in (select id from wd_host_info where host_ip = '192.168.235.129')\G;
        lData = WdTaskHostMap.objects.filter(host_id__in = (WdHostInfo.objects.filter(host_ip = sHostIp).values('id'))).values('insert_time','update_time','task_id','host_id','md5_0','md5_1')
        
        lst = SelfPaginator(request,lData, 40)
        
    kwvars = {
        'host_ip':sHostIp,
        'lPage':lst,
        'request':request,        
        'pro_flag': '0', #用于前端显示
    }
    return render_to_response('EasyOps/get_task_by_ip_watchdog.html',kwvars,RequestContext(request))

@login_required
@access_logging
def GetTaskDetailByIdWatchdog(request):
    #根据task id，获取task的明细
    if request.method == 'POST':
        iTaskId = request.POST['task_id']
        lData = WdTaskInfo.objects.filter(id = iTaskId).values('task')
    kwvars = {
        'data' :lData[0],
    }
    
    return HttpResponse(json.dumps(kwvars),content_type = 'application/json')

@login_required
@access_logging
def ResetRealtimeTaskWatchdog(request,ID):
    #重置wd_realtime_task_info表的opt_stat为0，重新开始一次任务
    WdRealtimeTaskInfo.objects.filter(id = ID).update(opt_stat = 0)
    
    return HttpResponseRedirect(reverse('realtime_task_watchdogurl'))
    
    
#和阿炜测试用的两个api
@csrf_exempt
def TestAnsibleCmdSend(request):
    sRetFlag = 'fail'
    sRetMsg = ''
    
    if request.method == 'POST':
        sRetMsg = request.body
        dRet = json.loads(sRetMsg)
        sTaskId = dRet.get('task_id','null')
        lHostId = dRet.get('host_ip',[])
        iPlayBook = dRet.get('playbook',0)
        
        sTaskInfo = ''
        for iHostId in lHostId:
            sTaskInfo += str(iHostId) + ';'
        
        sTaskInfo += sTaskId
        
        #测试时，一个atom即一个playbook，检索出对应的atom task，写入realtimetaskinfo表
        Obj = WdRealtimeTaskInfo.objects.create(task = (WdAtomTaskInfo.objects.filter(id = iPlayBook).values('task')[:1])[0]['task'],task_interval = 300,task_info = sTaskInfo,operator = 'ansible_test',del_flag = 0,opt_stat = 0)
        ID = Obj.id
        #将拼装后的命令插入wd_realtime_task_info表
        if(ID):
            for iHostId in lHostId:
                #测试中opt_0_flag设为0
                WdRealtimeTaskHostMap.objects.create(task_id = ID,host_id = iHostId,md5_0 = 'none',md5_1 = 'none',opt_0_flag = 0,opt_1_flag = 1)
                sRetFlag = 'success'
        
    ret_msg = {
        'ret':sRetFlag,
        'msg':sRetMsg,
    }
    
    return HttpResponse(json.dumps(ret_msg),content_type = 'application/json')
    
@csrf_exempt  
def TestAnsibleResultQuery(request):
    sRetFlag = 'fail'
    sRetMsg = ''
    if request.method == 'POST':
        sRetMsg = request.body
        dRet = json.loads(sRetMsg)
        sTaskId = dRet.get('task_id','null')
        sRetMsg = ''
        #从task_info中查找该task_id
        Obj = WdRealtimeTaskInfo.objects.filter(task_info__contains = sTaskId).values('id')
        if Obj:
            #检索任务结果
            lData = WdRealtimeTaskHostMap.objects.filter(task_id = Obj[0]['id']).filter(opt_0_flag = 1).values('ret_0')
            for dKv in lData:
                sRetMsg += dKv['ret_0']      
        sRetFlag = 'success' 
    ret_msg = {
        'ret':sRetFlag,
        'msg':sRetMsg,
    }
    
    return HttpResponse(json.dumps(ret_msg),content_type = 'application/json')
    
@login_required
@access_logging
def GetTaskHostWatchdog(request):
    #根据post过来的taskinfo字段，返回task明细、hostip
    sTask = ''
    lData = []
    if request.method == 'POST':
        sTaskInfo = request.POST['taskinfo']
        sFlag = request.POST['opt_flag']
        #分离出task、host
        sTask = sTaskInfo[0:sTaskInfo.find('host_id')]
        sHost = sTaskInfo[sTaskInfo.find('host_id'):]
        sTask = (sTask[sTask.find(':')+1:]).strip(';')
        sHost = (sHost[sHost.find(':')+1:]).strip(';')
        lTask = sTask.split(';')
        lHost = sHost.split(';')
        
        #获取对应的主机信息
        if sFlag == 'normal':
            lData = WdHostInfo.objects.filter(id__in = lHost).values('id','host_ip','host_user','host_su_user')
        elif sFlag == 'realtime':
            lData = WdRealtimeHostInfo.objects.filter(id__in = lHost).values('id','host_ip','host_user','host_su_user')
        else:
            lData = []
            
        lDataTmp = []
        for dKv in lData:
            dTmp = {}
            for Key in dKv:
                dTmp[Key] = dKv[Key]
            lDataTmp.append(dTmp)
        
    ret_msg = {
        #'task':sTask,
        'host_ip':lDataTmp,
    }
    
    return HttpResponse(json.dumps(ret_msg),content_type = 'application/json')
    
    
    
    
    
    