from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class User(User):
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Cities(models.Model):
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


class Journals(models.Model):
    journal_city = models.ForeignKey('Cities', on_delete=models.CASCADE, null=False, verbose_name='Город')
    journal_owner = models.ForeignKey('User', on_delete=models.CASCADE, null=False, verbose_name='Оператор')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')

    def __str__(self):
        return f'Журнал №{str(self.id)}'

    def show_info(self, city_id):
        return len(Journals.objects.filter(journal_city=city_id))

    class Meta:
        verbose_name = 'Журнал'
        verbose_name_plural = 'Журналы'


class JournalPhoto(models.Model):
    j_photo_journal = models.ForeignKey('Journals', on_delete=models.CASCADE, null=False, verbose_name='Журнал')
    j_photo_image = models.ImageField(null=False, blank=False, verbose_name='Изображение')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')

    class Meta:
        verbose_name = 'Фотография'
        verbose_name_plural = 'Фотографии'
