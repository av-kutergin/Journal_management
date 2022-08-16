from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_manage, name='main_manage'),
    path('cities/', views.cities_selection, name='cities'),
    path('cities/<int:city_id>/', views.get_journals, name='journal'),
]
