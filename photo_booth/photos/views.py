from django.shortcuts import render, redirect
from rest_framework.viewsets import ModelViewSet

from photos.models import Photo, Cities, JournalPhoto, Journals
from photos.serializers import PhotoSerializer


def photo_page(request):
    return render(request, 'index.html', {'photos': Photo.objects.all()})


class PhotoView(ModelViewSet):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer


def photos_app(request):
    return render(request, 'main_app.html')


def login(request):
    return render(request, 'login.html')


def cities_selection(request):
    return render(request, 'cities.html', {'cities_set': Cities.objects.all()})


def journal(request):
    if request.method == "POST":
        image = request.FILES.get('image')
        photo = JournalPhoto.objects.create(
            j_photo_journal=Journals.objects.all()[0],
            j_photo_image=image,
            j_photo_number=1
        )
        redirect('cities.html')

    return render(request, 'journal.html')
