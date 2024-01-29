from django.urls import path
from .views import WaiterView

urlpatterns = [
    path("add/", WaiterView.as_view()),
]