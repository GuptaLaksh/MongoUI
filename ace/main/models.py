# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.


# class User:


# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.username
