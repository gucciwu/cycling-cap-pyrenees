import logging

from djangorestframework_camel_case import render
from rest_framework import renderers

logger = logging.getLogger(__name__)

OK_KEY_MAP = {
    "results": "data",
    "data": "data",
    "error_code": "error_code",
    "error_message": "error_message",
}

ERROR_KEY_MAP = {
    "results": "data",
    "data": "data",
    "error_code": "error_code",
    "error_message": "error_message",
    "detail": "error_message",
    "code": "error_code"
}


def format_response_data(data, use_map):
    '''
    format response data as Alps standard response structure
    '''
    if data is None or use_map is None:
        return {}

    ret = {}
    for key in data.keys():
        if key in use_map.keys():
            ret.update({use_map[key]: data[key]})
        else:
            ret.update({key: data[key]})

    return ret


def build_response_data(data, renderer_context):
    try:
        if renderer_context['response'].status_code >= 400:
            res_data = format_response_data(data, ERROR_KEY_MAP)
            if 'error_message' not in res_data:
                res_data.update({'error_message': renderer_context['response'].status_text})
            if 'error_code' not in res_data:
                res_data.update({'error_code': renderer_context['response'].status_code})
        else:
            res_data = format_response_data(data, OK_KEY_MAP)
            if 'error_message' not in res_data:
                res_data.update({'error_message': ''})
            if 'error_code' not in res_data:
                res_data.update({'error_code': 0})
    except KeyError as err:
        logger.warning("Unknown renderer context! %s" % str(renderer_context))
        res_data = data
        if 'error_message' not in res_data:
            res_data.update({'error_message': 'Unknown error'})
        if 'error_code' not in res_data:
            res_data.update({'error_code': -1})
    return res_data


class BaseCamelCaseJSONRenderer(render.CamelCaseJSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        res_data = build_response_data(data, renderer_context)
        return super().render(res_data, accepted_media_type=accepted_media_type, renderer_context=renderer_context)


class BaseCamelCaseBrowsableAPIRenderer(render.CamelCaseBrowsableAPIRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        res_data = data  # build_response_data(data, renderer_context)
        return super().render(res_data, accepted_media_type=accepted_media_type, renderer_context=renderer_context)


class ImageRenderer(renderers.BaseRenderer):
    media_type = 'image/png'
    format = 'png'
    charset = None
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        return data
