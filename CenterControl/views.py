#-*- coding: utf-8 -*-
from django.shortcuts import render

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
        lData = CcFrameworkHeartbeatInfo.objects.using('cc')\
            .filter(tab_date_time__startswith=datetime.date.today())\
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
                if Key in ('insert_time','tab_date_time'):
                    dTmp[Key] = dKv[Key].strftime("%Y-%m-%d %H:%M:%S")
                else:
                    dTmp[Key] = dKv[Key]
            lDataTmp.append(dTmp)
                
        kwvars = lDataTmp
        # Log(gLogFile,'DEBUG',str(kwvars))
        
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
            )
            Obj.save(using='cc')
            host_task_id = Obj.host_task_id
            kwvars['id'] = host_task_id
            host_task_id_pk = HostTask.objects.using('cc')\
                .get(host_task_id = host_task_id)

            for sHost in lHosts:
                host_id = HostInfo.objects.using('cc').filter(host = sHost)\
                    .values('host_id')
                if not host_id:
                    continue

                host_id_pk = HostInfo.objects.using('cc').get(host_id = host_id)
                if not host_id_pk:
                    continue

                for sTask in lTasks:
                    Obj = HostTaskOperation(
                        host_task = host_task_id_pk,
                        host = host_id_pk,
                        type = 'raw',
                        arg = sTask,
                    )
                    Obj.save(using='cc')


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