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
    put_conn_mq_fail_cnt = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'cc_framework_heartbeat_info'


class HostInfo(models.Model):
    host_id = models.IntegerField(primary_key=True)
    host = models.CharField(max_length=32)
    hostname = models.CharField(max_length=32, blank=True)
    port = models.CharField(max_length=5, blank=True)
    user = models.CharField(max_length=64)
    ssh_pass = models.CharField(max_length=64)
    ssh_private_key_file = models.CharField(max_length=255, blank=True)
    become = models.IntegerField()
    become_method = models.CharField(max_length=10, blank=True)
    become_user = models.CharField(max_length=64, blank=True)
    become_pass = models.CharField(max_length=64, blank=True)
    statement = models.CharField(max_length=255, blank=True)
    probe_ip = models.CharField(max_length=32)
    del_flag = models.IntegerField()
    detect_flag = models.IntegerField()
    connect_flag = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'host_info'


class HostTask(models.Model):
    host_task_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    timer_flag = models.IntegerField()
    timer_on = models.IntegerField()
    timer_crontab = models.CharField(max_length=255, blank=True)
    comments = models.CharField(max_length=255, blank=True)
    created_by = models.CharField(max_length=30)
    created_at = models.DateTimeField()
    updated_by = models.CharField(max_length=30, blank=True)
    updated_at = models.DateTimeField()
    starts_flag = models.IntegerField(default=0, editable=False)
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField()
    result = models.CharField(max_length=30, blank=True)
    stdout = models.TextField(blank=True)
    stderr = models.TextField(blank=True)
    del_flag = models.IntegerField(default=0, editable=False)
    class Meta:
        managed = False
        db_table = 'host_task'


class HostTaskOperation(models.Model):
    host_task_operation_id = models.IntegerField(primary_key=True)
    host_task = models.ForeignKey(HostTask)
    host = models.ForeignKey(HostInfo)
    type = models.CharField(max_length=30)
    arg = models.CharField(max_length=255)
    prority = models.IntegerField(default=0, editable=False)
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField()
    result = models.CharField(max_length=30, blank=True)
    stdout = models.TextField(blank=True)
    stderr = models.TextField(blank=True)
    class Meta:
        managed = False
        db_table = 'host_task_operation'