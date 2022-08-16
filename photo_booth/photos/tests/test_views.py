from django.contrib.auth.models import AnonymousUser
from django.test.client import RequestFactory
from django.test import TestCase, Client

from photos.views import *


class SimpleTests(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.user = User.objects.create_user(id=2, username='Jack8369587426', email='abirvalg@lasdf.am', password='eqC11111')
        self.user.save()
        self.city_1 = City.objects.create(id=1, city_name='City1', city_code=34241)
        self.city_1.operators.add(self.user)
        self.city_1.save()
        self.journal = Journal(journal_city=self.city_1, journal_owner=self.user)
        self.journal.save()
        self.photo = Photo.objects.create(journal=self.journal, photo_image='132.png')
        self.photo.save()
        self.anonymous = AnonymousUser

    def test_main_page(self):
        request = self.factory.get('')
        response = main_page(request)
        self.assertEqual(response.status_code, 200)

    def test_registry(self):
        request = self.factory.get('registry')
        request.user = self.user
        response = registry(request, 34241)
        self.assertEqual(response.status_code, 200)

    def test_registry_further(self):
        request = self.factory.get('registry_further')
        request.user = self.user
        response = registry_further(request, 34241, 1)
        self.assertEqual(response.status_code, 200)

    def test_furthermore(self):
        request = self.factory.get('furthermore')
        request.user = self.user
        response = furthermore(request, 34241, 1, 1)
        self.assertEqual(response.status_code, 200)

    def test_main_manage_user(self):
        request = self.factory.get('main_manage')
        request.user = self.user
        response = main_manage(request)
        self.assertEqual(response.status_code, 200)

    # def test_main_manage_anonymous(self):
    #     request = self.factory.get('main_manage')
    #     request.user = self.anonymous
    #     response = main_manage(request)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertRedirects(response=response, expected_url='/manage/login')

    def test_cities_selection(self):
        request = self.factory.get('cities_selection')
        request.user = self.user
        response = cities_selection(request)
        self.assertEqual(response.status_code, 200)

    def test_get_journals(self):
        request = self.factory.get('get_journals')
        request.user = self.user
        response = get_journals(request, self.city_1.pk)
        self.assertEqual(response.status_code, 200)
