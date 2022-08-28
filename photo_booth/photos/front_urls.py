from django.urls import path

from photos import views

urlpatterns = [
    path('<int:city_code>/', views.registry, name='registry'),
    path('<int:city_code>/<int:journal_id>', views.registry_further, name='registry_further'),
    path('<int:city_code>/<int:journal_id>/<int:photo_id>', views.furthermore, name='furthermore'),
]
