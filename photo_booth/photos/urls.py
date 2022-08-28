from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_manage, name='main_manage'),
    path('cities/', views.cities_selection, name='cities'),
    path('cities/<str:city_code>/', views.get_or_update_journals, name='journal'),
]
