from django.shortcuts import render  # noqa
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


# Create your views here.
class DownloadedTenders(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response("success", status=status.HTTP_200_OK)
