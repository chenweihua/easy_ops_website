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

class CcDevInfo(models.Model):
    insert_time = models.DateTimeField()
    dev_ip = models.CharField(max_length=16)
    dev_type = models.CharField(max_length=13)
    using_flag = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'cc_dev_info'

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

