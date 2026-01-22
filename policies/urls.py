# policies/urls.py
from django.urls import path
from .views import CategoryListView, RuleListView

urlpatterns = [
    path("categories/", CategoryListView.as_view()),
    path("rules/", RuleListView.as_view()),
]
