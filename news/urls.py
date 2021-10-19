from django.contrib import admin
from django.urls import path
from . import views
from django.views.decorators.cache import cache_page

urlpatterns = [
    path('cryptopanic/<str:kind>/<str:filter>/', cache_page(3*60)(views.getNews)),
]
