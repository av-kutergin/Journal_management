from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_page, name='main_page'),
    path('cities/', views.cities_selection, name='cities'),
    path('cities/<int:city_id>/', views.get_journals, name='journal'),
]
