from rest_framework.response import Response as RestResponse
import logging
from django.http import HttpResponse
import json
from rest_framework import status

logger = logging.getLogger(__name__)


class AlpsRestResponse:
    @staticmethod
    def success(data: object = None, extra=None, error_code: object = 0, error_message: object = "",
                status: object = status.HTTP_200_OK, *args, **kwargs):
        if data is None:
            data = {}
        if isinstance(extra, dict):
            data.update(extra)
        return RestResponse({"data": data, "error_code": error_code, "error_message": error_message}, status,
                            *args, **kwargs)

    @staticmethod
    def fail(data=None, error_message="", status=status.HTTP_500_INTERNAL_SERVER_ERROR, *args, **kwargs):
        logger.info("Response fail. error code: %s, error message: %s" % (status, error_message))
        if data is None:
            data = {}
        return RestResponse({"data": data, "error_code": status, "error_message": error_message},
                            status, *args, **kwargs)


class AlpsHttpResponse:
    @staticmethod
    def success(data=None, error_code=0, error_message="", status=status.HTTP_200_OK, *args, **kwargs):
        if data is None:
            data = {}
        response_data = {
            "data": data,
            "error_code": error_code,
            "error_message": error_message
        }
        return HttpResponse(json.dumps(response_data, ensure_ascii=False),
                            content_type="application/json,charset=utf-8", status=status, *args, **kwargs)

    @staticmethod
    def fail(data=None, error_code=-1, error_message="", status=status.HTTP_500_INTERNAL_SERVER_ERROR, *args, **kwargs):
        logger.warning("Response fail. error code: %s, error message: %s" % (error_code, error_message))
        if data is None:
            data = {}
        response_data = {
            "data": data,
            "error_code": error_code,
            "error_message": error_message
        }
        return HttpResponse(json.dumps(response_data, ensure_ascii=False),
                            content_type="application/json,charset=utf-8", status=status, *args, **kwargs)


class AlpsImageResponse:
    @staticmethod
    def success(data=None):
        return HttpResponse(data, content_type="image/png", status=status.HTTP_200_OK)
