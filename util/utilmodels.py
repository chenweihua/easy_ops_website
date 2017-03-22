#-*- coding: utf-8 -*-
from django.db import models

#用户访问日志信息
class UtilAccessInfo(models.Model):                                                                                          
    insert_time = models.DateTimeField()
    tab_date_time = models.DateTimeField()
    id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=64)
    method = models.CharField(max_length=6)
    url = models.CharField(max_length=512)
    info = models.TextField(blank=True)
    remote_addr = models.CharField(max_length=32)
    class Meta:
        managed = False
        db_table = 'util_access_info'