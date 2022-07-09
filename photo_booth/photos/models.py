from django.contrib.auth.models import User
from django.contrib import admin
from django.db import models


class Photo(models.Model):
    photo_name = models.CharField(max_length=255, default=None)
    description = models.CharField(max_length=255)
    display = models.BooleanField(default=True)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, default=1)
