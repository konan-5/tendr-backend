from django.urls import path

from .views import Latest, Scrape, Search

urlpatterns = [
    path("scrape/", Scrape.as_view()),
    path("search/", Search.as_view()),
    path("latest/", Latest.as_view()),
]
