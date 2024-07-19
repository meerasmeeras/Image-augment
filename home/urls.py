from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('image_upload/', views.image_upload, name='image_upload'),
    
]
