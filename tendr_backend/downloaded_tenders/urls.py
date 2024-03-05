from django.urls import path

from .views import DownloadedTenders

urlpatterns = [
    path("downloaded-tenders/", DownloadedTenders.as_view(), name="downloaded-tenders"),
]
