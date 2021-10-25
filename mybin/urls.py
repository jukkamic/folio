from django.contrib import admin
from django.urls import path
from . import views
from django.views.decorators.cache import cache_page

urlpatterns = [
    path('', cache_page(5)(views.getAll)),
    path('test-kucoin/', views.testKucoin),
    path('login/', views.login),
    path('deposits/addr/<str:symbol>/', views.getDepositAddr),
]
