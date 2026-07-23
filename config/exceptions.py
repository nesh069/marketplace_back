import logging
import traceback

from rest_framework.views import exception_handler
from rest_framework.response import Response

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    logger.error("Unhandled exception in %s: %s\n%s",
                 context.get('view', 'unknown'),
                 exc,
                 traceback.format_exc())

    response = exception_handler(exc, context)

    if response is not None:
        return response

    return Response(
        {"error": str(exc), "type": type(exc).__name__},
        status=500,
    )
