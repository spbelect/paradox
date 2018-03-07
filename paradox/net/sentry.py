# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from datetime import datetime
from hashlib import md5

from kivy.app import App
from kivy.network.urlrequest import UrlRequest
from tinydb import TinyDB, Query

from .. import config
#from ..uix.float_message import show_float_message
from ..scheduler import schedule

try:
    from .release import make_packet, get_server
except ImportError:
    def make_packet(x):
        return x

    def get_server(name):
        return config.SERVER_ADDRESS


x = Query()


class SentrySendQueue(TinyDB):

    def pop(self):
        events = sorted(self.all(), key=lambda x: x.get('data', {}).get('timestamp'))
        return events[0] if events else None

    def add_trace(self, trace):
        timestamp = datetime.utcnow().isoformat()
        self.insert({'data': {'timestamp': timestamp, 'traceback': trace}})

    def on_success(self, request, result):
        #data = json.loads(request.req_body)
        self.remove(eids=[request.packet.eid])
        schedule(self.loop)

    def on_error(self, request, error):
        #print repr(error).decode('unicode-escape')
        schedule(self.loop, timeout=20)

    def on_failure(self, request, error):
        if request.resp_status // 100 == 4 and not request.resp_status == 404:
            # HTTP 4xx Client Error. Client update needed.
            # 404 error may be recovered after client update, so keep these packets.
            self.remove(eids=[request.packet.eid])
        schedule(self.loop, timeout=10)

    def loop(self):
        packet = self.pop()
        #print packet
        if packet:
            self.send_packet(packet)
        else:
            schedule(self.loop, timeout=5)

    def send_packet(self, packet):
        packet['data']['app_id'] = App.app_store[b'app_id']
        packet['data']['hash'] = md5(json.dumps(packet['data'])).hexdigest()

        url = '%s/errors/' % get_server('sentry')

        request = UrlRequest(
            url,
            req_body=json.dumps(make_packet(packet['data'])),
            req_headers={'Content-type': 'application/json'},
            timeout=20,
            on_success=self.on_success,
            on_error=self.on_error,
            on_failure=self.on_error)
        request.packet = packet
