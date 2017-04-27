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

            lTasks = map(lambda x: x.strip(),sTasks.split('\n'))
            lHosts = map(lambda x: x.strip(), sHosts.split('\n'))

            Obj = HostTask(
                name = 'test task',
                timer_flag = sTaskType,
                timer_on = 1,
                timer_crontab = sContab,
                starts_flag=1,
                tab_date_time=GetTimeDayStr_(),
            )
            Obj.save(using='cc')
            host_task_id = Obj.host_task_id
            kwvars['id'] = host_task_id
            # host_task_id_pk = HostTask.objects.using('cc')\
            #     .get(host_task_id = host_task_id)

            for sHost in lHosts:
                if sHost == '':
                    continue
                host_id = HostInfo.objects.using('cc').filter(host = sHost)\
                    .values('host_id')
                if not host_id:
                    continue
                host_id = host_id[0]['host_id']
                # host_id_pk = HostInfo.objects.using('cc').get(host_id = host_id)
                # if not host_id_pk:
                #     continue

                for sTask in lTasks:
                    if sTask == '':
                        continue
                    Obj = HostTaskOperation(
                        host_task_id = host_task_id,
                        host_id = host_id,
                        type = 'raw',
                        arg = sTask,
                        tab_date_time=GetTimeDayStr_(),
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
            .values('host_task_operation_id','host_task_id','host_id'
                    ,'type','arg','prority','started_at','ended_at'
                    ,'result','stdout','stderr')
        lDataRet = []
        for dKv in lData:
            lTmp = HostInfo.objects.using('cc').filter(host_id = dKv['host_id']).values('host')
            if not lTmp:
                continue
            host = lTmp[0]['host']
            lDataRet.append({
                'host_task_operation_id': dKv['host_task_operation_id'],
                'host_task': dKv['host_task_id'],
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
    except BaseException,e:
        Log(gLogFile, 'ERROR', str(e))
    return HttpResponse(json.dumps(lDataRet), content_type='application/json')

@login_required
@access_logging
def sendFile(request):
    try:
        if request.method == "GET":
            kwvars = {
                'request': request,
            }
            return render_to_response('CenterControl/send_file.html'
                                      , kwvars, RequestContext(request))
        elif request.method == "POST":
            kwvars = {
                'ret': 0,
                'id': 'none',
            }

            Obj = CcFileInfo(
                file_name=str(request.FILES['load_file']),
                file_path=request.FILES['load_file'],
            )
            Obj.save(using='cc')
            Log(gLogFile, "INFO", str(myScp(str(Obj.file_path)[3:])))

            sFileName = str(request.FILES['load_file'])
            sMd5sum = Obj.md5sum
            sHosts = request.POST.get('hosts', '')
            sDstPath = request.POST.get('dst_path', '').strip()
            lHosts = map(lambda x:x.strip(),sHosts.split('\n'))
            sTask = json.dumps(
                {
                    "src":sFileName,
                    "dest":sDstPath,
                    "md5":sMd5sum,
                }
            )

            Obj = HostTask(
                name='test task',
                timer_flag=0,
                timer_on=1,
                timer_crontab='',
                starts_flag=1,
                tab_date_time=GetTimeDayStr_(),
            )
            Obj.save(using='cc')
            host_task_id = Obj.host_task_id
            kwvars['id'] = host_task_id
            # host_task_id_pk = HostTask.objects.using('cc') \
            #     .get(host_task_id=host_task_id)

            for sHost in lHosts:
                if sHost == '':
                    continue
                host_id = HostInfo.objects.using('cc').filter(host = sHost)\
                    .values('host_id')
                if not host_id:
                    continue
                host_id = host_id[0]['host_id']
                # host_id_pk = HostInfo.objects.using('cc').get(host_id = host_id)
                # if not host_id_pk:
                #     continue
                Obj = HostTaskOperation(
                    host_task_id=host_task_id,
                    host_id=host_id,
                    type='scp',
                    arg=sTask,
                    tab_date_time=GetTimeDayStr_(),
                )
                Obj.save(using='cc')

            HostTask.objects.using('cc').filter(host_task_id = host_task_id)\
                .update(starts_flag = 0)

    except BaseException,e:
        Log(gLogFile, 'ERROR', str(e))
    return HttpResponseRedirect("/cc/send_result/%s/"%(kwvars["id"]))


'''
####################################
API模块实现
####################################
'''
def judgeApiAuth(request):
    # api请求鉴权
    try:
        sSrcIp = request.META['REMOTE_ADDR']
        dPayload = json.loads(request.body)
        sUsername = dPayload.get('username', 'none')
        sPasswd = dPayload.get('passwd', 'none')
        if sUsername == 'none':
            iCnt = CcApiAuthorityInfo.objects.using("cc")\
                .filter(src_ip=sSrcIp).count()
        else:
            iCnt = CcApiAuthorityInfo.objects.using("cc")\
                .filter(api_username=sUsername,api_passwd=sPasswd).count()
        if iCnt != 0:
            return True
    except BaseException, e:
        Log(gLogFile, 'ERROR', str(e))
    return False


def judgeApiFormat(dPayload):
    #todo：IP合法性校验
    try:
        #type:
        if "type" not in dPayload:
            raise Exception("type not in request.")
        if dPayload["type"] == "process":
            if "cmds" not in dPayload:
                raise Exception("cmd not in request.")
            if "hosts" not in dPayload:
                raise Exception("host not in request.")
            for dHost in dPayload["hosts"]:
                if "host_ip" not in dHost:
                    raise Exception("host_ip not in request.")
                if JudgeIpFormat(dHost["host_ip"]) == False:
                    raise Exception("ip %s format error."%(dHost["host_ip"]))
                if len(dHost) >= 2:
                    for dKey in dHost:
                        if dKey not in ("host_port","host_ip"
                                        ,"host_user","host_passwd"
                                        ,"host_su_user","host_su_passwd"):
                            raise Exception("%s not in request."%(dKey))
        elif dPayload["type"] == "query":
            if "task_id" not in dPayload:
                raise Exception("task_id not in request.")
        else:
            raise Exception("unknown request type %s."%(dPayload["type"]))

    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))
        return (False,str(e))
    return (True,'')


@csrf_exempt
@access_logging
def ccApi(request):
    try:
        dRet = {
            "status": "failed",
            "return": "none",
        }

        if request.method == 'POST':
            # 解析post内容
            dPayload = json.loads(request.body)

            # 将源IP写入dPayload中
            dPayload['src_ip'] = request.META['REMOTE_ADDR']
            sPayload = json.dumps(dPayload)

            # 鉴权
            if judgeApiAuth(request) == False:
                dRet.update({
                    "status":"failed",
                    "return":"authenticate failed.",
                })
            else:
                (judgeRet, retInfo) = judgeApiFormat(dPayload)
                if judgeRet == False:
                    dRet.update({
                        "status": "failed",
                        "return": retInfo,
                    })
                else:
                    if dPayload['type'] == 'process':
                        (sendRet, retInfo) =  sendTaskFromApi(dPayload)
                    elif dPayload['type'] == 'query':
                        (sendRet, retInfo) = queryTaskResultFromApi(dPayload)
                    dRet = retInfo

    except BaseException, e:
        Log(gLogFile, 'ERROR', str(e))
        dRet.update({
            "status": "failed",
            "return": str(e),
        })

    return HttpResponse(json.dumps(dRet), content_type='application/json')


def sendTaskFromApi(dPayload):
    #下发任务
    #
    try:
        dRet = {
            "status": "failed",
            "return": "none",
        }

        lHost = dPayload["hosts"]
        lTask = dPayload["cmds"]

        # 写入任务表，获取到host_task_id
        #
        Obj = HostTask(
            name='api task',
            timer_flag=0, #0表示实时任务
            timer_on=1,
            timer_crontab='',
            starts_flag=1,
            tab_date_time=GetTimeDayStr_(),
        )
        Obj.save(using='cc')
        host_task_id = Obj.host_task_id

        # 处理新增主机信息（合法性校验已在judgeApiFormat中完成），获取到lhost_id
        #此处的逻辑如下：
        #   在host_info表中对host_ip+user+become_user进行唯一性判断，若存在，
        #   则更新账号和密码。
        #
        lHostId = []
        for dHost in lHost:
            if len(dHost) >= 2:
                #新增主机的场景
                #重复的主机-usr-su_usr会update
                iCount = HostInfo.objects.using("cc").filter(host=dHost["host_ip"]
                                        ,user=dHost["host_user"]
                                        ,become_user=dHost["host_su_user"]).count()
                if iCount:
                    host_id = HostInfo.objects.using("cc")\
                        .filter(host=dHost["host_ip"]
                                ,user=dHost["host_user"]
                                ,become_user=dHost["host_su_user"])\
                        .values("host_id")[0]["host_id"]

                    HostInfo.objects.using("cc").filter(host_id=host_id)\
                        .update(port=dHost["host_port"]
                                ,ssh_pass=dHost["host_passwd"]
                                ,become_pass=dHost["host_su_passwd"]
                                ,updated_at=GetTimeNowStr())

                else:
                    Obj = HostInfo(host=dHost["host_ip"]
                                   ,user=dHost["host_user"]
                                   ,become_user=dHost["host_su_user"]
                                   ,port=dHost["host_port"]
                                   ,ssh_pass=dHost["host_passwd"]
                                   ,become_pass=dHost["host_su_passwd"]
                                   ,updated_at=GetTimeNowStr())
                    Obj.save(using="cc")
                    host_id = Obj.host_id
                    Log(gLogFile,"DEBUG","deb 1,%s"%(host_id))
                lHostId.append(host_id)
            else:
                #已有主机IP的场景
                #todo：此处有缺陷，若存在多个相同的host_ip，此处仍然只会随机选择一个使用
                #解决方法：待泽鑫将资源组逻辑完成后再处理。
                host_id = HostInfo.objects.using("cc")\
                    .filter(host=dHost["host_ip"]).values("host_id")
                if host_id:
                    host_id = host_id[0]["host_id"]
                    lHostId.append(host_id)
                else:
                    raise Exception("host %s can not find login method."%(dHost["host_ip"]))

        #插入HostTaskOperation
        for iHostId in lHostId:
            for sTask in lTask:
                if sTask == '':
                    continue
                Obj = HostTaskOperation(
                    host_task_id=host_task_id,
                    host_id=iHostId,
                    type='raw',
                    arg=sTask,
                    tab_date_time=GetTimeDayStr_(),
                )
                Obj.save(using='cc')

        #最后更新下host_task表的完成字段
        HostTask.objects.using('cc').filter(host_task_id=host_task_id).update(starts_flag=0)

        dRet.update({
            "status": "succeeded",
            "return": str(host_task_id),
        })
        return (True,dRet)
    except BaseException, e:
        Log(gLogFile, 'ERROR', str(e))
        dRet.update({
            "status": "failed",
            "return": str(e),
        })
    return (False,dRet)

def queryTaskResultFromApi(dPayload):
    #查询任务
    #
    try:
        dRet = {
            "status": "failed",
            "return": "none",
        }
        sTaskId = dPayload["task_id"]
        lHostIp = dPayload.get("host_ip",[])
        lHostId = []

        qArg = Q()
        qArg.add(Q( **dict(host_task_id=sTaskId) ), Q.AND)

        if len(lHostIp):
            # todo：缺陷同上
            for sHostIp in lHostIp:
                host_id = HostInfo.objects.using("cc") \
                    .filter(host=sHostIp).values("host_id")[0]["host_id"]
                lHostId.append(host_id)
            qArg.add(Q( **dict(host_id__in=lHostId) ), Q.AND)

        iCount = HostTaskOperation.objects.using("cc").filter(qArg)\
            .filter(result=None).count()
        if iCount != 0:
            #processing
            dRet.update({
                "status": "processing",
                "return": "processing task count:%s."%(iCount),
            })
        else:
            #all process done
            lData = HostTaskOperation.objects.using("cc").filter(qArg)\
                .values('host_id', 'arg', 'started_at', 'ended_at'
                        , 'result', 'stdout')

            lDataRet = []
            for dKv in lData:
                lTmp = HostInfo.objects.using('cc').filter(
                    host_id=dKv['host_id']).values('host')
                if not lTmp:
                    Log(gLogFile,"ALARM","hostid:%s not in host_info table."%(dKv["host_id"]))
                    continue
                host = lTmp[0]['host']
                lDataRet.append({
                    'host': host,
                    'arg': dKv['arg'],
                    'started_at': dKv['started_at'].strftime("%Y-%m-%d %H:%M:%S"),
                    'ended_at': dKv['ended_at'].strftime("%Y-%m-%d %H:%M:%S"),
                    'result': dKv['result'],
                    'stdout': dKv['stdout'],
                })
            dRet.update({
                "status": "succeeded",
                "return": lDataRet,
            })
        return (True,dRet)
    except BaseException, e:
        Log(gLogFile, 'ERROR', str(e))
        dRet.update({
            "status": "failed",
            "return": str(e),
        })
    return (False, dRet)