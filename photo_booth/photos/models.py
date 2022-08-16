import os

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

TOTAL_PAGES = 33


def photo_path(instance, filename):
    _, file_extension = os.path.splitext(filename)
    city_code, _ = instance.photo_name.split('.')
    return f'{city_code}/{instance.photo_name}{file_extension}'


class City(models.Model):
    city_name = models.CharField(max_length=20, db_index=True, verbose_name='Город')
    city_code = models.IntegerField(verbose_name='Код города', null=False, default=0)
    operators = models.ManyToManyField(User, verbose_name='Оператор', related_name='cities')

    def __str__(self):
        return f'{self.city_code}: {self.city_name}'

    def get_absolute_url(self):
        return reverse('journal', kwargs={'city_id': self.pk})

    def get_city_code_url(self):
        return reverse('registry', kwargs={'city_code': self.city_code})

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'
        ordering = ['city_name']


class Journal(models.Model):
    journal_city = models.ForeignKey('City', on_delete=models.CASCADE, null=False, verbose_name='Город')
    journal_owner = models.ForeignKey(User, on_delete=models.CASCADE, null=False, verbose_name='Оператор', default='')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    journal_name = models.CharField(null=True, max_length=20, verbose_name='Название журнала', default='')
    total_pages = models.IntegerField(null=True, verbose_name='Всего страниц', default=TOTAL_PAGES, editable=False)
    filled_pages = models.IntegerField(null=True, verbose_name='Заполнено страниц', default=0, editable=False)

    def update_values(self):
        self.filled_pages = len(Photo.objects.filter(journal=self.id))
        self.save(update_fields=['journal_name', 'total_pages', 'filled_pages'])

    def get_absolute_url(self):
        return reverse('journal', kwargs={'journal_id': self.pk})

    def __str__(self):
        return self.journal_name

    class Meta:
        verbose_name = 'Журнал'
        verbose_name_plural = 'Журналы'


class Photo(models.Model):
    journal = models.ForeignKey('Journal', on_delete=models.CASCADE, null=False, verbose_name='Журнал')
    photo_image = models.ImageField(null=False, blank=False, verbose_name='Изображение', default='',
                                    upload_to=photo_path)
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    photo_name = models.CharField(max_length=20, verbose_name='Название', default='')
    page_in_journal = models.IntegerField(verbose_name='Номер страницы в журнале', default=0, editable=False)

    def update_values(self):
        self.page_in_journal = len(Photo.objects.filter(journal=self.journal_id))
        self.save(update_fields=['photo_name', 'page_in_journal'])

    def get_absolute_url(self):
        return reverse('furthermore',
                       kwargs={'city_code': self.journal.journal_city.city_code, 'journal_id': self.journal_id,
                               'photo_id': self.pk})

    class Meta:
        verbose_name = 'Фотография'
        verbose_name_plural = 'Фотографии'
