from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('analyze/', views.analyze_tasks, name='analyze-tasks'),
    path('suggest/', views.suggest_tasks, name='suggest-tasks'),
]