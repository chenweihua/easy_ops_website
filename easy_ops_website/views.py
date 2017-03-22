#!/usr/bin/env python
#-*- coding: utf-8 -*-
#update:2014-08-30 by liufeily@163.com

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response,RequestContext

from django.core.urlresolvers import reverse

@login_required
def Home(request):
   return render_to_response('home.html',locals(),RequestContext(request))
   
@login_required
def Explanation(request):
    return render_to_response('explanation.html',locals(),RequestContext(request))

def About(request):
   return render_to_response('about.html',locals(),RequestContext(request))
