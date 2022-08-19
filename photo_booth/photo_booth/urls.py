from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from photos import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('manage/', include('photos.urls')),
    path('', views.main_page, name='main_page'),
    path('registry/<int:city_code>/', views.registry, name='registry'),
    path('registry/<int:city_code>/<int:journal_id>', views.registry_further, name='registry_further'),
    path('registry/<int:city_code>/<int:journal_id>/<int:photo_id>', views.furthermore, name='furthermore'),
]

urlpatterns += [
    path('manage/', include('django.contrib.auth.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
