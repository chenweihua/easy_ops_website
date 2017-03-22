#-*- coding: utf-8 -*-
from django.shortcuts import render

# Create your views here.
from util.utilfunc import *
from util.utilvar import *
from util.utilmodels import *

from InteranetDetect.models import *
from InteranetDetect.forms import *

from UserManage.views.permission import PermissionVerify


@login_required
@access_logging
def MainPage(request):
    #主页面
    kwvars = {
        'request':request,
    }
    return render_to_response('InteranetDetect/main_page.html',kwvars,RequestContext(request))

@login_required
@access_logging
def NetSegPage(request):
    #网段管理页面
    kwvars = {
        'request':request,
    }
    return render_to_response('InteranetDetect/net_seg_page.html',kwvars,RequestContext(request))

@login_required
@access_logging   
def IpPage(request):
    #IP探测信息
    kwvars = {
        'request':request,
    }
    return render_to_response('InteranetDetect/ip_page.html',kwvars,RequestContext(request))
    
@login_required
@access_logging
def ProcPage(request):
    #进程信息
    kwvars = {
        'request':request,
    }
    return render_to_response('InteranetDetect/proc_page.html',kwvars,RequestContext(request))
    
    
@login_required
@access_logging
def DevPage(request):
    #设备管理页面
    kwvars = {
        'request':request,
    }
    return render_to_response('InteranetDetect/dev_page.html',kwvars,RequestContext(request))
    
@login_required
def QueryMain(request):
    #获取main_page的展示信息
    kwvars = {}
    
    if request.method == 'POST':
        #select count(distinct id) from xxx
        iNetSegCnt = IdIpDetectNetworkHostMap.objects.values('id').count()
        iNetSegStartCnt = IdIpDetectNetworkHostMap.objects.filter(opt_type = 'start').values('id').count()
        #select sum(ipcnt) from id_ip_detect_network_host_map where opt_type != 'del';
        iIpCnt = IdIpDetectNetworkHostMap.objects.exclude(opt_type = 'del').aggregate(Sum('ipcnt'))
        iIpStartCnt = IdIpDetectNetworkHostMap.objects.filter(opt_type = 'start').aggregate(Sum('ipcnt'))
        iIpRetCnt = IdIpDetectNetworkHostMap.objects.exclude(opt_type = 'del').aggregate(Sum('using_ipcnt'))
        iDevCnt = IdDevInfo.objects.filter(dev_type = 'detector').values('dev_ip').distinct().count()
        kwvars = {
            'net_seg_cnt' : iNetSegCnt,
            'ip_cnt' : iIpCnt['ipcnt__sum'],
            'net_seg_start_cnt' : iNetSegStartCnt,
            'ip_ret_cnt' : iIpRetCnt['using_ipcnt__sum'],
            'ip_start_cnt':iIpStartCnt['ipcnt__sum'],
            'dev_cnt' : iDevCnt,
        }
    return HttpResponse(json.dumps(kwvars),content_type = 'application/json')

    
@login_required
def QueryIp(request):
    #查询IP
    kwvars = {}
    if request.method == 'POST':
        sIp = request.POST['query_ip']
        
        if sIp == 'get_all':
            lData = IdIpDetectResult.objects.values('insert_time','ip','ttl','time_consume','arp_addr','agent_ip')[:100]            
        else:
            lData = IdIpDetectResult.objects.filter(ip__startswith = sIp).values('insert_time','ip','ttl','time_consume','arp_addr','agent_ip')[:1000]
        
        lDataTmp = []
        for dKv in lData:
            dTmp = {}
            for Key in dKv:
                if Key == 'insert_time':
                    dTmp[Key] = dKv[Key].strftime("%Y-%m-%d %H:%M:%S")
                else:
                    dTmp[Key] = dKv[Key]
            lDataTmp.append(dTmp)
        kwvars = {
            'ldata':lDataTmp,
        }
    return HttpResponse(json.dumps(kwvars),content_type = 'application/json')    
    
    
@login_required    
def QueryNetSeg(request):
    #查询网段IP
    kwvars = {}
    if request.method == 'POST':
        sIp = request.POST['query_ip']
        
        if sIp == 'get_all':
            lData = IdIpDetectNetworkHostMap.objects.values('insert_time','id','network_segment','mask','dev_ip','ipcnt','using_ipcnt','det_type','opt_type')
        else:
            lData = IdIpDetectNetworkHostMap.objects.filter(network_segment__startswith = sIp).values('insert_time','id','network_segment','mask','dev_ip','ipcnt','using_ipcnt','det_type','opt_type')
        
        #获取已启用的探测端IP，用于网段信息编辑使用（暂不使用）
        lDev = IdHeartbeatInfo.objects.values('dev_ip').distinct()
        
   
        lDataTmp = []
        for dKv in lData:
            dTmp = {}
            for Key in dKv:
                if Key == 'insert_time':
                    dTmp[Key] = dKv[Key].strftime("%Y-%m-%d %H:%M:%S")
                else:
                    dTmp[Key] = dKv[Key]
            lDataTmp.append(dTmp)

        lDevTmp = []
        for dKv in lDev:
            dTmp = {}
            for Key in dKv:
                dTmp[Key] = dKv[Key]
            lDevTmp.append(dTmp)
            
        kwvars = {
            'ldata':lDataTmp,
            'ldev':lDevTmp,
        }
    return HttpResponse(json.dumps(kwvars),content_type = 'application/json')


@login_required
@access_logging
def EditNetSeg(request):
    #更新网段信息
    kwvars = {}
    if request.method == 'POST':
        sId = request.POST['id_id']
        sNetSeg = request.POST['id_network_segment']
        sMask = request.POST['id_mask']
        sDevIp = request.POST['id_dev_ip']
        sDetType = request.POST['id_det_type']
        sOptType = request.POST['id_opt_type']
        
        IdIpDetectNetworkHostMap.objects.filter(id=sId).update(det_type = sDetType,opt_type = sOptType)

        kwvars = {
            'ret':[sId,sNetSeg,sMask,sDetType,sOptType]
        }
    return HttpResponse(json.dumps(kwvars),content_type = 'application/json')    
    

@login_required
@access_logging
def QueryProcHeartbeat(request):
    #获取进程心跳信息
    kwvars = {}
    if request.method == 'POST':
        #select * from id_heartbeat_info group by dev_ip,task order by insert_time desc; 
        lDataCommonProc = IdHeartbeatInfo.objects.filter(task = 'client_common_proc').filter(tab_date_time__startswith=datetime.date.today())\
        .values('insert_time','task','dev_ip','send_pkg_num','recv_pkg_num','rc0','rc1','rc2').order_by('insert_time')
        lDataPingProc = IdHeartbeatInfo.objects.filter(task = 'ping_det_proc').filter(tab_date_time__startswith=datetime.date.today())\
        .values('insert_time','task','dev_ip','send_pkg_num','recv_pkg_num','rc0','rc1','rc2').order_by('insert_time')

        lCommonTmp = []
        for dKv in lDataCommonProc:
            dTmp = {}
            for Key in dKv:
                if Key == 'insert_time':
                    dTmp[Key] = dKv[Key].strftime("%Y-%m-%d %H:%M:%S")
                else:
                    dTmp[Key] = dKv[Key]
            lCommonTmp.append(dTmp)
            
        lPingTmp = []
        for dKv in lDataPingProc:
            dTmp = {}
            for Key in dKv:
                if Key == 'insert_time':
                    dTmp[Key] = dKv[Key].strftime("%Y-%m-%d %H:%M:%S")
                else:
                    dTmp[Key] = dKv[Key]
            lPingTmp.append(dTmp)
    
        kwvars = {
            'lcommon_proc':lCommonTmp,
            'lping_proc':lPingTmp,
        }
    
    return HttpResponse(json.dumps(kwvars),content_type = 'application/json')

@login_required
@access_logging
def QueryDev(request):
    #获取探测端信息
    kwvars = {}
    if request.method == 'POST':
        lData = IdDevInfo.objects.values('insert_time','dev_ip','dev_type','net_type')
        lDataTmp = []
        for dKv in lData:
            dTmp = {}
            for Key in dKv:
                if Key == 'insert_time':
                    dTmp[Key] = dKv[Key].strftime("%Y-%m-%d %H:%M:%S")
                else:
                    dTmp[Key] = dKv[Key]
            lDataTmp.append(dTmp)
        kwvars = {
            'ldata':lDataTmp,
        }
    else:
        kwvars = {
            'ldata':'err',
        }
        
    return HttpResponse(json.dumps(kwvars),content_type = 'application/json')
    
@csrf_exempt
def PostTest(request):
    '''
    opcm接口测试使用
    '''
    kwvars = {}
    if request.method == 'POST':
        kwvars = {
            'response':request.readline(), #获取post的payload
            'error':'',
            'status':'200',
        }
    else:
        kwvars = {
            'response':'none',
            'error':'not post request',
            'status':'400',
        }
    
    return HttpResponse(json.dumps(kwvars),content_type = 'application/json')
    
    
'''
交换机mac table信息采集
'''
@login_required
@access_logging
def SwMainPage(request):
    #主页面
    kwvars = {
        'request':request,
    }
    return render_to_response('InteranetDetect/sw_main_page.html',kwvars,RequestContext(request))

@login_required
@access_logging
def SwSwitchPage(request):
    #交换机管理
    kwvars = {
        'request':request,
    }
    return render_to_response('InteranetDetect/sw_switch_page.html',kwvars,RequestContext(request))

    
@login_required
@access_logging
def SwSwitchRetPage(request):
    #mac地址管理
    kwvars = {
        'request':request,
    }
    return render_to_response('InteranetDetect/sw_switch_ret_page.html',kwvars,RequestContext(request))

    
@login_required
@access_logging
def SwSwitchAccessLogPage(request):
    #探测日志
    kwvars = {
        'request':request,
    }
    return render_to_response('InteranetDetect/sw_switch_access_log_page.html',kwvars,RequestContext(request))
    
@login_required
@access_logging
def SwGetSwitchData(request,SearchFlag,Qwords):
    try:
        lDataRet = []
        if request.method == 'GET':
            if SearchFlag == 'using':
                iDelFlag = 0
            elif SearchFlag == 'del':
                iDelFlag = 1
                
            if Qwords == 'empty_flag':
                lData = SwSwitchInfo.objects.filter(del_flag = iDelFlag)\
                    .values('insert_time','switch_ip','logic_name','agent_ip','mac_cnt','del_flag','proc_flag')
            else:
                lData = SwSwitchInfo.objects.filter(del_flag = iDelFlag).filter(Q(switch_ip__contains = Qwords)|Q(logic_name__contains = Qwords))\
                    .values('insert_time','switch_ip','logic_name','agent_ip','mac_cnt','del_flag','proc_flag')
            
            for dKv in lData:
                lDataRet.append({
                    'insert_time':dKv['insert_time'].strftime("%Y-%m-%d %H:%M:%S"),
                    'switch_ip':dKv['switch_ip'],
                    'logic_name':dKv['logic_name'],
                    'agent_ip':dKv['agent_ip'],
                    'mac_cnt':dKv['mac_cnt'],
                    'del_flag':dKv['del_flag'],
                    'proc_flag':dKv['proc_flag'],                
                })
    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))

    return HttpResponse(json.dumps(lDataRet),content_type = 'application/json')

@login_required
@access_logging
def SwDelSwitch(request):
    try:
        if request.method == 'POST':
            SwSwitchInfo.objects.filter(switch_ip = request.POST['switch_ip']).update(del_flag = 1)
            
            
    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))
    return HttpResponse(json.dumps({'ret':1}),content_type = 'application/json')    
    

@login_required
@access_logging
def SwRestoreDelSwitch(request):
    try:
        if request.method == 'POST':
            SwSwitchInfo.objects.filter(switch_ip = request.POST['switch_ip']).update(del_flag = 0)
            
            
    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))
    return HttpResponse(json.dumps({'ret':1}),content_type = 'application/json')   


@login_required
@access_logging
def SwGetRealtimeMac(request):
    try:
        if request.method == 'POST':
            SwSwitchInfo.objects.filter(switch_ip = request.POST['switch_ip']).update(proc_flag = 0)
            
            
    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))
    return HttpResponse(json.dumps({'ret':1}),content_type = 'application/json')
    
@login_required
@access_logging
def SwGetMacData(request,Qwords):
    try:
        lDataRet = []
        if request.method == 'GET':
            if Qwords == 'empty_flag':
                lData = SwMacResult.objects\
                    .values('insert_time','switch_ip','logic_name','agent_ip','interface','mac_addr').order_by('-insert_time')[:200]
            else:
                lData = SwMacResult.objects.filter(Q(switch_ip__contains = Qwords)
                    |Q(interface__contains = Qwords)
                    |Q(mac_addr__contains = Qwords)
                    |Q(logic_name__contains = Qwords))\
                    .values('insert_time','switch_ip','logic_name','agent_ip','interface','mac_addr')
            
            for dKv in lData:
                lDataRet.append({
                    'insert_time':dKv['insert_time'].strftime("%Y-%m-%d %H:%M:%S"),
                    'switch_ip':dKv['switch_ip'],
                    'logic_name':dKv['logic_name'],
                    'agent_ip':dKv['agent_ip'],
                    'interface':dKv['interface'],
                    'mac_addr':dKv['mac_addr'],                    
                })            
    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))
    return HttpResponse(json.dumps(lDataRet),content_type = 'application/json')


@login_required
@access_logging
def SwGetAccLogData(request,SearchFlag,Qwords):
    #获取交换机访问状态信息
    try:
        lDataRet = []
        if request.method == 'GET':
            #search flag = no_ret|proc_done|none
            #none:用于empty_flag/的查询
            #no_ret/proc_done:用于cnt_flag的查询
            #
            #
            
            #cnt_flag_1972-01-01
            if Qwords[:8] == 'cnt_flag':
                QDate = Qwords[9:]
                Qwords = 'cnt_flag'
                
        
            if Qwords == 'empty_flag':

                iSubDay = 1 #log查询范围       
                Stime = (datetime.datetime.now() + datetime.timedelta(-iSubDay)).strftime('%Y-%m-%d')
                (Y1,M1,D1) = map(int,Stime.split('-'))
                
                lData = SwSwitchAccessLog.objects.filter(update_time__gt = datetime.date(Y1,M1,D1)).order_by('-insert_time')[:2000]\
                    .values('update_time','switch_ip','proc_status')
            elif Qwords == 'cnt_flag': #提高前端页面的加载速度，改为insert_time聚合，减少数据量
                lData = SwSwitchAccessLog.objects.filter(proc_status = SearchFlag).filter(tab_date_time__startswith=QDate)\
                    .values('insert_time').annotate(cnt = Count('insert_time'))
            else:
                lData = SwSwitchAccessLog.objects.filter(Q(switch_ip__contains = Qwords))\
                    .values('update_time','switch_ip','proc_status')
            
            if Qwords == 'cnt_flag':
                for dKv in lData:
                    lDataRet.append({
                        'update_time':dKv['insert_time'].strftime("%Y-%m-%d %H:%M:%S"),
                        'timestamp':int( time.mktime(time.strptime(dKv['insert_time'].strftime("%Y-%m-%d %H:%M:%S"),"%Y-%m-%d %H:%M:%S")) ),
                        'cnt':dKv['cnt'],                    
                    })
            else:
                for dKv in lData:
                    lDataRet.append({
                        'update_time':dKv['update_time'].strftime("%Y-%m-%d %H:%M:%S"),
                        'switch_ip':dKv['switch_ip'],
                        'proc_status':dKv['proc_status'],           
                    })
                
    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))
    return HttpResponse(json.dumps(lDataRet),content_type = 'application/json')


@login_required
def SwGetCntData(request):
    try:
        if request.method == 'GET':
            iSwCnt = SwSwitchInfo.objects.filter(del_flag = 0).count()
            iMacCnt = SwMacResult.objects.values('mac_addr').distinct().count()
        
    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))
    return HttpResponse(json.dumps({'sw_cnt':iSwCnt,'mac_cnt':iMacCnt}),content_type = 'application/json')
    
        
        

    