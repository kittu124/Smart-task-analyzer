from django.urls import path
from . import views

urlpatterns = [
    path("analyze/", views.analyze_tasks, name="analyze-tasks"),
    path("suggest/", views.suggest, name="suggest-tasks"),
]
