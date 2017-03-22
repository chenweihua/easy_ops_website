#-*- coding: utf-8 -*-
from django.db import models

# Create your models here.
            

#配置监控系统主机信息表
class WdHostInfo(models.Model):
    insert_time = models.DateTimeField()
    id = models.AutoField(primary_key=True)
    host_ip = models.CharField(max_length=16)
    host_domain = models.CharField(max_length=64)
    host_port = models.IntegerField()
    host_user = models.CharField(max_length=64)
    host_passwd = models.CharField(max_length=64)
    host_su_user = models.CharField(max_length=64)
    host_su_passwd = models.CharField(max_length=64)
    del_flag = models.IntegerField()
    operator = models.CharField(max_length=128)
    class Meta:
        managed = False
        db_table = 'wd_host_info'
        
class WdRealtimeHostInfo(models.Model):
    insert_time = models.DateTimeField()
    id = models.AutoField(primary_key=True)
    host_ip = models.CharField(max_length=16)
    host_domain = models.CharField(max_length=64)
    host_port = models.IntegerField()
    host_user = models.CharField(max_length=64)
    host_passwd = models.CharField(max_length=64)
    host_su_user = models.CharField(max_length=64)
    host_su_passwd = models.CharField(max_length=64)
    del_flag = models.IntegerField()
    operator = models.CharField(max_length=128)
    class Meta:
        managed = False
        db_table = 'wd_realtime_host_info'

#配置监控系统任务信息表
class WdTaskInfo(models.Model):
    insert_time = models.DateTimeField()
    id = models.AutoField(primary_key=True)
    task = models.TextField(blank=True)
    task_interval = models.IntegerField()
    task_info = models.TextField(blank=True)
    del_flag = models.IntegerField()
    operator = models.CharField(max_length=128)
    mail_recv = models.CharField(max_length=256)
    class Meta:
        managed = False
        db_table = 'wd_task_info' 


#配置监控系统任务映射表
class WdTaskHostMap(models.Model):
    insert_time = models.DateTimeField()
    update_time = models.DateTimeField()
    task_id = models.IntegerField()
    host_id = models.IntegerField()
    ret_0 = models.TextField(blank=True)
    ret_1 = models.TextField(blank=True)
    ret_diff = models.TextField(blank=True)
    md5_0 = models.CharField(max_length=64)
    md5_1 = models.CharField(max_length=64)
    del_flag = models.IntegerField()
    opt_flag = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'wd_task_host_map'
        
#配置监控系统原子命令表
class WdAtomTaskInfo(models.Model):                                                                                                                
    insert_time = models.DateTimeField()
    id = models.AutoField(primary_key=True)
    task = models.TextField(blank=True)
    task_info = models.TextField(blank=True)
    operator = models.CharField(max_length=128)
    del_flag = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'wd_atom_task_info'

#配置监控系统实时任务表
class WdRealtimeTaskInfo(models.Model):
    insert_time = models.DateTimeField()
    id = models.AutoField(primary_key=True)
    task = models.TextField(blank=True)
    task_interval = models.IntegerField()
    task_info = models.TextField(blank=True)
    operator = models.CharField(max_length=128)
    del_flag = models.IntegerField()
    opt_stat = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'wd_realtime_task_info'

        
#配置监控系统实时任务映射表
class WdRealtimeTaskHostMap(models.Model):
    insert_time = models.DateTimeField()
    update_time = models.DateTimeField()
    task_id = models.IntegerField()
    host_id = models.IntegerField()
    ret_0 = models.TextField(blank=True)
    ret_1 = models.TextField(blank=True)
    ret_diff = models.TextField(blank=True)
    md5_0 = models.CharField(max_length=64)
    md5_1 = models.CharField(max_length=64)
    opt_0_flag = models.IntegerField()
    opt_1_flag = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'wd_realtime_task_host_map'
