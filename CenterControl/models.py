#-*- coding: utf-8 -*-
from django.db import models
import hashlib
from django.core.files.storage import FileSystemStorage

# Create your models here.

'''
####################################
系统健康度
####################################
'''
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

class HostTaskHeartbeatInfo(models.Model):
    host_task_heartbeat_info_id = models.IntegerField(primary_key=True)
    dev_ip = models.CharField(max_length=16)
    dev_type = models.CharField(max_length=16, blank=True)
    heartbeat_type = models.CharField(max_length=6, blank=True)
    heartbeat_time = models.DateTimeField()
    received_cnt = models.IntegerField()
    received_data = models.TextField(blank=True)
    pre_start_cnt = models.IntegerField()
    pre_start_data = models.TextField(blank=True)
    started_cnt = models.IntegerField()
    started_data = models.TextField(blank=True)
    finished_cnt = models.IntegerField()
    finished_data = models.TextField(blank=True)
    tab_date_time = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'host_task_heartbeat_info'

'''
####################################
主机管理任务下发
####################################
'''
class HostInfo(models.Model):
    host_id = models.AutoField(primary_key=True)
    host = models.CharField(max_length=32)
    hostname = models.CharField(max_length=32, blank=True,default=None)
    port = models.CharField(max_length=5, blank=True,default=22)
    user = models.CharField(max_length=64)
    ssh_pass = models.CharField(max_length=64)
    ssh_private_key_file = models.CharField(max_length=255, blank=True,default=None)
    become = models.IntegerField(default=1)
    become_method = models.CharField(max_length=10, default="su", blank=True)
    become_user = models.CharField(max_length=64, blank=True,default=None)
    become_pass = models.CharField(max_length=64, blank=True,default=None)
    statement = models.CharField(max_length=255, blank=True,default=None)
    probe_ip = models.CharField(max_length=32,default="0.0.0.0")
    del_flag = models.IntegerField(default=0)
    detect_flag = models.IntegerField(default=0)
    connect_flag = models.IntegerField(default=0)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    status = models.TextField(blank=True)
    cache_flag = models.IntegerField(default=1)
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
    tab_date_time = models.DateTimeField()
    super_host_task_id = models.IntegerField(default=0)
    class Meta:
        managed = False
        db_table = 'host_task'


class HostTaskOperation(models.Model):
    host_task_operation_id = models.IntegerField(primary_key=True)
    tab_date_time = models.DateTimeField()
    host_task_id = models.IntegerField()
    host_id = models.IntegerField()
    type = models.CharField(max_length=30,default='raw',editable=False)
    arg = models.CharField(max_length=255)
    prority = models.IntegerField(default=0, editable=False)
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField()
    result = models.CharField(max_length=30, blank=True, default=None)
    stdout = models.TextField(blank=True)
    stderr = models.TextField(blank=True)
    class Meta:
        managed = False
        db_table = 'host_task_operation'

class HostCoverageStat(models.Model):
    insert_time = models.DateTimeField()
    all_host_cnt = models.IntegerField()
    conn_host_cnt = models.IntegerField()
    unconn_host_cnt = models.IntegerField()
    timeout_host_cnt = models.IntegerField()
    refused_host_cnt = models.IntegerField()
    denied_host_cnt = models.IntegerField()
    closed_by_remote_host_cnt = models.IntegerField()
    other_host_cnt = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'host_coverage_stat'

'''
####################################
文件上传
####################################
'''
class MediaFileSystemStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        if max_length and len(name) > max_length:
            raise(Exception("name's length is greater than max_length"))
        return name

    def _save(self, name, content):
        if self.exists(name):
            # if the file exists, do not call the superclasses _save method
            return name
        # if the file is new, DO call it
        return super(MediaFileSystemStorage, self)._save(name, content)

def uploadFun(instance,filename):
    sMd5 = instance.md5sum
    return "cc/%s@_@%s"%(filename,sMd5)

class CcFileInfo(models.Model):
    insert_time = models.DateTimeField()
    id = models.AutoField(primary_key=True)
    file_name = models.CharField(max_length=255)

    file_path = models.FileField(
        upload_to=uploadFun, storage=MediaFileSystemStorage())
    md5sum = models.CharField(max_length=36)
    class Meta:
        managed = False
        db_table = 'cc_file_info'

    def save(self,*args,**kwargs):
        if not self.pk:  # file is new
            md5 = hashlib.md5()
            for chunk in self.file_path.chunks():
                md5.update(chunk)
            self.md5sum = md5.hexdigest()
        super(CcFileInfo, self).save(*args, **kwargs)


'''
####################################
API模块实现
####################################
'''
class CcApiAuthorityInfo(models.Model):
    id = models.AutoField(primary_key=True)
    insert_time = models.DateTimeField()
    src_ip = models.CharField(max_length=32)
    api_username = models.CharField(max_length=32)
    api_passwd = models.CharField(max_length=32)
    class Meta:
        managed = False
        db_table = 'cc_api_authority_info'


'''
####################################
权限模块
####################################
'''
class HostGroupInfo(models.Model):
    host_group_info_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    del_flag = models.IntegerField(default=0)
    class Meta:
        managed = False
        db_table = 'host_group_info'

class HostInfoAndHostGroupInfoMap(models.Model):
    host_info_and_host_group_info_map_id = models.AutoField(primary_key=True)
    host_id = models.IntegerField()
    host_group_info_id = models.IntegerField()
    del_flag = models.IntegerField(default=0)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'host_info_and_host_group_info_map'

class UserAndHostGroupInfoMap(models.Model):
    user_and_host_group_info_map_id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    host_group_info_id = models.IntegerField()
    del_flag = models.IntegerField(default=0)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    is_owner = models.IntegerField(default=0)
    permission = models.IntegerField(default=0)
    class Meta:
        managed = False
        db_table = 'user_and_host_group_info_map'
