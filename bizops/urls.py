from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.startAllQuotes, name="startAllQuotes"),
    path('allquotes', views.startAllQuotes, name="startAllQuotes"),
    path('candles', views.startCandleCandles, name="startCandleCandles"),
    path('', views.startWebsocket, name="startWebsocket"),
]
