#-*- coding: utf-8 -*-
from django.db import models

# Create your models here.
        
class CcFrameworkHeartbeatInfo(models.Model):
    insert_time = models.DateTimeField()
    tab_date_time = models.DateTimeField()
    dev_ip = models.CharField(max_length=16)
    dev_type = models.CharField(max_length=16)
    recv_cnt = models.IntegerField()
    send_cnt = models.IntegerField()
    log_mq = models.IntegerField()
    netio_recv_mq = models.IntegerField()
    netio_send_mq = models.IntegerField()
    api_recv_mq = models.IntegerField()
    data_proc_recv_mq = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'cc_framework_heartbeat_info'