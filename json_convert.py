from flask import Response
import json


def make_utf8_json_response(data):
    return Response(json.dumps(data, ensure_ascii=False), content_type='application/json; charset=utf-8')
