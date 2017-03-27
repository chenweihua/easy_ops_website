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
    
    
    
    