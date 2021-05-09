from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.startAllQuotes, name="startAllQuotes"),
    path('', views.startCandleCandles, name="startCandleCandles"),
    path('', views.startWebsocket, name="startWebsocket"),
]
