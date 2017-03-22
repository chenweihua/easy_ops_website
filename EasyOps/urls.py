#-*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

urlpatterns = patterns('EasyOps.views',    
    url(r'^task_watchdog/$','os_cfg_monitor.TaskWatchdog',name='task_watchdogurl'),
    url(r'^edit_task_watchdog/$','os_cfg_monitor.EditTaskWatchdog',name='edit_task_watchdogurl'),
    url(r'^add_task_watchdog/$','os_cfg_monitor.AddTaskWatchdog',name='add_task_watchdogurl'),
    url(r'^del_task_watchdog/(?P<ID>\d+)$','os_cfg_monitor.DelTaskWatchdog',name='del_task_watchdogurl'),
    url(r'^get_task_watchdog/(?P<ID>\d+)/(?P<FLAG>\d+)/(?P<PRO_FLAG>\d+)/$','os_cfg_monitor.GetTaskWatchdog',name='get_task_watchdogurl'),
    url(r'^get_the_task_watchdog/(?P<TASK>\d+)/(?P<HOST>\d+)/(?P<PRO_FLAG>\d+)/$','os_cfg_monitor.GetTheTaskWatchdog',name='get_the_task_watchdogurl'),
    url(r'^update_the_task_watchdog/(?P<TASK>\d+)/(?P<HOST>\d+)/$','os_cfg_monitor.UpdateTheTaskWatchdog',name='update_the_task_watchdogurl'),
    
    #原子操作
    url(r'^atom_task_watchdog/$','os_cfg_monitor.AtomTaskWatchdog',name='atom_task_watchdogurl'),    
    url(r'^edit_atom_task_watchdog/$','os_cfg_monitor.EditAtomTaskWatchdog',name='edit_atom_task_watchdogurl'),
    url(r'^add_atom_task_watchdog/$','os_cfg_monitor.AddAtomTaskWatchdog',name='add_atom_task_watchdogurl'),
    url(r'^del_atom_task_watchdog/(?P<ID>\d+)$','os_cfg_monitor.DelAtomTaskWatchdog',name='del_atom_task_watchdogurl'),

    #大机维护工具
    url(r'^realtime_task_watchdog/$','os_cfg_monitor.RealTimeTaskWatchdog',name='realtime_task_watchdogurl'),
    url(r'^get_atom_task_and_host_watchdog/$','os_cfg_monitor.GetAtomTaskAndHostWatchdog',name='get_atom_task_and_host_watchdogurl'),
    url(r'^get_atom_task/$','os_cfg_monitor.GetAtomTaskWatchdog',name='get_atom_task_watchdogurl'),
    url(r'^add_realtime_task_watchdog/$','os_cfg_monitor.AddRealTimeTaskWatchdog',name='add_realtime_task_watchdogurl'),
    url(r'^add_realtime_task_new_watchdog/$','os_cfg_monitor.AddRealTimeTaskNewWatchdog',name='add_realtime_task_new_watchdogurl'),
    url(r'^send_realtime_task_cmd_watchdog/$','os_cfg_monitor.SendRealTimeTaskCmdWatchdog',name='send_realtime_task_cmd_watchdogurl'),
    
    url(r'^get_the_task_info_watchdog/$','os_cfg_monitor.GetTheTaskInfoWatchdog',name='get_the_task_info_watchdogurl'),
    url(r'^get_task_by_ip_watchdog/$','os_cfg_monitor.GetTaskByIpWatchdog',name='get_task_by_ip_watchdogurl'),
    url(r'^get_task_detail_by_id_watchdog/$','os_cfg_monitor.GetTaskDetailByIdWatchdog',name='get_task_detail_by_id_watchdogurl'),
    url(r'^reset_realtime_task_watchdog/(?P<ID>\d+)/$','os_cfg_monitor.ResetRealtimeTaskWatchdog',name='reset_realtime_task_watchdogurl'),
    url(r'^get_task_host_watchdog/$','os_cfg_monitor.GetTaskHostWatchdog',name='get_task_host_watchdogurl'),
    
    
    #和阿炜测试用的两个api
    url(r'^test_ansible_cmd_send/$','os_cfg_monitor.TestAnsibleCmdSend',name='test_ansible_cmd_sendurl'),
    url(r'^test_ansible_result_query/$','os_cfg_monitor.TestAnsibleResultQuery',name='test_ansible_result_queryurl'),

)
