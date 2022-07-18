from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class User(User):
    pass


class Cities(models.Model):
    city_name = models.CharField(max_length=20, db_index=True)
    operators = models.ManyToManyField(User)

    def __str__(self):
        return self.city_name

    def get_absolute_url(self):
        # return reverse('journal', kwargs={'name': self.city_name})
        return reverse('journal', kwargs={'city_id': self.pk})


class Journals(models.Model):
    journal_city = models.ForeignKey('Cities', on_delete=models.CASCADE, null=False)
    journal_owner = models.ForeignKey('User', on_delete=models.CASCADE, null=False)
    time_create = models.DateTimeField(auto_now_add=True)

    def show_info(self, city_id):
        return len(Journals.objects.filter(journal_city=city_id))

    # def get_absolute_url(self):
    #     return reverse('journal', kwargs={'journal_city': self.journal_city})


class JournalPhoto(models.Model):
    j_photo_journal = models.ForeignKey('Journals', on_delete=models.CASCADE, null=False)
    j_photo_image = models.ImageField(null=False, blank=False)
    time_create = models.DateTimeField(auto_now_add=True)

    # def __str__(self):
    #     return self.j_photo_image

