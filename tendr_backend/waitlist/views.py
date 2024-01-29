from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Waiter

class WaiterView(APIView):
    permission_classes = (AllowAny, )

    def post(self, request):

        full_name = request.data.get("full_name")
        email = request.data.get("email")
        company = request.data.get("company")
        phone = request.data.get("phone")
        other = request.data.get("other")

        waiter = Waiter()
        waiter.full_name = full_name
        waiter.email = email
        waiter.company = company
        waiter.phone = phone
        waiter.other = other

        waiter.save()

        return Response("success")
