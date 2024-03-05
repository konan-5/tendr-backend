from django.shortcuts import render  # noqa
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from tendr_backend.scrape.models import Tender

from .serializers import TenderSerializer  # Adjust the import according to your project structure


# Create your views here.
class DownloadedTenders(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request):

        tender = Tender.objects.first()
        if tender:
            serializer = TenderSerializer(tender)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Resource not found"}, status=status.HTTP_404_NOT_FOUND)
