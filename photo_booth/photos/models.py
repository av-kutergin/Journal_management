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
    journal_name = models.CharField(blank=True, max_length=20, verbose_name='Название журнала')
    total_pages = models.IntegerField(blank=True, verbose_name='Количество страниц')
    journal_plenum = models.IntegerField(blank=True, verbose_name='Количество заполненных страниц')

    def update_values(self):
        self.journal_name = f'JR-{self.id}'
        self.total_pages = 3
        self.journal_plenum = len(JournalPhoto.objects.filter(j_photo_journal_id=self.id))
        self.save(update_fields=['journal_name', 'total_pages', 'journal_plenum'])

    def __str__(self):
        return self.journal_name

    class Meta:
        verbose_name = 'Журнал'
        verbose_name_plural = 'Журналы'


class JournalPhoto(models.Model):
    j_photo_journal = models.ForeignKey('Journals', on_delete=models.CASCADE, null=False, verbose_name='Журнал')
    j_photo_image = models.ImageField(null=False, blank=False, verbose_name='Изображение')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    j_photo_name = models.CharField(blank=True, max_length=20, verbose_name='Название')
    j_photo_number = models.IntegerField(blank=True, verbose_name='Номер страницы в журнале')

    def update_values(self):
        self.j_photo_number = len(JournalPhoto.objects.filter(j_photo_journal_id=self.j_photo_journal_id))
        self.j_photo_name = f'{self.j_photo_journal.journal_name}_PG-{self.j_photo_number}'
        self.save(update_fields=['j_photo_name', 'j_photo_number'])

    class Meta:
        verbose_name = 'Фотография'
        verbose_name_plural = 'Фотографии'
