from django.urls import path
from . import views

urlpatterns = [
    path('', views.startAllQuotes, name="startAllQuotes"),
    path('allquotes', views.startAllQuotes, name="startAllQuotes"),
    path('candles', views.startCandleCandles, name="startCandleCandles"),
    path('websockets', views.startWebsocket, name="startWebsocket"),
    path('processdata', views.processVisualizeData, name="processVisualizeData"),
    path('viewdata', views.getVisualData, name="getVisualData"),
    path('visualfilenames', views.getVisualFilenames, name="getVisualFilenames"),
    path('visualfile/<str:filename>/', views.getVisualFile, name='getVisualFile'),
    path('sleepy', views.sleepy, name='sleepy')
]
