from django.contrib import admin
from django.urls import path
from . import views
from django.views.decorators.cache import cache_page

urlpatterns = [
    path('', cache_page(25)(views.getAll)),
    path('deposits/addr/<str:symbol>/', views.getDepositAddr),
    path('history/<int:days>/', views.getHistory),
    path('history/store/', views.storeBalances),
    path('margin/', views.getMarginBalances),
    # path('account/', views.getAccountBalances),
    path('price/<str:symbol>/', cache_page(5)(views.getPrice)),
    path('query/', views.query),
]
