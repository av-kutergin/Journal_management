from django.contrib.auth.models import User
from django.contrib import admin
from django.db import models


class Photo(models.Model):
    photo_name = models.CharField(max_length=255, default=None)
    description = models.CharField(max_length=255)
    display = models.BooleanField(default=True)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, default=1)


class Operators(User):
    pass

    # allowed_cities = models.



class Cities(models.Model):
    city_name = models.CharField(max_length=20, db_index=True, )

    def __str__(self):
        return self.city_name


class Journals(models.Model):
    journal_city = models.ForeignKey('Cities', on_delete=models.CASCADE, null=False)
    journal_owner = models.ForeignKey('Operators', on_delete=models.CASCADE, null=False)
    journal_number = models.IntegerField(null=False)
    # journal_filling = models.


class JournalPhoto(models.Model):
    j_photo_journal = models.ForeignKey('Journals', on_delete=models.CASCADE, null=False)
    j_photo_image = models.ImageField(null=False, blank=False)
    j_photo_number = models.IntegerField(auto_created=True)
