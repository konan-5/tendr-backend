from rest_framework import serializers

from tendr_backend.scrape.models import CftFile, Tender  # Adjust based on your actual models


class CftFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CftFile
        fields = ("id", "file", "title")  # or list specific fields you want to include


class TenderSerializer(serializers.ModelSerializer):
    cft_files = CftFileSerializer(many=True, read_only=True)

    class Meta:
        model = Tender
        fields = ("title", "resource_id", "cft_files", "cpv_code")  # or list specific fields, including 'cft_files'
