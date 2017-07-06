#-*- coding: utf-8 -*-
from django.shortcuts import render
from django.db.models import Max

# Create your views here.

from util.module_crypto import *
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
                )[:100]

        #取出最新的一条数据
        dKeyTmp = {}

        lDataTmp = []        
        for dKv in lData:
            if '%s_%s'%(dKv['dev_ip'],dKv['dev_type']) in dKeyTmp:
                continue
            #获取到host_task_heartbeat中的任务数目
            lData = HostTaskHeartbeatInfo.objects.using("cc") \
                .filter(dev_ip=dKv['dev_ip'], dev_type=dKv['dev_type'], heartbeat_type="common") \
                .order_by('-heartbeat_time').values("pre_start_cnt")[:1]
            if lData:
                iPreCnt = lData[0]["pre_start_cnt"]
            else:
                iPreCnt = 0

            dKeyTmp['%s_%s'%(dKv['dev_ip'],dKv['dev_type'])] = 1
            dTmp = {
                "pre_start_cnt": iPreCnt,
            }
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

        #host 模块健康度数据
        # .filter(
        #     tab_date_time__range=(
        #         datetime.date(int(sY1), int(sM1), int(sD1)),
        #         datetime.date(int(sY2), int(sM2),
        #                       int(sD2)) + datetime.timedelta(1))
        # ) \
            lData = HostTaskHeartbeatInfo.objects.using("cc") \
            .filter(
                tab_date_time__range=(
                    datetime.date(int(sY1), int(sM1), int(sD1)),
                    datetime.date(int(sY2), int(sM2),int(sD2)) \
                    # + datetime.timedelta(1)
                )
            ) \
            .filter(dev_ip=dev_ip,dev_type=dev_type,heartbeat_type="common") \
            .order_by('heartbeat_time') \
            .values(
            'dev_ip',
            'dev_type',
            "heartbeat_time",
            "pre_start_cnt",
            )
        lDataTmp1 = []
        for dKv in lData:
            dTmp = {}
            for Key in dKv:
                if Key in ('heartbeat_time'):
                    dTmp[Key] = dKv[Key].strftime("%Y-%m-%d %H:%M:%S")
                else:
                    dTmp[Key] = dKv[Key]
            lDataTmp1.append(dTmp)

        dRetTmp = {
            "framework_data": lDataTmp,
            "host_module_data": lDataTmp1,
        }


    except BaseException,e:
        Log(gLogFile,'ERROR',str(e))

    return HttpResponse(json.dumps(dRetTmp),content_type = 'application/json')


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
        sUsername = dPayload.get('username', None)
        sPasswd = dPayload.get('passwd', None)
        if not sUsername:
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
    try:
        if "type" not in dPayload:
            raise Exception("type not in request.")
        if dPayload["type"] == "process" or dPayload["type"] == "process_sync":
            if "cmds" not in dPayload:
                raise Exception("cmd not in request.")
            if "host_ip" not in dPayload and "host_info" not in dPayload:
                raise Exception("host_ip or host_info not in request.")
            if "host_ip" in dPayload:
                if not isinstance(dPayload["host_ip"],list):
                    raise Exception("host_ip must be list.")
                for sIp in dPayload["host_ip"]:
                    if JudgeIpFormat(sIp) == False:
                        raise Exception("ip %s format error."%(sIp))
            if "host_info" in dPayload:
                if not isinstance(dPayload["host_info"],list):
                    raise Exception("host_info must be list.")
                for dHost in dPayload["host_info"]:
                    if "host_ip" not in dHost:
                        raise Exception("host_ip not in request.")
                    if JudgeIpFormat(dHost["host_ip"]) == False:
                        raise Exception(
                            "ip %s format error." % (dHost["host_ip"]))
                    for dKey in dHost:
                        if dKey not in ("host_ip"
                                        , "host_user", "host_passwd"
                                        , "host_su_user", "host_su_passwd"):
                            raise Exception("%s not in request." % (dKey))

        elif dPayload["type"] == "query":
            if "task_id" not in dPayload:
                raise Exception("task_id not in request.")
        elif dPayload["type"] == "add_host":
            if "hosts" not in dPayload:
                raise Exception("host not in request.")
            for dHost in dPayload["hosts"]:
                if "host_ip" not in dHost:
                    raise Exception("host_ip not in request.")
                if JudgeIpFormat(dHost["host_ip"]) == False:
                    raise Exception("ip %s format error."%(dHost["host_ip"]))
                for dKey in dHost:
                    if dKey not in ("host_port", "host_ip"
                                    , "host_user", "host_passwd"
                                    , "host_su_user", "host_su_passwd"):
                        raise Exception("%s not in request." % (dKey))
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
                raise Exception("authenticate failed.")

            (judgeRet, retInfo) = judgeApiFormat(dPayload)
            if judgeRet == False:
                raise Exception(retInfo)

            if dPayload["type"] == "process" or dPayload["type"] == "process_sync":
                (sendRet, retInfo) =  sendTaskFromApi(dPayload)
            elif dPayload["type"] == "query":
                (sendRet, retInfo) = queryTaskResultFromApi(dPayload)
            elif dPayload["type"] == "add_host":
                (sendRet, retInfo) = addHostFromApi(dPayload)
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

        # lHost = dPayload["host_ip"]
        lHost = dPayload.get("host_ip",dPayload.get("host_info",[]))
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
        sUserName = dPayload.get('username', None)
        if "host_info" in dPayload:
            (bRet,data) = utilHostOpt(sOpt="add",
                        iHostGroupId=__getUserOwnHostGroupId(sUserName),
                        lHost=lHost,sUserName=sUserName)
        elif "host_ip" in dPayload:
            (bRet, data) = utilHostOpt(sOpt="sel",
                        iHostGroupId=__getUserOwnHostGroupId(sUserName),
                        lHost=lHost, sUserName=sUserName)

        if not bRet:
            raise Exception(str(data))
        lHostId = data

        # lHostId = []
        # for sHostIp in lHost:
        #     #已有主机IP的场景
        #     #解决方法：待泽鑫将资源组逻辑完成后再处理。
        #     host_id = HostInfo.objects.using("cc")\
        #         .filter(host=sHostIp).values("host_id")
        #     if host_id:
        #         host_id = host_id[0]["host_id"]
        #         lHostId.append(host_id)
        #     else:
        #         raise Exception("host %s can not find login method."%(sHostIp))

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

        sType = dPayload["type"]
        if sType == "process":
            dRet.update({
                "status": "succeeded",
                "return": str(host_task_id),
            })
            return (True,dRet)
        elif sType == "process_sync":
            iProcTimes = 120
            while iProcTimes != 0:
                (bRet,dRetData) = __queryTaskResultFromId(str(host_task_id))
                if dRetData["status"] in ("succeeded","failed"):
                    dRet.update(dRetData)
                    break
                elif dRetData["status"] == "processing":
                    iProcTimes -= 1
                    time.sleep(1)
            if iProcTimes == 0:
                raise Exception("process timeout.")
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


        #根据host_task表获取整个任务的执行状态
        lData = HostTask.objects.using("cc").filter(host_task_id=sTaskId)\
            .values("started_at","ended_at","result","stderr")
        sResult = lData[0]["result"]
        if sResult == "error":
            raise Exception(lData[0]["stderr"])

        #没有无法连通的主机
        qArg = Q()
        qArg.add(Q( **dict(host_task_id=sTaskId) ), Q.AND)


        if len(lHostIp):
            sUserName = dPayload.get('username', None)
            (bRet, data) = utilHostOpt(sOpt="sel",
                           iHostGroupId=__getUserOwnHostGroupId(sUserName),
                           lHost=lHostIp,sUserName=sUserName)
            if not bRet:
                raise Exception(str(data))
            lHostId = data
            qArg.add(Q(**dict(host_id__in=lHostId)), Q.AND)

        # lHostId = []
        # if len(lHostIp):
        #     for sHostIp in lHostIp:
        #         host_id = HostInfo.objects.using("cc") \
        #             .filter(host=sHostIp).values("host_id")[0]["host_id"]
        #         lHostId.append(host_id)
        #     qArg.add(Q( **dict(host_id__in=lHostId) ), Q.AND)

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
                lTmp = HostInfo.objects.using('cc')\
                    .filter( host_id=dKv['host_id']).values('host')
                if not lTmp:
                    Log(gLogFile,"ALARM","hostid:%s not in host_info table."\
                        %(dKv["host_id"]))
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

def __queryTaskResultFromId(sTaskId):
    try:
        dRet = {
            "status": "failed",
            "return": "none",
        }

        # 根据host_task表获取整个任务的执行状态
        lData = HostTask.objects.using("cc").filter(host_task_id=sTaskId) \
            .values("started_at", "ended_at", "result", "stderr")
        sResult = lData[0]["result"]
        if sResult == "error":
            raise Exception(lData[0]["stderr"])

        # 没有无法连通的主机
        qArg = Q()
        qArg.add(Q(**dict(host_task_id=sTaskId)), Q.AND)

        iCount = HostTaskOperation.objects.using("cc").filter(qArg) \
            .filter(result=None).count()
        if iCount != 0:
            # processing
            dRet.update({
                "status": "processing",
                "return": "processing task count:%s." % (iCount),
            })
        else:
            # all process done
            lData = HostTaskOperation.objects.using("cc").filter(qArg) \
                .values('host_id', 'arg', 'started_at', 'ended_at'
                        , 'result', 'stdout', 'stderr')

            lDataRet = []
            for dKv in lData:
                lTmp = HostInfo.objects.using('cc') \
                    .filter(host_id=dKv['host_id']).values('host')
                if not lTmp:
                    Log(gLogFile, "ALARM", "hostid:%s not in host_info table." \
                        % (dKv["host_id"]))
                    continue
                host = lTmp[0]['host']
                lDataRet.append({
                    'host': host,
                    'arg': dKv['arg'],
                    'started_at': dKv['started_at'].strftime(
                        "%Y-%m-%d %H:%M:%S"),
                    'ended_at': dKv['ended_at'].strftime("%Y-%m-%d %H:%M:%S"),
                    'result': dKv['result'],
                    'stdout': dKv['stdout'],
                    'stderr': dKv['stderr'],
                })
            dRet.update({
                "status": "succeeded",
                "return": lDataRet,
            })
        return (True, dRet)
    except BaseException,e:
        Log(gLogFile,"ERROR",str(e))
        dRet.update({
            "status": "failed",
            "return": str(e),
        })
    return (False, dRet)


def addHostFromApi(dPayload):
    try:
        dRet = {
            "status": "failed",
            "return": "none",
        }
        lHost = dPayload["hosts"]

        sUserName = dPayload.get('username', None)
        (bRet, data) = utilHostOpt(sOpt="add",
                       iHostGroupId=__getUserOwnHostGroupId(sUserName),
                       lHost=lHost,sUserName=sUserName)
        if not bRet:
            raise Exception(str(data))
        # for dHost in lHost:
        #     #新增主机的场景
        #     #重复的主机-usr-su_usr会update
        #     iCount = HostInfo.objects.using("cc").filter(host=dHost["host_ip"]
        #                             ,user=dHost["host_user"]
        #                             ,become_user=dHost["host_su_user"]).count()
        #     if iCount:
        #         host_id = HostInfo.objects.using("cc")\
        #             .filter(host=dHost["host_ip"]
        #                     ,user=dHost["host_user"]
        #                     ,become_user=dHost["host_su_user"])\
        #             .values("host_id")[0]["host_id"]
        #
        #         HostInfo.objects.using("cc").filter(host_id=host_id)\
        #             .update(port=dHost["host_port"]
        #                     ,ssh_pass=dHost["host_passwd"]
        #                     ,become_pass=dHost["host_su_passwd"]
        #                     ,updated_at=GetTimeNowStr())
        #     else:
        #         Obj = HostInfo(host=dHost["host_ip"]
        #                        ,user=dHost["host_user"]
        #                        ,become_user=dHost["host_su_user"]
        #                        ,port=dHost["host_port"]
        #                        ,ssh_pass=dHost["host_passwd"]
        #                        ,become_pass=dHost["host_su_passwd"]
        #                        ,updated_at=GetTimeNowStr())
        #         Obj.save(using="cc")
        dRet.update({
            "status": "succeeded",
            "return": "add host succeeded.",
        })
        return (True, dRet)
    except BaseException, e:
        Log(gLogFile, 'ERROR', str(e))
        dRet.update({
            "status": "failed",
            "return": str(e),
        })
    return (False, dRet)


@csrf_exempt
@access_logging
def sendFileFromApi(request):
    try:
        dRet = {
            "status": "failed",
            "return": "none",
        }

        if request.method != "POST":
            raise Exception("request method %s error."%(request.method))

        # 鉴权也要重新搞。。
        sSrcIp = request.META['REMOTE_ADDR']
        sUsername = request.POST.get('username', 'none')
        sPasswd = request.POST.get('passwd', 'none')
        if sUsername == 'none':
            iCnt = CcApiAuthorityInfo.objects.using("cc")\
                .filter(src_ip=sSrcIp).count()
        else:
            iCnt = CcApiAuthorityInfo.objects.using("cc")\
                .filter(api_username=sUsername,api_passwd=sPasswd).count()
        if iCnt == 0:
            raise Exception("authenticate failed.")

        # 不能复用judgeApiFormat()，只能自己怼。
        sType = request.POST.get("type","")
        if sType != "push_file" and sType != "push_file_sync":
            raise Exception("unknown request type %s."%(sType))

        sDstPath = request.POST.get("dst_path","")
        if sDstPath == "":
            raise Exception("dst_path cannot be empty.")

        if "host_ip" in request.POST:
            lHosts = request.POST.getlist("host_ip")
            for sHostIp in lHosts:
                if JudgeIpFormat(sHostIp) == False:
                    raise Exception("ip %s format error." % (sHostIp))
        elif "host_info" in request.POST: #支持实时传入主机信息（包括用户名、密码等）
            sHosts = request.POST.get("host_info","[]")
            try:
                Log(gLogFile,"DEBUG",sHosts)
                lHosts = json.loads(sHosts)
            except BaseException,e:
                raise Exception("host_info format error.")

            for dHost in lHosts:
                if "host_ip" not in dHost:
                    raise Exception("host_ip not in request.")
                if JudgeIpFormat(dHost["host_ip"]) == False:
                    raise Exception("ip %s format error." % (dHost["host_ip"]))
                for dKey in dHost:
                    if dKey not in ("host_ip", "host_user", "host_passwd",
                                    "host_su_user", "host_su_passwd"):
                        raise Exception("%s not in request." % (dKey))

        # 文件处理
        Obj = CcFileInfo(
            file_name=str(request.FILES['load_file']),
            file_path=request.FILES['load_file'],
        )
        Obj.save(using='cc')
        Log(gLogFile, "INFO", str(myScp(str(Obj.file_path)[3:])))
        sFileName = str(request.FILES['load_file'])
        sMd5sum = Obj.md5sum

        # 下发到中控平台
        sTask = json.dumps({
                "src": sFileName,
                "dest": sDstPath,
                "md5": sMd5sum,
            })

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

        if "host_info" in request.POST:
            (bRet, data) = utilHostOpt(sOpt="add",
                           iHostGroupId=__getUserOwnHostGroupId(sUsername),
                           lHost=lHosts, sUserName=sUsername)
        elif "host_ip" in request.POST:
            (bRet, data) = utilHostOpt(sOpt="sel",
                           iHostGroupId=__getUserOwnHostGroupId(sUsername),
                           lHost=lHosts,sUserName=sUsername)
        if not bRet:
            raise Exception(str(data))
        lHostId = data
        for host_id in lHostId:
            Obj = HostTaskOperation(
                host_task_id=host_task_id,
                host_id=host_id,
                type='scp',
                arg=sTask,
                tab_date_time=GetTimeDayStr_(),
            )
            Obj.save(using='cc')

        # for sHost in lHosts:
        #     host_id = HostInfo.objects.using('cc').filter(host=sHost) \
        #         .values('host_id')
        #     if not host_id:
        #         raise Exception("host %s can not find login method."%(sHostIp))
        #     host_id = host_id[0]['host_id']
        #
        #     Obj = HostTaskOperation(
        #         host_task_id=host_task_id,
        #         host_id=host_id,
        #         type='scp',
        #         arg=sTask,
        #         tab_date_time=GetTimeDayStr_(),
        #     )
        #     Obj.save(using='cc')

        HostTask.objects.using('cc').filter(host_task_id=host_task_id) \
            .update(starts_flag=0)

        if sType == "push_file":
            dRet.update({
                "status": "succeeded",
                "return": str(host_task_id),
            })
        elif sType == "push_file_sync":
            iProcTimes = 120
            while iProcTimes != 0:
                (bRet, dRetData) = __queryTaskResultFromId(str(host_task_id))
                if dRetData["status"] in ("succeeded", "failed"):
                    dRet.update(dRetData)
                    break
                elif dRetData["status"] == "processing":
                    iProcTimes -= 1
                    time.sleep(1)
            if iProcTimes == 0:
                raise Exception("process timeout.")
    except BaseException,e:
        Log(gLogFile,"ERROR",str(e))
        dRet.update({
            "status": "failed",
            "return": str(e),
        })
    return HttpResponse(json.dumps(dRet), content_type='application/json')

'''
####################################
权限模块公共函数
####################################
所有权限相关操作都抽出在这部分实现
权限管理模块实施后的数据写入规则：
a、同一主机组中的主机IP/name唯一，新增主机时，若主机IP相同，则更新其他字段；
b、主机组中默认设置0号组，包含所有的主机信息该组用于执行自动化数据采集等任务。
另外，在API调用中不存在的主机可从其中选择；

'''
def __getUserOwnHostGroupId(sUserName=None):
    try:
        user_id = CcApiAuthorityInfo.objects.using("cc")\
                      .filter(api_username=sUserName).values("id")
        if not user_id:
            raise Exception("user not exist.")
        user_id = user_id
        host_group_info_id = UserAndHostGroupInfoMap.objects.using("cc")\
            .filter(user_id=user_id,is_owner=1).values("host_group_info_id")
        if not host_group_info_id:
            raise Exception("hsot group id not exist.")
        host_group_info_id = host_group_info_id[0]["host_group_info_id"]
        return host_group_info_id
    except BaseException,e:
        Log(gLogFile,"ERROR",str(e))
    return None



def __judgePermission(iPermission,sOpt):
    try:
        if sOpt == "add":
            iVal = int("0010",2)
        elif sOpt == "del":
            iVal = int("0100",2)
        elif sOpt == "sel":
            iVal = int("0001", 2)
        elif sOpt == "mod":
            iVal = int("1000", 2)
        if iPermission & iVal == iVal:
            return True
    except BaseException,e:
        Log(gLogFile,"ERROR",str(e))
    return False

def utilHostOpt(sOpt,sUserName=None,iHostGroupId=None,lHost=None):
    #主机信息的增、删、查、改  opt --> add|del|sel|mod
    #user -> host group -> host
    #
    try:
        if not sUserName:
            raise Exception("user name is none.")
        if not iHostGroupId:
            raise Exception("host group id is none.")

        #验证是否有权限
        user_id = CcApiAuthorityInfo.objects.using("cc") \
                      .filter(api_username=sUserName).values("id")
        if not user_id:
            raise Exception("user not exist.")

        permission = UserAndHostGroupInfoMap.objects.using("cc") \
            .filter(user_id=user_id, host_group_info_id=iHostGroupId) \
            .values("permission")[0]["permission"]
        if not __judgePermission(iPermission=permission, sOpt=sOpt):
            raise Exception("user %s %s permission denied." % (sUserName, sOpt))

        ret = None
        if sOpt == "add":
            #场景：api & 前端
            if not lHost:
                raise Exception("host list is none.")
            ret = []
            #检验，host, host_user, host_su_user相同的，抛出异常
            lHostId = HostInfoAndHostGroupInfoMap.objects.using("cc") \
                .filter(host_group_info_id=iHostGroupId).values("host_id")
            for dHostInfo in lHost:
                # 获取加密后的host信息
                (sEncryptoUser,sEncryptoPasswd) = encrypt(
                    dHostInfo["host_ip"],
                    dHostInfo["host_user"],
                    dHostInfo["host_passwd"]
                )
                (sEncryptoSuUser, sEncryptoSuPasswd) = encrypt(
                    dHostInfo["host_ip"],
                    dHostInfo["host_su_user"],
                    dHostInfo["host_su_passwd"]
                )

                if "host_port" not in dHostInfo: #中间件场景下，用户不需要输入端口
                    dHostInfo["host_port"] = 22

                host_id = HostInfo.objects.using("cc")\
                    .filter(host_id__in=lHostId,
                            host=dHostInfo["host_ip"],
                            # user=dHostInfo["host_user"],
                            # become_user=dHostInfo["host_su_user"]
                            user=sEncryptoUser,
                            become_user=sEncryptoSuUser
                            ).values("host_id")
                if host_id:
                    #有相同的，update
                    HostInfo.objects.using("cc")\
                        .filter(host_id__in=lHostId,
                                host=dHostInfo["host_ip"],
                                # user=dHostInfo["host_user"],
                                # become_user=dHostInfo["host_su_user"])\
                                user=sEncryptoUser,
                                become_user=sEncryptoSuUser)\
                        .update(
                                # ssh_pass=dHostInfo["host_passwd"],
                                # become_pass=dHostInfo["host_su_passwd"],
                                ssh_pass=sEncryptoPasswd,
                                become_pass=sEncryptoSuPasswd,
                                port=dHostInfo["host_port"],
                                cache_flag=0,
                                updated_at=GetTimeNowStr()) #下发主机缓存

                    #对于原来密码就错误的场景，更新完之后将detect_flag置为0
                    HostInfo.objects.using("cc") \
                        .filter(host_id__in=lHostId,
                                host=dHostInfo["host_ip"],
                                # user=dHostInfo["host_user"],
                                # become_user=dHostInfo["host_su_user"])\
                                user=sEncryptoUser,
                                become_user=sEncryptoSuUser,
                                connect_flag=0) \
                        .update(detect_flag=0)

                    ret.append(host_id[0]["host_id"])
                else:
                    # 检索下host_info中（不区分群组）是否存在该IP，
                    # 若存在，则detect_flag、connect_flag复用
                    probe_ip = HostInfo.objects.using("cc").filter(
                        host=dHostInfo["host_ip"],
                        detect_flag=1, connect_flag=1,
                    ).values("probe_ip")[:1]
                    if probe_ip:
                        probe_ip = probe_ip[0]["probe_ip"]
                        detect_flag = 1
                        connect_flag = 1
                    else:
                        probe_ip = "0.0.0.0"
                        detect_flag = 0
                        connect_flag = 0

                    Obj = HostInfo(
                        host=dHostInfo["host_ip"],
                        port=dHostInfo["host_port"],
                        # user=dHostInfo["host_user"],
                        # become_user=dHostInfo["host_su_user"],
                        # ssh_pass=dHostInfo["host_passwd"],
                        # become_pass=dHostInfo["host_su_passwd"],
                        user=sEncryptoUser,
                        become_user=sEncryptoSuUser,
                        ssh_pass=sEncryptoPasswd,
                        become_pass=sEncryptoSuPasswd,
                        cache_flag=0,
                        detect_flag=detect_flag,
                        connect_flag=connect_flag,
                        probe_ip=probe_ip
                    )
                    Obj.save(using="cc")
                    host_id = Obj.host_id
                    Obj = HostInfoAndHostGroupInfoMap(
                        host_id=host_id,
                        host_group_info_id=iHostGroupId,
                    )
                    Obj.save(using="cc")
                    ret.append(host_id)

        elif sOpt == "del":
            # 场景：api & 前端 暂时先不实现
            if not lHost:
                raise Exception("host list is none.")
        elif sOpt == "sel":
            # 场景：api & 前端
            #这里的lhost结构与add的不同，只是ip的列表
            ret = []
            lHostId = HostInfoAndHostGroupInfoMap.objects.using("cc") \
                .filter(host_group_info_id=iHostGroupId).values("host_id")
            lNoConHosts = []
            if lHost is None:
                pass #预留
            else:
                for sHostIp in lHost:
                    # 检索提供的IPlist是否在自己的组里
                    host_id = HostInfo.objects.using("cc")\
                        .filter(host_id__in=lHostId,host=sHostIp,del_flag=0)\
                        .values("host_id")
                    if host_id:
                        ret.append(host_id[0]["host_id"])
                    else:
                        # 若不在，使用默认分组的IP
                        # iDeafultHostGroup = 1
                        lHostIdDef = HostInfoAndHostGroupInfoMap.objects \
                            .using("cc") \
                            .filter(host_group_info_id=1).values("host_id")

                        host_id = HostInfo.objects.using("cc")\
                            .filter(host_id__in=lHostIdDef,
                                    host=sHostIp,del_flag=0).values("host_id")
                        if host_id:
                            ret.append(host_id[0]["host_id"])
                        else:
                            lNoConHosts.append(sHostIp)
                            # raise Exception("host %s cannot find login method."\
                            #                 % (sHostIp))
            if len(lNoConHosts) != 0:
                raise Exception("unreachable_hosts:%s"%(','.join(lNoConHosts)))

        elif sOpt == "mod":
            # 场景：api & 前端 暂时先不实现
            if not lHost:
                raise Exception("host list is none.")
        else:
            raise Exception("host opt type error.")
    except BaseException,e:
        Log(gLogFile, 'ERROR', str(e))
        return False, str(e)
    return True, ret


def utilGroupOpt(sOpt,sUserName=None,iHostGroupId=None):
    # 主机组信息的增、删、查、改  opt --> add|del|sel|mod
    #
    #
    try:
        ret = None
        if sOpt == "add":
            # 场景：前端
            pass
        elif sOpt == "del":
            # 场景：前端
            pass
        elif sOpt == "sel":
            # 场景：前端
            pass
        elif sOpt == "mod":
            # 场景：前端
            pass
        else:
            raise Exception("host group opt type error.")
    except BaseException,e:
        Log(gLogFile, 'ERROR', str(e))
        return False, str(e)
    return True, ret


def hostInfo(request):
    kwvars = {
        'request': request,
    }
    return render_to_response('CenterControl/host_info.html' \
                              , kwvars, RequestContext(request))

def getHostStatInfo(request):
    try:
        lData = HostCoverageStat.objects.using("cc").values(
            "insert_time",
            "all_host_cnt",
            "conn_host_cnt",
            "unconn_host_cnt",
            "timeout_host_cnt",
            "refused_host_cnt",
            "denied_host_cnt",
            "closed_by_remote_host_cnt",
            "other_host_cnt",
        ).order_by("insert_time")[:30]

        lDataTmp = []
        for dKv in lData:
            dTmp = {}
            for Key in dKv:
                if Key in ("insert_time"):
                    if dKv[Key] is None:
                        dTmp[Key] = "0000-00-00 00:00:00"
                    else:
                        dTmp[Key] = dKv[Key].strftime("%Y-%m-%d %H:%M:%S")
                else:
                    dTmp[Key] = dKv[Key]
            lDataTmp.append(dTmp)

    except BaseException as e:
        Log(gLogFile,"ERROR",str(e))
    # return HttpResponse(json.dumps(dRet),content_type = 'application/json')
    return HttpResponse(json.dumps(lDataTmp),content_type = 'application/json')


def getHostInfo(request):
    try:
        kwvars = {}
        sIp = request.POST["query_ip"]
        if sIp == "get_all":
            lData = HostInfo.objects.using("cc").values(
                "created_at",
                "updated_at",
                "host",
                "user",
                "become_user",
                "probe_ip",
                "del_flag",
                "detect_flag",
                "connect_flag",
                "status",
                "ssh_pass",
                "become_pass",
            )[:50]

        else:
            lData = HostInfo.objects.using("cc").filter(
                host__startswith=sIp).values(
                "created_at",
                "updated_at",
                "host",
                "user",
                "become_user",
                "probe_ip",
                "del_flag",
                "detect_flag",
                "connect_flag",
                "status",
                "ssh_pass",
                "become_pass",
            )[:50]

        lDataTmp = []
        for dKv in lData:
            dTmp = {}
            for Key in dKv:
                if Key in ('created_at',"updated_at"):
                    if dKv[Key] is None:
                        dTmp[Key] = "0000-00-00 00:00:00"
                    else:
                        dTmp[Key] = dKv[Key].strftime("%Y-%m-%d %H:%M:%S")
                else:
                    dTmp[Key] = dKv[Key]
            if len(dTmp["user"]) == 32 and len(dTmp["ssh_pass"]) == 32 \
                    and len(dTmp["become_user"]) == 32 and len(dTmp["become_pass"]) == 32:
                (dTmp["user"],sDecryptPasswd) \
                    = decrypt(dTmp["host"],dTmp["user"],dTmp["ssh_pass"])
                (dTmp["become_user"],sDecryptSuPasswd) \
                    = decrypt(dTmp["host"],dTmp["become_user"],dTmp["become_pass"])

            lDataTmp.append(dTmp)
        kwvars.update({
            'ldata': lDataTmp,
        })
    except BaseException, e:
        Log(gLogFile, "ERROR", str(e))

    return HttpResponse(json.dumps(kwvars),content_type = 'application/json')
