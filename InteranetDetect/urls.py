#-*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

urlpatterns = patterns('InteranetDetect.views', 
    url(r'^main_page/$','MainPage',name='main_page_url'),
    url(r'^net_seg_page/$','NetSegPage',name='net_seg_page_url'),
    url(r'^ip_page/$','IpPage',name='ip_page_url'),
    url(r'^dev_page/$','DevPage',name='dev_page_url'),
    url(r'^proc_page/$','ProcPage',name='proc_page_url'),
    
    url(r'^query_main/$','QueryMain',name='query_main_url'),
    
    url(r'^query_net_seg/$','QueryNetSeg',name='query_net_seg_url'),
    url(r'^edit_net_seg/$','EditNetSeg',name='edit_net_seg_url'),
    
    url(r'^query_ip/$','QueryIp',name='query_ip_url'),
    url(r'^query_proc_heartbeat/$','QueryProcHeartbeat',name='query_proc_heartbeat_url'),
    
    url(r'^query_dev/$','QueryDev',name='query_dev_url'),
    
    #接口测试
    url(r'^post_test/$','PostTest',name='post_test_url'),
    
    #交换机mac表获取
    url(r'^sw_main_page/$','SwMainPage',name='sw_main_page_url'),
    url(r'^sw_switch_page/$','SwSwitchPage',name='sw_switch_page_url'),
    url(r'^sw_switch_ret_page/$','SwSwitchRetPage',name='sw_switch_ret_page_url'),
    url(r'^sw_switch_access_log_page/$','SwSwitchAccessLogPage',name='sw_switch_access_log_page_url'),

    url(r'^sw_get_realtime_mac/$','SwGetRealtimeMac',name='sw_get_realtime_mac_url'),
    url(r'^sw_del_switch/$','SwDelSwitch',name='sw_del_switch_url'),
    url(r'^sw_restore_del_switch/$','SwRestoreDelSwitch',name='sw_restore_del_switch_url'),
    url(r'^sw_get_switch_data/(?P<SearchFlag>\w+)/(?P<Qwords>\S+)/$','SwGetSwitchData',name='sw_get_switch_data_url'),
    
    url(r'^sw_get_mac_data/(?P<Qwords>\S+)/$','SwGetMacData',name='sw_get_mac_data_url'),
    url(r'^sw_get_access_log_data/(?P<SearchFlag>\w+)/(?P<Qwords>\S+)/$','SwGetAccLogData',name='sw_get_access_log_data_url'),
    url(r'^sw_get_cnt_data/$','SwGetCntData',name='sw_get_cnt_data_url'),
    
)