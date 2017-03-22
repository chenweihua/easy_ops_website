#-*- coding: utf-8 -*-

'''
AnsibleAutomation
20160809
'''

from django.conf.urls import patterns, include, url

urlpatterns = patterns('AnsibleAutomation.views',
    
    #主页模块
    url(r'^main_page/$','MainPage',name='asb_main_page_url'),
    url(r'^user_group_page/$','UserGroupPage',name='asb_user_group_page_url'),
    url(r'^atom_task_page/$','AtomTaskPage',name='asb_atom_task_page_url'),
    url(r'^host_group_page/$','HostGroupPage',name='asb_host_group_page_url'),
    url(r'^playbook_page/$','PlaybookPage',name='asb_playbook_page_url'),
    url(r'^host_page/$','HostPage',name='asb_host_page_url'),
    url(r'^file_page/$','FilePage',name='asb_file_page_url'),
    
    #atom_task模块
    url(r'^add_atom_task/$','AddAtomTask',name='add_atom_task_url'),
    url(r'^edit_atom_task/$','EditAtomTask',name='edit_atom_task_url'),
    url(r'^del_atom_task/$','DelAtomTask',name='del_atom_task_url'),
    url(r'^restore_del_atom_task/$','RestoreDelAtomTask',name='restore_del_atom_task_url'),
    url(r'^get_atom_task_data/(?P<SearchFlag>\w+)/(?P<Qwords>\w+)/$','GetAtomTaskData',name='get_atom_task_data_url'),
    
    #设备管理模块
    url(r'^add_host/$','AddHost',name='add_host_url'),
    url(r'^edit_host/$','EditHost',name='edit_host_url'),
    url(r'^del_host/$','DelHost',name='del_host_url'),
    url(r'^restore_del_host/$','RestoreDelHost',name='restore_del_host_url'),
    url(r'^get_host_data/(?P<SearchFlag>\w+)/(?P<Qwords>\w+)/$','GetHostData',name='get_host_data_url'),
    
    #用户管理模块
    url(r'^add_user/$','AddUser',name='add_user_url'),
    url(r'^del_user/$','DelUser',name='del_user_url'),
    url(r'^restore_del_user/$','RestoreDelUser',name='restore_del_user_url'),
    url(r'^get_add_user_data/$','GetAddUserData',name='get_add_user_data_url'), #获取新增用户时所需的数据
    url(r'^get_user_data/(?P<SearchFlag>\w+)/(?P<Qwords>\w+)/$','GetUserData',name='get_user_data_url'),   
    
    #设备分组管理模块（未完续待）
    url(r'^add_host_group/$','AddHostGroup',name='add_host_group_url'),
    url(r'^get_host_group_data/(?P<SearchFlag>\w+)/(?P<Qwords>\w+)/$','GetHostGroupData',name='get_host_group_data_url'),
    
    #playbook管理模块
    url(r'^add_playbook/$','AddPlaybook',name='add_playbook_url'),
    url(r'^del_playbook/$','DelPlaybook',name='del_playbook_url'),
    url(r'^run_playbook/$','RunPlaybook',name='run_playbook_url'),
    url(r'^run_playbook_by_step/$','RunPlaybookByStep',name='run_playbook_by_step_url'),
    url(r'^check_playbook_result/(?P<MAPID>\w+)/$','CheckPlaybookResult',name='check_playbook_result_url'),
    url(r'^check_playbook_result_by_step/(?P<PROCID>\w+)/(?P<MAPID>\w+)/$','CheckPlaybookResultByStep',name='check_playbook_result_by_step_url'),
    url(r'^get_pb_step_proc_info/(?P<MAPID>\w+)/$','GetPbStepProcInfo',name='get_pb_step_proc_info_url'),
    url(r'^proc_playbook_by_step/(?P<MAPID>\w+)/$','ProcPlaybookByStep',name='proc_playbook_by_step_url'),
    
    url(r'^get_playbook_result/(?P<Type>\w+)/(?P<ID>\w+)/(?P<SearchFlag>\w+)/$','GetPlaybookResult',name='get_playbook_result_url'),
    url(r'^restore_del_playbook/$','RestoreDelPlaybook',name='restore_del_playbook_url'),
    url(r'^get_playbook_edit_data/$','GetPlaybookEditData',name='get_playbook_edit_data_url'),
    url(r'^get_playbook_table_data/(?P<SearchFlag>\w+)/(?P<Qwords>\w+)/$','GetPlaybookTableData',name='get_playbook_table_data_url'),
    
    
    #上传文件管理模块
    url(r'^test_file_page/$', 'TestFilePage', name='file_page_url'),    
    url(r'^add_file/$', 'AddFile', name='add_file_url'),    
    #url(r'^edit_file/$', 'AddFile', name='add_file_url'),    
    url(r'^del_file/$', 'DelFile', name='del_file_url'),    
    #url(r'^restore_del_file/$', 'AddFile', name='add_file_url'),
    url(r'^get_file_data/(?P<SearchFlag>\w+)/(?P<Qwords>\w+)/$','GetFileData',name='get_file_data_url'),
    
    
    #api模块
    url(r'^asb_api/$', 'AsbApi', name='asb_api_url'),  
    
    
    
    
    

)