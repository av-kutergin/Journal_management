from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class City(models.Model):
    city_name = models.CharField(max_length=20, db_index=True, verbose_name='Город')
    operators = models.ManyToManyField(User, verbose_name='Оператор', related_name='cities')

    def __str__(self):
        return self.city_name

    def get_absolute_url(self):
        return reverse('journal', kwargs={'city_id': self.pk})

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'
        ordering = ['city_name']


class Journal(models.Model):
    journal_city = models.ForeignKey('City', on_delete=models.CASCADE, null=False, verbose_name='Город')
    journal_owner = models.ForeignKey(User, on_delete=models.CASCADE, null=False, verbose_name='Оператор')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    journal_name = models.CharField(null=True, max_length=20, verbose_name='Название журнала', default='')
    total_pages = models.IntegerField(null=True, verbose_name='Всего страниц', default=33)
    filled_pages = models.IntegerField(null=True, verbose_name='Заполнено страниц', default=0)

    def update_values(self):
        self.journal_name = f'JR-{self.id}'
        self.filled_pages = len(Photo.objects.filter(journal=self.id))
        self.save(update_fields=['journal_name', 'total_pages', 'filled_pages'])

    def __str__(self):
        return self.journal_name

    class Meta:
        verbose_name = 'Журнал'
        verbose_name_plural = 'Журналы'


class Photo(models.Model):
    journal = models.ForeignKey('Journal', on_delete=models.CASCADE, null=False, verbose_name='Журнал')
    photo_image = models.ImageField(null=False, blank=False, verbose_name='Изображение')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    photo_name = models.CharField(max_length=20, verbose_name='Название', default='')
    page_in_journal = models.IntegerField(verbose_name='Номер страницы в журнале', default=0)

    def update_values(self):
        self.page_in_journal = len(Photo.objects.filter(journal=self.journal_id))
        self.photo_name = f'{self.journal.journal_name}_PG-{self.page_in_journal}'
        self.save(update_fields=['photo_name', 'page_in_journal'])

    class Meta:
        verbose_name = 'Фотография'
        verbose_name_plural = 'Фотографии'
