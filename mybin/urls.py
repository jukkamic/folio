from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('mock/', views.mockAll),
    path('custom/<str:endpoint>/', views.getCustom),
    path('price/<str:symbol>/', views.getPrice),
    path('', views.getAll),
]
