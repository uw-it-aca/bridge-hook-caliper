# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from bridge_hook.util import build_event, send_event
import json


@csrf_exempt
def webhook(req):
    json_data = json.loads(req.body)
    event = build_event(json_data)
    if event:
        send_event(event)

    return HttpResponse('OK')
