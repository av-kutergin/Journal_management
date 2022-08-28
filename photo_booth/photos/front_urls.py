from django.urls import path

from photos import views

urlpatterns = [
    path('<int:city_code>/', views.registry, name='registry'),
    path('<int:city_code>/<str:journal_name>', views.registry_further, name='registry_further'),
    path('<int:city_code>/<str:journal_name>/<int:photo_id>', views.furthermore, name='furthermore'),
]
