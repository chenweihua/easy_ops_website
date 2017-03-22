#-*- coding: utf-8 -*-

'''
AnsibleAutomation
20160809
'''

from django.db import models
# Create your models here.

class AsbAgentInfo(models.Model):
    insert_time = models.DateTimeField()
    asb_agent = models.CharField(primary_key=True, max_length=16)
    statement = models.CharField(max_length=256)
    del_flag = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'asb_agent_info'

class AsbAtomTaskInfo(models.Model):
    insert_time = models.DateTimeField()
    atom_task_id = models.AutoField(primary_key=True)
    atom_task = models.TextField(blank=True)
    statement = models.CharField(max_length=256)
    del_flag = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'asb_atom_task_info'

class AsbUserGroupAtomTaskMap(models.Model):
    insert_time = models.DateTimeField()
    map_id = models.AutoField(primary_key=True)
    user_group_id = models.IntegerField()
    atom_task_id = models.IntegerField()
    del_flag = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'asb_user_group_atom_task_map'

class AsbHostGroupHostMap(models.Model):
    insert_time = models.DateTimeField()
    map_id = models.AutoField(primary_key=True)
    host_id = models.IntegerField()
    host_group_id = models.IntegerField()
    del_flag = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'asb_host_group_host_map'

class AsbHostGroupInfo(models.Model):
    insert_time = models.DateTimeField()
    host_group_id = models.AutoField(primary_key=True)
    statement = models.CharField(max_length=256)
    del_flag = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'asb_host_group_info'

class AsbHostInfo(models.Model):
    insert_time = models.DateTimeField()
    host_id = models.AutoField(primary_key=True)
    host = models.CharField(max_length=32)
    host_port = models.IntegerField()
    host_user = models.CharField(max_length=64)
    host_passwd = models.CharField(max_length=64)
    host_su_user = models.CharField(max_length=64)
    host_su_passwd = models.CharField(max_length=64)
    statement = models.CharField(max_length=256)
    asb_agent = models.CharField(max_length=16)
    del_flag = models.IntegerField()
    connect_flag = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'asb_host_info'

class AsbPlaybookInfo(models.Model):
    insert_time = models.DateTimeField()
    playbook_id = models.AutoField(primary_key=True)
    playbook_info_json = models.TextField(blank=True)
    playbook_info_yml = models.TextField(blank=True)                                                                                          
    playbook_md5_info = models.CharField(max_length=33, blank=True)
    statement = models.CharField(max_length=256)
    del_flag = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'asb_playbook_info'


class AsbUserGroupHostMap(models.Model):
    insert_time = models.DateTimeField()
    map_id = models.AutoField(primary_key=True)
    user_group_id = models.IntegerField()
    host_id = models.IntegerField()
    del_flag = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'asb_user_group_host_map'
        
        
class AsbUserGroupHostGroupMap(models.Model):
    insert_time = models.DateTimeField()
    map_id = models.AutoField(primary_key=True)
    user_group_id = models.IntegerField()
    host_group_id = models.IntegerField()
    del_flag = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'asb_user_group_host_group_map'

class AsbUserGroupInfo(models.Model):
    insert_time = models.DateTimeField()
    user_group_id = models.AutoField(primary_key=True)
    superuser = models.CharField(max_length=128)
    statement = models.CharField(max_length=256)
    del_flag = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'asb_user_group_info'

class AsbUserGroupUserMap(models.Model):
    insert_time = models.DateTimeField()
    map_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=64)
    user_group_id = models.IntegerField()
    del_flag = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'asb_user_group_user_map'
        
class AsbUserGroupPlaybookMap(models.Model):
    insert_time = models.DateTimeField()
    map_id = models.AutoField(primary_key=True)
    user_group_id = models.IntegerField()
    playbook_id = models.IntegerField()
    proc_type = models.CharField(max_length=4)
    proc_flag = models.IntegerField()    
    del_flag = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'asb_user_group_playbook_map'


class Document(models.Model):
    docfile = models.FileField(upload_to='documents/%Y/%m/%d')
    class Meta:
        managed = False
        db_table = 'document'
        

class AsbFileInfo(models.Model):                                                                                                              
    insert_time = models.DateTimeField()
    id = models.AutoField(primary_key=True)
    file_name = models.CharField(max_length=255)
    file_path = models.FileField(upload_to='documents/%Y%m%d')
    file_flag = models.CharField(max_length=6)
    statement = models.CharField(max_length=256)
    del_flag = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'asb_file_info'
        
        
class AsbUserGroupFileMap(models.Model):
    insert_time = models.DateTimeField()
    map_id = models.AutoField(primary_key=True)
    user_group_id = models.IntegerField()
    file_id = models.IntegerField()
    del_flag = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'asb_user_group_file_map'
        

class AsbPbProcResult(models.Model):
    result_id = models.IntegerField(primary_key=True)
    proc_id = models.IntegerField()
    insert_time = models.DateTimeField()
    user_group_playbook_map_id = models.IntegerField()
    step_id = models.IntegerField()                                                                                            
    obj_id = models.CharField(max_length=64)
    host = models.CharField(max_length=32)
    result_flag = models.CharField(max_length=10)
    result_info = models.TextField(blank=True)
    class Meta:
        managed = False
        db_table = 'asb_pb_proc_result'
        

class AsbPbStepProcInfo(models.Model):
    proc_id = models.IntegerField(primary_key=True)
    insert_time = models.DateTimeField()
    user_group_playbook_map_id = models.IntegerField()
    playbook_id = models.IntegerField()
    playbook_md5_info = models.CharField(max_length=33)
    step_id = models.IntegerField()
    obj_id = models.CharField(max_length=64)
    step_info_json = models.TextField(blank=True)
    proc_flag = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'asb_pb_step_proc_info'
        
        
class AsbApiAuthorityInfo(models.Model):
    id = models.IntegerField(primary_key=True)
    insert_time = models.DateTimeField()
    src_ip = models.CharField(max_length=32)
    api_username = models.CharField(max_length=32)                                                                                         
    api_passwd = models.CharField(max_length=32)
    class Meta:
        managed = False
        db_table = 'asb_api_authority_info'
        
        
class AsbApiProcInfo(models.Model):
    id = models.IntegerField(primary_key=True)
    insert_time = models.DateTimeField()
    opt_time = models.DateTimeField()
    src_ip = models.CharField(max_length=32)
    api_username = models.CharField(max_length=32)
    host = models.CharField(max_length=32)
    cmd_info = models.TextField(blank=True)
    ret_info = models.TextField(blank=True)
    class Meta:
        managed = False
        db_table = 'asb_api_proc_info'
        
        
    
    