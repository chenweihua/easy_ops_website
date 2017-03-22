#-*- coding: utf-8 -*-
from django.db import models

# Create your models here.

class IdDevInfo(models.Model):                                                                                         
    insert_time = models.DateTimeField()
    dev_ip = models.CharField(max_length=16)
    dev_type = models.CharField(max_length=9)
    net_type = models.CharField(max_length=32, blank=True)
    class Meta:
        managed = False
        db_table = 'id_dev_info'
        


class IdHeartbeatInfo(models.Model):
    insert_time = models.DateTimeField()
    update_time = models.DateTimeField()
    tab_date_time = models.DateTimeField()
    task = models.CharField(max_length=64)
    dev_ip = models.CharField(max_length=16)
    send_pkg_num = models.IntegerField(blank=True, null=True)
    recv_pkg_num = models.IntegerField(blank=True, null=True)
    rc0 = models.CharField(max_length=256)
    rc1 = models.CharField(max_length=256)
    rc2 = models.CharField(max_length=256)
    class Meta:
        managed = False
        db_table = 'id_heartbeat_info'
        
class IdIpDetectNetworkHostMap(models.Model):
    insert_time = models.DateTimeField()
    id = models.IntegerField(primary_key=True)
    network_segment = models.CharField(max_length=16, blank=True)
    mask = models.IntegerField(blank=True, null=True)
    dev_ip = models.CharField(max_length=16)
    ipcnt = models.IntegerField(blank=True, null=True)
    using_ipcnt = models.IntegerField(blank=True, null=True)
    det_type = models.CharField(max_length=4, blank=True)
    opt_type = models.CharField(max_length=5, blank=True)
    class Meta:
        managed = False
        db_table = 'id_ip_detect_network_host_map'
        
        
        
class IdIpDetectResult(models.Model):
    insert_time = models.DateTimeField()
    ip = models.CharField(max_length=16)
    ttl = models.IntegerField(blank=True, null=True)
    time_consume = models.IntegerField(blank=True, null=True)
    arp_addr = models.CharField(max_length=20, blank=True)
    agent_ip = models.CharField(max_length=16)
    class Meta:
        managed = False
        db_table = 'id_ip_detect_result'

        
class IdNetworkSegmentInfo(models.Model):
    insert_time = models.DateTimeField()
    id = models.IntegerField(primary_key=True)
    network_segment = models.CharField(max_length=16, blank=True)
    mask = models.IntegerField(blank=True, null=True)
    net_type = models.CharField(max_length=32, blank=True)
    del_flag = models.IntegerField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'id_network_segment_info'
        
'''
交换机mac表获取功能
'''
class SwSwitchInfo(models.Model):
    insert_time = models.DateTimeField()
    switch_ip = models.CharField(primary_key=True, max_length=16)
    logic_name = models.CharField(max_length=128)
    community = models.CharField(max_length=64)
    agent_ip = models.CharField(max_length=16)
    username = models.CharField(max_length=64)
    passwd = models.CharField(max_length=64)
    mac_cnt = models.IntegerField(blank=True, null=True)
    del_flag = models.IntegerField(blank=True, null=True)
    proc_flag = models.IntegerField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'sw_switch_info'
        

class SwSwitchAccessLog(models.Model):
    insert_time = models.DateTimeField()
    update_time = models.DateTimeField()
    tab_date_time = models.DateTimeField()
    switch_ip = models.CharField(max_length=16)
    proc_status = models.CharField(max_length=16)
    class Meta:
        managed = False
        db_table = 'sw_switch_access_log'
        
        
class SwMacResult(models.Model):
    insert_time = models.DateTimeField()
    switch_ip = models.CharField(max_length=16)
    logic_name = models.CharField(max_length=128)
    agent_ip = models.CharField(max_length=16)
    interface = models.CharField(max_length=128)
    mac_addr = models.CharField(max_length=16)
    class Meta:
        managed = False
        db_table = 'sw_mac_result'




        
        