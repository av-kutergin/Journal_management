from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet

from photos.models import Photo
from photos.serializers import PhotoSerializer


def photo_page(request):
    return render(request, 'index.html', {'photos': Photo.objects.all()})


class PhotoView(ModelViewSet):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer


def photos_app(request):
    return render(request, 'main_app.html')
