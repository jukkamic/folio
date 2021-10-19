from django.contrib import admin
from django.urls import path
from . import views
from django.views.decorators.cache import cache_page

urlpatterns = [
    path('', cache_page(2*60)(views.getAll)),
]
