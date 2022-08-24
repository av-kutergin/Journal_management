import os
import re

from django.forms import ValidationError
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.urls import reverse
from django.dispatch import receiver

from photo_booth.settings import BASE_DIR, MEDIA_ROOT, STATIC_ROOT

TOTAL_PAGES = 33


def photo_path(instance, filename):
    _, file_extension = os.path.splitext(filename)
    city_code = instance.journal.journal_city.city_code
    return f'{city_code}/{city_code}.{get_photo_number(instance)[0]}{file_extension}'


class City(models.Model):
    city_name = models.CharField(max_length=20, db_index=True, verbose_name='Город')
    city_code = models.IntegerField(verbose_name='Код города', null=False, default=0, unique=True)
    operators = models.ManyToManyField(User, verbose_name='Оператор', related_name='cities')

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'
        ordering = ['city_name']

    def __str__(self):
        return f'{self.city_code}: {self.city_name}'

    def get_absolute_url(self):
        return reverse('journal', kwargs={'city_id': self.pk})

    def get_city_code_url(self):
        return reverse('registry', kwargs={'city_code': self.city_code})


class Journal(models.Model):
    journal_city = models.ForeignKey('City', on_delete=models.CASCADE, null=False, verbose_name='Город')
    journal_owner = models.ForeignKey(User, on_delete=models.CASCADE, null=False, verbose_name='Оператор', default='')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    journal_name = models.CharField(null=True, max_length=20, verbose_name='Название журнала', default='', blank=True)
    total_pages = models.IntegerField(null=True, verbose_name='Всего страниц', default=TOTAL_PAGES, editable=False)
    filled_pages = models.IntegerField(null=True, verbose_name='Заполнено страниц', default=0, editable=False)

    def __str__(self):
        return f'{self.journal_city.city_code}: {self.journal_name}'

    class Meta:
        verbose_name = 'Журнал'
        verbose_name_plural = 'Журналы'
        ordering = ['journal_city', 'journal_name']

    def update_values(self):
        self.filled_pages = len(Photo.objects.filter(journal=self))
        self.save(update_fields=['filled_pages'])

    def get_absolute_url(self):
        return reverse('journal', kwargs={'journal_id': self.pk})

    def clean(self):
        if not self.journal_name:
            return True
        all_journals = Journal.objects.filter(journal_city=self.journal_city)
        journals_in_city = set()

        for journal in all_journals:
            if journal != self:
                journals_in_city.add(int(journal.journal_name.split('-')[-1]))

        pattern = '(\d)+-(\d)+'
        if not re.match(pattern, self.journal_name):
            raise ValidationError({'journal_name': 'Название журнала должно состоять из двух чисел, разделённых дефисом.'})

        first_page, last_page = map(int, self.journal_name.split('-'))
        if (
            ((first_page - 1) % TOTAL_PAGES != 0)
            or (last_page % TOTAL_PAGES != 0)
            or (last_page - first_page != TOTAL_PAGES - 1)
        ):
            raise ValidationError({'journal_name': 'Неверный интервал.'})

        if last_page in journals_in_city:
            raise ValidationError({'journal_name': 'Журнал с таким названием уже существует.'})

        return True


class Photo(models.Model):
    journal = models.ForeignKey('Journal', on_delete=models.CASCADE, null=False, verbose_name='Журнал')
    photo_image = models.ImageField(null=False, blank=False, verbose_name='Изображение', default='',
                                    upload_to=photo_path)
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    photo_name = models.CharField(max_length=20, verbose_name='Название', default='', blank=True)
    page_in_journal = models.IntegerField(verbose_name='Номер страницы в журнале', default=0, editable=False)

    class Meta:
        verbose_name = 'Фотография'
        verbose_name_plural = 'Фотографии'
        ordering = ['page_in_journal']

    def __str__(self):
        return f'{self.journal}, {self.photo_name}'

    def get_absolute_url(self):
        return reverse('furthermore',
                       kwargs={'city_code': self.journal.journal_city.city_code, 'journal_id': self.journal_id,
                               'photo_id': self.pk})

    def clean(self):
        if not self.photo_name:
            return True
        instance_journal = Journal.objects.get(pk=self.journal_id)
        photos = Photo.objects.filter(journal=instance_journal)

        photo_numbers_in_journal = set()
        for photo in photos:
            if photo != self and photo.photo_name:
                photo_numbers_in_journal.add(int(photo.photo_name.split('.')[-1]))

        first_page, last_page = map(int, instance_journal.journal_name.split('-'))

        pattern = '((\d).)?(\d)+'
        if not re.match(pattern, self.photo_name):
            raise ValidationError({'photo_name': 'Название фотографии должно быть числом в формате: "<код города>.<номер фотографии>" или "<номер фотографии>".'})

        photo_number = int(self.photo_name.split('.')[-1])
        if (photo_number < first_page) or (photo_number > last_page):
            raise ValidationError({'photo_name': "Номер фотографии должен входить в диапазон журнала."})

        if photo_number in photo_numbers_in_journal:
            raise ValidationError({'photo_name': "Фотография с таким номером уже существует."})

        return True


@receiver(post_save, sender=City)
def update_photos_on_city_renaming(sender, instance, **kwargs):
    journals = Journal.objects.filter(journal_city_id=instance.id)
    for journal in journals:
        photos = Photo.objects.filter(journal=journal)
        for photo in photos:
            page = photo.photo_name.split('.')[-1]
            photo.photo_name = f'{instance.city_code}.{page}'
            photo.save()

    post_save.disconnect(update_photos_on_city_renaming, sender=City)
    instance.save()
    post_save.connect(update_photos_on_city_renaming, sender=City)


@receiver(post_save, sender=Journal)
def update_journal(sender, instance, created, **kwargs):
    instance.clean()
    first_page, last_page = define_journal_pages(instance)
    instance.journal_name = f'{first_page}-{last_page}'
    photos = Photo.objects.filter(journal=instance)
    if not created:
        for photo in photos:
            if not (first_page <= int(photo.photo_name.split('.')[-1]) <= last_page):
                photo.photo_name = f'{instance.journal_city.city_code}.{first_page + photo.page_in_journal - 1}'
                photo.save()

    post_save.disconnect(update_journal, sender=Journal)
    instance.save()
    post_save.connect(update_journal, sender=Journal)


def define_journal_pages(instance):
    all_journals = Journal.objects.filter(journal_city=instance.journal_city)
    journals_in_city = set()
    for journal in all_journals:
        if journal != instance:
            journals_in_city.add(int(journal.journal_name.split('-')[-1]))

    if instance.journal_name:
        first_page, last_page = map(int, instance.journal_name.split('-'))
        return first_page, last_page

    if journals_in_city:
        first_page = max(journals_in_city) + 1
        last_page = first_page + TOTAL_PAGES - 1
        return first_page, last_page

    return 1, TOTAL_PAGES


@receiver(post_save, sender=Photo)
def update_photo_values(sender, instance, **kwargs):
    instance.clean()
    journal = Journal.objects.get(pk=instance.journal_id)
    photo_number, page_in_journal = get_photo_number(instance)

    if instance.photo_name:
        initial_path = instance.photo_image.path
        instance.photo_image = photo_path(instance, instance.photo_image.url.split('/')[-1])
        new_directory = os.path.join(MEDIA_ROOT, str(instance.journal.journal_city.city_code))

        if not os.path.exists(new_directory):
            os.mkdir(new_directory)
        os.rename(initial_path, instance.photo_image.path)

    instance.photo_name = f'{instance.journal.journal_city.city_code}.{photo_number}'
    instance.page_in_journal = page_in_journal
    post_save.disconnect(update_photo_values, sender=Photo)
    instance.save()
    post_save.connect(update_photo_values, sender=Photo)
    journal.update_values()


def get_photo_number(instance):
    instance_journal = Journal.objects.get(pk=instance.journal_id)
    photos = Photo.objects.filter(journal=instance_journal)

    photo_numbers_in_journal = set()
    for photo in photos:
        if photo != instance and photo.photo_name:
            photo_numbers_in_journal.add(int(photo.photo_name.split('.')[-1]))

    first_page, last_page = map(int, instance_journal.journal_name.split('-'))
    if instance.photo_name:
        photo_number = int(instance.photo_name.split('.')[-1])
        page_in_journal = photo_number - first_page + 1
        return photo_number, page_in_journal

    if photo_numbers_in_journal:
        photo_number = max(photo_numbers_in_journal) + 1
        return photo_number, photo_number - first_page + 1

    return first_page, 1


@receiver(models.signals.post_delete, sender=Photo)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.photo_image:
        if os.path.isfile(instance.photo_image.path):
            os.remove(instance.photo_image.path)
