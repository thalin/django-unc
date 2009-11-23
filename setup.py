#!/usr/bin/env python
'''
Created on Nov 20, 2009

@author: wfscheper

Setup script for django-unc
'''
from distutils.core import setup

setup(name="django-unc",
      version="1.0",
      description="Django LDAP Backend for UNC",
      author="Zeke Harris",
      author_email="thalin@gmail.com",
      url="http://github.com/thalin/django-unc",
      packages=["django-unc"],
     )