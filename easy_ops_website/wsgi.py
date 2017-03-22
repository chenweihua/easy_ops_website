"""
WSGI config for easy_ops_website project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "easy_ops_website.settings")
os.environ["DJANGO_SETTINGS_MODULE"] = "easy_ops_website.settings"

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

os.environ['PYTHON_EGG_CACHE'] = '/tmp/.python-eggs'
from os.path import join,dirname,abspath
PROJECT_DIR = dirname(dirname(abspath(__file__)))
import sys
sys.path.insert(0,PROJECT_DIR)
