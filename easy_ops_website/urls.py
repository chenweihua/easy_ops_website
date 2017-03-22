from django.conf.urls import patterns, include, url

from django.conf import settings
from django.conf.urls.static import static
from easy_ops_website.views import Home,About,Explanation

#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'easy_ops_website.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    #url(r'^admin/', include(admin.site.urls)),
    url(r'^$',Home),
    url(r'^about/$',About),
    url(r'^explanation/$',Explanation),

    url(r'^accounts/',include('UserManage.urls')),
    url(r'^easyops/',include('EasyOps.urls')),
    url(r'^intnetdet/',include('InteranetDetect.urls')),
    url(r'^ansible/',include('AnsibleAutomation.urls')),
    url(r'^cc/',include('CenterControl.urls')),
    
    #static
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.STATIC_ROOT,}),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
