from django_ratelimit.exceptions import Ratelimited
from rest_framework.response import Response
from rest_framework.views import exception_handler


def ratelimit_exception_handler(exc, context):
    if isinstance(exc, Ratelimited):
        return Response(
            {"error": "Too many orders. Please wait before placing another order."},
            status=429,
        )
    return exception_handler(exc, context)
