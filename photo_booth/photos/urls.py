from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('cities/', views.cities_selection, name='cities'),
    path('journal/', views.journal, name='journal'),
]