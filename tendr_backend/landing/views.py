import time

from dateutil import parser
from django.db.models import Q
from django.utils import timezone
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from tendr_backend.scrape.models import Tender


def parse_date(date_string):
    dt = parser.parse(date_string)

    # If the datetime object is naive (no timezone info), assume UTC
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        dt = dt.replace(tzinfo=timezone.utc)

    # Getting Unix time
    unix_time = int(dt.timestamp())

    return unix_time


class Scrape(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        now = time.time()
        twenty_four_hours_ago = timezone.now() - timezone.timedelta(hours=24)
        new_tenders = Tender.objects.filter(Q(date_published__gt=twenty_four_hours_ago) & Q(is_active=True)).count()
        response = {
            "widgets": [
                {
                    "is_private": False,
                    "newTenders": new_tenders,
                    "totalTenders": Tender.objects.filter(is_active=True).count(),
                },
            ],
            "tenders": Tender.objects.filter(is_active=True)
            .order_by("-updated_at")[:10]
            .values("title", "tenders_submission_deadline", "ca", "estimated_value", "cpv_code"),
        }
        print(time.time() - now, "aaaaaaaaa")
        return Response(response)


class Search(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        cpv = request.data.get("cpv")
        print(cpv)
        epps = Tender.objects.filter(Q(cpv_code__contains=cpv[:8]) & Q(is_active=True)).values(
            "ca",
            "title",
            "cpv_code",
            "estimated_value",
            "tenders_submission_deadline",
            "tender_detail",
            "resource_id",
            "notice_pdf",
        )
        return Response(epps)


class Latest(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        twenty_four_hours_ago = timezone.now() - timezone.timedelta(hours=24)
        new_tenders = Tender.objects.filter(Q(date_published__gt=twenty_four_hours_ago) & Q(is_active=True)).values(
            "ca",
            "title",
            "cpv_code",
            "estimated_value",
            "tenders_submission_deadline",
            "tender_detail",
            "resource_id",
            "notice_pdf",
        )
        return Response(new_tenders)
