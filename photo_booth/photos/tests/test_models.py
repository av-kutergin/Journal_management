import os
import tempfile
import time

from django.contrib.auth.models import User

from photo_booth.settings import MEDIA_ROOT
from photos.models import *

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'photo_booth.settings')
import django

django.setup()

from django.test import TestCase, override_settings
from django.test.client import RequestFactory, Client
from django.core.files import File
from django.core.exceptions import ValidationError

import shutil
from io import BytesIO
from PIL import Image

TEST_DIR = 'test_data'


# @override_settings(MEDIA_ROOT=(TEST_DIR + '/media'))
class ModelTests(TestCase):
    @staticmethod
    def get_image_file(name='test.png', ext='png', size=(50, 50), color=(256, 0, 0)):
        file_obj = BytesIO()
        image = Image.new("RGBA", size=size, color=color)
        image.save(file_obj, ext)
        file_obj.seek(0)
        return File(file_obj, name=name)

    @classmethod
    def setUpTestData(cls) -> None:
        cls.factory = RequestFactory()
        cls.user = User.objects.create_user(id=2, username='123', email='abirvalg@lasdf.am',
                                             password='jasdfjkn,m1')
        cls.user.save()
        cls.city1 = City.objects.create(id=1, city_name='City1', city_code=11111111)
        cls.city2 = City.objects.create(id=2, city_name='City2', city_code=22222222)
        cls.city1.operators.add(cls.user)
        cls.city1.save()
        cls.city2.save()
        cls.journal1 = Journal(journal_city=cls.city1, journal_owner=cls.user)
        cls.journal2 = Journal(journal_city=cls.city2, journal_owner=cls.user)
        cls.journal1.save()
        cls.journal2.save()
        cls.photo1 = Photo.objects.create(journal=cls.journal1, photo_image=cls.get_image_file())
        cls.photo2 = Photo.objects.create(journal=cls.journal1, photo_image=cls.get_image_file())
        cls.photo3 = Photo.objects.create(journal=cls.journal2, photo_image=cls.get_image_file())
        cls.photo1.save()
        cls.photo2.save()
        cls.photo3.save()
        cls.client = Client()

    def test_city_code_change_photo_name(self):
        self.city1.city_code = '33333333'
        self.city1.save()
        ph1, ph2 = self.journal1.photo_set.all()
        self.assertEqual(self.city1.city_code, '33333333')
        self.assertEqual(ph1.photo_name, '33333333.1')
        self.assertEqual(str(ph2), '33333333: 1-33, 33333333.2')

    def test_journal_name_change_photo_name(self):
        self.journal2.journal_name = '34-66'
        self.journal2.save()
        ph = self.journal2.photo_set.all()[0]
        self.assertEqual(ph.photo_name, '22222222.34')

    def test_empty_name_journal_creation(self):
        journal4 = Journal.objects.create(journal_city=self.city1, journal_owner=self.user)
        journal5 = Journal.objects.create(journal_city=self.city1, journal_owner=self.user)
        # name1 = journal4.journal_name
        # name2 = journal5.journal_name
        self.assertEqual(str(journal4), '11111111: 34-66')
        self.assertEqual(str(journal5), '11111111: 67-99')

    def test_journal_length_change(self):
        prev_len1 = len(self.journal1.photo_set.all())
        prev_len2 = len(self.journal2.photo_set.all())
        Photo.objects.create(journal=self.journal1, photo_image=self.get_image_file())
        self.assertEqual((prev_len1 + 1), len(self.journal1.photo_set.all()))
        self.assertEqual(prev_len2, len(self.journal2.photo_set.all()))

    def test_journal_update_values(self):
        journal3 = Journal.objects.create(journal_city=self.city2, journal_owner=self.user)
        journal4 = Journal.objects.create(journal_city=self.city2, journal_owner=self.user)
        self.assertEqual(journal3.filled_pages, len(journal3.photo_set.all()))
        Photo.objects.create(journal=journal3, photo_image=self.get_image_file())
        Photo.objects.create(journal=journal3, photo_image=self.get_image_file())
        Photo.objects.create(journal=journal4, photo_image=self.get_image_file())
        journal3.update_values()
        journal4.update_values()
        self.assertEqual(journal3.filled_pages, len(journal3.photo_set.all()))
        self.assertEqual(journal4.filled_pages, len(journal4.photo_set.all()))

    def test_photos_order_on_delete(self):
        self.photo1.delete()
        self.assertEqual(self.photo2.photo_name, '11111111.2')
        self.assertEqual(self.photo3.photo_name, '22222222.1')

    def test_photos_file_delete(self):
        path = self.photo1.photo_image.path
        self.photo1.delete()
        self.assertFalse(os.path.exists(path))

    def test_journal_clean_method_true(self):
        journal6 = Journal.objects.create(journal_city=self.city1, journal_owner=self.user, journal_name='')
        self.assertTrue(self.journal2.clean())
        self.assertTrue(journal6.clean())

    def test_journal_clean_method_wrong_input_1(self):
        with self.assertRaises(ValidationError) as ctx:
            self.journal2.journal_name = '5'
            self.journal2.save()
        expected_msg = ValidationError({'journal_name': ['Название журнала должно состоять из двух чисел, разделённых дефисом.']})
        self.assertEquals(ctx.exception, expected_msg)

    def test_journal_clean_method_wrong_input_2(self):
        with self.assertRaises(ValidationError) as ctx:
            self.journal2.journal_name ='1-66'
            self.journal2.save()
        expected_msg = ValidationError({'journal_name': ['Неверный интервал.']})
        self.assertEquals(ctx.exception, expected_msg)

    def test_journal_clean_method_wrong_input_3(self):
        with self.assertRaises(ValidationError) as ctx:
            Journal.objects.create(journal_city=self.city1, journal_owner=self.user, journal_name='1-33')
        expected_msg = ValidationError({'journal_name': ['Журнал с таким названием уже существует.']})
        self.assertEquals(ctx.exception, expected_msg)

    def test_photo_clean_method_all(self):
        photo4 = Photo.objects.create(journal=self.journal2, photo_image=self.get_image_file())
        self.assertTrue(photo4.clean())

    def test_photo_clean_method_wrong_input_1(self):
        with self.assertRaises(ValidationError) as ctx:
            self.photo3.photo_name = 'sadf'
            self.photo3.save()
        expected_msg = ValidationError({'photo_name': ['Название фотографии должно быть числом в формате: "<код города>.<номер фотографии>" или "<номер фотографии>".']})
        self.assertEquals(ctx.exception, expected_msg)

    def test_photo_clean_method_wrong_input_2(self):
        with self.assertRaises(ValidationError) as ctx:
            self.photo3.photo_name ='4568'
            self.photo3.save()
        expected_msg = ValidationError({'photo_name': ['Номер фотографии должен входить в диапазон журнала.']})
        self.assertEquals(ctx.exception, expected_msg)

    def test_photo_clean_method_wrong_input_3(self):
        with self.assertRaises(ValidationError) as ctx:
            Photo.objects.create(journal=self.journal2, photo_image=self.get_image_file(), photo_name='1')
        expected_msg = ValidationError({'photo_name': ['Фотография с таким номером уже существует.']})
        self.assertEquals(ctx.exception, expected_msg)


def tearDownModule():
    print("\nDeleting temporary files...\n")
    try:
        shutil.rmtree(os.path.join(MEDIA_ROOT, '11111111'))
        shutil.rmtree(os.path.join(MEDIA_ROOT, '22222222'))
        shutil.rmtree(os.path.join(MEDIA_ROOT, '33333333'))
        shutil.rmtree(TEST_DIR)
    except OSError:
        pass
