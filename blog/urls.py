from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('posts/', views.postsApi),
    path('posts/latest/<int:number>', views.getLatest),
    path('posts/<int:id>/', views.getPost),
]
