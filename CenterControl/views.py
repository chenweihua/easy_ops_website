#-*- coding: utf-8 -*-
from django.shortcuts import render
from django.db.models import Max

# Create your views here.


from util.utilfunc import *
from util.utilvar import *
from util.utilmodels import *

from CenterControl.models import *
from CenterControl.forms import *

from UserManage.views.permission import PermissionVerify
from UserManage.models import User

reload(sys)
sys.setdefaultencoding('utf-8')

#----------功能入口函数----------


@login_required
@access_logging
@PermissionVerify()
def frameworkHealth(request):
    kwvars = {
        'request':request,
    }
    return render_to_response('CenterControl/framework_health.html'\
        ,kwvars,RequestContext(request))



def frameworkHealthGetData(request):
    try:
        #select max(insert_time),dev_ip,dev_type from cc_framework_heartbeat_info
        # group by dev_ip,dev_type;
        lData = CcFrameworkHeartbeatInfo.objects.using('cc')\
            .filter(tab_date_time__startswith=datetime.date.today())\
            .order_by('-insert_time')\
            .values(
                'insert_time',
                'tab_date_time',
                'dev_ip',
                'dev_type',
                'recv_cnt',
                'send_cnt',
                'log_mq',
                'netio_recv_mq',
                'netio_send_mq',
                'api_recv_mq',
                'data_proc_recv_mq',
                'put_conn_mq_fail_cnt'
                )

        #取出最新的一条数据
        dKeyTmp = {}

        lDataTmp = []        
        for dKv in lData:
            if '%s_%s'%(dKv['dev_ip'],dKv['dev_type']) in dKeyTmp:
                continue
            dKeyTmp['%s_%s'%(dKv['dev_ip'],dKv['dev_type'])] = 1
            dTmp = {}
            for Key in dKv:
                if Key in ('insert_time','tab_date_time'):
                    dTmp[Key] = dKv[Key].strftime("%Y-%m-%d %H:%M:%S")
                else:
                    dTmp[Key] = dKv[Key]
            lDataTmp.append(dTmp)
    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))
        
    return HttpResponse(json.dumps(lDataTmp),content_type = 'application/json')


def frameworkHealthGetTheData(request):
    #根据选择的日期查询健康度信息
    #
    #
    #todo
    try:
        sSDate = request.POST.get('start_data','')
        sEDate = request.POST.get('end_data','')
        dev_ip = request.POST.get('dev_ip','')
        dev_type = request.POST.get('dev_type','')
        (sY1, sM1, sD1) = sSDate.split('-')
        (sY2, sM2, sD2) = sEDate.split('-')
        #
        lData = CcFrameworkHeartbeatInfo.objects.using('cc')\
            .filter(
            tab_date_time__range=(
                datetime.date(int(sY1), int(sM1), int(sD1)),
                datetime.date(int(sY2), int(sM2), int(sD2)))
            ).filter(dev_ip=dev_ip).filter(dev_type=dev_type)\
            .order_by('insert_time')\
            .values(
                'insert_time',
                'tab_date_time',
                'dev_ip',
                'dev_type',
                'recv_cnt',
                'send_cnt',
                'log_mq',
                'netio_recv_mq',
                'netio_send_mq',
                'api_recv_mq',
                'data_proc_recv_mq',
                'put_conn_mq_fail_cnt'
                )
        lDataTmp = []
        for dKv in lData:
            dTmp = {}
            for Key in dKv:
                if Key in ('insert_time', 'tab_date_time'):
                    dTmp[Key] = dKv[Key].strftime("%Y-%m-%d %H:%M:%S")
                else:
                    dTmp[Key] = dKv[Key]
            lDataTmp.append(dTmp)

    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))

    return HttpResponse(json.dumps(lDataTmp),content_type = 'application/json')


@login_required
@access_logging
def sendTask(request):
    if request.method == 'GET':
        kwvars = {
            'request':request,
        }
        return render_to_response('CenterControl/send_task.html'\
            ,kwvars,RequestContext(request))
    elif request.method == 'POST':
        try:
            kwvars = {
                'ret':0,
                'id':'none',
            }

            sTasks = request.POST.get('id_tasks','')
            sHosts = request.POST.get('id_hosts','')
            sTaskType = request.POST.get('id_task_type','')
            sContab = request.POST.get('id_contab_text','')

            lTasks = sTasks.split('\n')
            lHosts = sHosts.split('\n')

            Obj = HostTask(
                name = 'test task',
                timer_flag = sTaskType,
                timer_on = 1,
                timer_crontab = sContab,
                starts_flag=1,
            )
            Obj.save(using='cc')
            host_task_id = Obj.host_task_id
            kwvars['id'] = host_task_id
            host_task_id_pk = HostTask.objects.using('cc')\
                .get(host_task_id = host_task_id)

            for sHost in lHosts:
                if sHost == '':
                    continue
                host_id = HostInfo.objects.using('cc').filter(host = sHost)\
                    .values('host_id')
                if not host_id:
                    continue

                host_id_pk = HostInfo.objects.using('cc').get(host_id = host_id)
                if not host_id_pk:
                    continue

                for sTask in lTasks:
                    if sTask == '':
                        continue
                    Obj = HostTaskOperation(
                        host_task = host_task_id_pk,
                        host = host_id_pk,
                        type = 'raw',
                        arg = sTask,
                    )
                    Obj.save(using='cc')

            #替老王擦屁股:)
            HostTask.objects.using('cc').filter(host_task_id = host_task_id)\
                .update(starts_flag = 0)

        except BaseException,e:
            Log(gLogFile,'ERROR',str(e))
        return HttpResponse(json.dumps(kwvars), content_type='application/json')


@login_required
@access_logging
def taskResult(request,ID):
    kwvars = {
        'request': request,
        'task_id': ID,
    }
    return render_to_response('CenterControl/task_result.html' \
                              , kwvars, RequestContext(request))


@login_required
@access_logging
def getTaskResult(request,ID):
    try:
        lData = HostTaskOperation.objects.using('cc').filter(host_task_id = ID)\
            .values('host_task_operation_id','host_task','host'
                    ,'type','arg','prority','started_at','ended_at'
                    ,'result','stdout','stderr')
        lDataRet = []
        for dKv in lData:
            lTmp = HostInfo.objects.using('cc').filter(host_id = dKv['host']).values('host')
            if not lTmp:
                continue
            host = lTmp[0]['host']
            lDataRet.append({
                'host_task_operation_id': dKv['host_task_operation_id'],
                'host_task': dKv['host_task'],
                'host': host,
                'type': dKv['type'],
                'arg': dKv['arg'],
                'prority': dKv['prority'],
                'started_at': dKv['started_at'].strftime("%Y-%m-%d %H:%M:%S"),
                'ended_at': dKv['ended_at'].strftime("%Y-%m-%d %H:%M:%S"),
                'result': dKv['result'],
                'stdout': dKv['stdout'],
                'stderr': dKv['stderr'],
            })
        Log(gLogFile,'DEBUG',str(lDataRet))
    except BaseException,e:
        Log(gLogFile, 'ERROR', str(e))
    return HttpResponse(json.dumps(lDataRet), content_type='application/json')