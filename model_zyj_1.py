# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.
from __future__ import unicode_literals

from django.db import models

class CcApiAuthorityInfo(models.Model):
    id = models.IntegerField(primary_key=True)
    insert_time = models.DateTimeField()
    src_ip = models.CharField(max_length=32)
    api_username = models.CharField(max_length=32)
    api_passwd = models.CharField(max_length=32)
    class Meta:
        managed = False
        db_table = 'cc_api_authority_info'

class CcDevInfo(models.Model):
    insert_time = models.DateTimeField()
    dev_ip = models.CharField(max_length=16)
    dev_type = models.CharField(max_length=13)
    using_flag = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'cc_dev_info'

class CcFileInfo(models.Model):
    insert_time = models.DateTimeField()
    id = models.IntegerField(primary_key=True)
    file_name = models.CharField(max_length=255)
    md5sum = models.CharField(max_length=36)
    file_path = models.TextField(blank=True)
    class Meta:
        managed = False
        db_table = 'cc_file_info'

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

class HostGroupInfo(models.Model):
    host_group_info_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    del_flag = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'host_group_info'

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
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'host_info'

class HostInfoAndHostGroupInfoMap(models.Model):
    host_info_and_host_group_info_map_id = models.IntegerField(primary_key=True)
    host_id = models.IntegerField()
    host_group_info_id = models.IntegerField()
    del_flag = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'host_info_and_host_group_info_map'

class HostTask(models.Model):
    host_task_id = models.IntegerField(primary_key=True)
    type = models.CharField(max_length=11, blank=True)
    name = models.CharField(max_length=255)
    timer_flag = models.IntegerField()
    timer_on = models.IntegerField()
    timer_crontab = models.CharField(max_length=255, blank=True)
    comments = models.CharField(max_length=255, blank=True)
    created_by = models.CharField(max_length=30)
    created_at = models.DateTimeField()
    updated_by = models.CharField(max_length=30, blank=True)
    updated_at = models.DateTimeField()
    starts_flag = models.IntegerField()
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField()
    result = models.CharField(max_length=30, blank=True)
    stdout = models.TextField(blank=True)
    stderr = models.TextField(blank=True)
    del_flag = models.IntegerField()
    tab_date_time = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'host_task'

class HostTaskOperation(models.Model):
    host_task_operation_id = models.IntegerField(primary_key=True)
    host_task_id = models.IntegerField()
    host_id = models.IntegerField()
    type = models.CharField(max_length=30)
    arg = models.CharField(max_length=255)
    prority = models.IntegerField()
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField()
    result = models.CharField(max_length=30, blank=True)
    stdout = models.TextField(blank=True)
    stderr = models.TextField(blank=True)
    tab_date_time = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'host_task_operation'

class UserAndHostGroupInfoMap(models.Model):
    user_and_host_group_info_map_id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField()
    host_group_info_id = models.IntegerField()
    del_flag = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    is_owner = models.IntegerField()
    permission = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'user_and_host_group_info_map'

