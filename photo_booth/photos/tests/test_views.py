import os
import tempfile

from django.urls import reverse

from photo_booth.settings import MEDIA_ROOT

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'photo_booth.settings')
import django

django.setup()
from io import BytesIO

from PIL import Image
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.files import File
from django.http import HttpRequest
from django.contrib.auth.models import AnonymousUser
from django.test.client import RequestFactory, Client
from django.test import TestCase, override_settings

from photos.views import *
import shutil

TEST_DIR = 'test_data'


def add_session_to_request(request: HttpRequest) -> HttpRequest:
    """Adds session support to a RequestFactory generated request."""
    middleware = SessionMiddleware(get_response=lambda request: None)
    middleware.process_request(request)
    request.session.save()
    return request


def add_messages_to_request(request: HttpRequest) -> HttpRequest:
    """Adds message/alert support to a RequestFactory generated request."""
    request._messages = FallbackStorage(request)
    return request


@override_settings(MEDIA_ROOT=(TEST_DIR + '/media'))
# @override_settings(MEDIA_ROOT=tempfile.TemporaryDirectory(prefix='mediatest').name)
class ViewsTests(TestCase):
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
        cls.user = User.objects.create_user(id=2, username='Jack8369587426', email='abirvalg@lasdf.am',
                                             password='jasdfjkn,m1')
        cls.user.save()
        cls.city_1 = City.objects.create(id=1, city_name='City1', city_code=11111111)
        cls.city_1.operators.add(cls.user)
        cls.city_1.save()
        cls.journal = Journal(journal_city=cls.city_1, journal_owner=cls.user)
        cls.journal.save()
        cls.photo = Photo.objects.create(journal=cls.journal, photo_image=cls.get_image_file())
        cls.photo.save()
        cls.client = Client()

    def test_main_page(self):
        request = self.factory.get('')
        response = main_page(request)
        self.assertEqual(response.status_code, 200)

    def test_registry(self):
        request = self.factory.get('registry')
        request.user = self.user
        response = registry(request, self.city_1.city_code)
        self.assertEqual(response.status_code, 200)

    def test_registry_further(self):
        request = self.factory.get('registry_further')
        # request.user = self.user
        response = registry_further(request, self.city_1.city_code, self.journal.journal_name)
        self.assertEqual(response.status_code, 200)

    def test_furthermore(self):
        request = self.factory.get('furthermore')
        request.user = self.user
        response = furthermore(request, self.city_1.city_code, self.journal.journal_name, self.photo.pk)
        self.assertEqual(response.status_code, 200)

    def test_main_manage_user(self):
        request = self.factory.get('main_manage')
        request.user = self.user
        response = main_manage(request)
        self.assertEqual(response.status_code, 200)

    def test_main_manage_anonymous(self):
        self.client.logout()
        request = self.factory.get('main_manage')
        request.user = AnonymousUser
        response = main_manage(request)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/manage', follow=True)
        self.assertRedirects(response=response, expected_url='/manage/login/', status_code=301)

    def test_cities_selection(self):
        request = self.factory.get('cities_selection')
        request.user = self.user
        response = cities_selection(request)
        self.assertEqual(response.status_code, 200)

    def test_get_or_update_journals(self):
        request = self.factory.get('get_or_update_journals')
        request.user = self.user
        response = get_or_update_journals(request, self.city_1.city_code)
        self.assertEqual(response.status_code, 200)

    def test_get_or_update_journals_POST(self):
        file = self.get_image_file()
        request = self.factory.post(path='get_or_update_journals', data={'image': self.get_image_file()})
        request.user = self.user
        add_session_to_request(request)
        add_messages_to_request(request)
        response = get_or_update_journals(request, self.city_1.city_code)
        self.assertEqual(len(self.city_1.journal_set.all()), 1)
        self.assertEqual(response.status_code, 302)

    def test_get_or_update_journals_POST_new_journal(self):
        journal1 = Journal.objects.create(journal_city=self.city_1, journal_owner=self.user, journal_name='100-132')
        for i in range(33):
            photo = Photo.objects.create(journal=journal1, photo_image=self.get_image_file())
            photo.save()
        request = self.factory.post(path='get_or_update_journals', data={'image': self.get_image_file()})
        request.user = self.user
        add_session_to_request(request)
        add_messages_to_request(request)
        response = get_or_update_journals(request, self.city_1.city_code)
        self.assertEqual(self.city_1.journal_set.all().count(), 3)
        self.assertEqual(response.status_code, 302)

    def test_gget_or_update_journals_update_method(self):
        with self.assertRaises(BadRequest) as ctx:
            request = self.factory.get('get_or_update_journals')
            request.user = self.user
            request.method = "PUT"
            response = get_or_update_journals(request, self.city_1.city_code)
        expected_msg = BadRequest()
        self.assertEquals(type(ctx.exception), type(expected_msg))

    def test_abs_url_city(self):
        path = self.city_1.get_absolute_url()
        request = self.factory.get(path)
        request.user = self.user
        response = get_or_update_journals(request, city_code=self.city_1.city_code)
        self.assertEqual(response.status_code, 200)

    # def test_abs_url_journal(self):
    #     path = self.journal.get_absolute_url()
    #     request = self.factory.get(path)
    #     request.user = self.user
    #     response = registry_further(request, city_code=self.city_1.city_code, journal_id=self.journal.pk)
    #     self.assertEqual(response.status_code, 200)


def tearDownModule():
    print("\nDeleting temporary files...\n")
    try:
        shutil.rmtree(TEST_DIR)
        shutil.rmtree(os.path.join(MEDIA_ROOT, '11111111'))
    except OSError:
        pass
