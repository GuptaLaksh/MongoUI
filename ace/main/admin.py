# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

import templates


# Register your models here.
class MainAdminArea(admin.AdminSite):
    site_header = 'Main Admin Area'
    #login_template = 'main/admin/login.html'

main_site = MainAdminArea(name='MainAdmin')


