# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from hashlib import md5

from kivy.app import App
from kivy.network.urlrequest import UrlRequest
from tinydb import TinyDB, Query

from .. import config
from ..uix.float_message import show_float_message
from ..scheduler import schedule

try:
    from .release import make_packet, get_server
except ImportError:
    def make_packet(x):
        return x

    def get_server(name):
        if name == 'primary':
            return config.SERVER_ADDRESS
        else:
            return config.BACKUP_SERVER_ADDRESS


x = Query()


class SendQueue(TinyDB):
    def __init__(self, server_name, *args, **kwargs):
        super(SendQueue, self).__init__(*args, **kwargs)
        self.server_name = server_name

    def pop(self):
        events = sorted(self.all(), key=lambda x: x.get('data', {}).get('timestamp'))
        return events[0] if events else None

    def add_input_event(self, data):
        self.insert({'type': 'input_event', 'data': dict(data, type='input_event')})

    def add_userprofile(self, data):
        self.insert({'type': 'userprofile', 'data': dict(data, type='userprofile')})

    def add_position(self, data):
        self.insert({'type': 'position', 'data': dict(data, type='position')})

    def on_success(self, request, result):
        self.remove(eids=[request.packet.eid])
        if request.packet['type'] == 'input_event' and self.server_name == 'primary':
            data = json.loads(request.req_body)
            schedule('core.send_input_event_success', data)
        schedule(self.loop)

    def on_error(self, request, error):
        schedule(self.loop, timeout=10)

    def on_failure(self, request, error):
        if request.resp_status // 100 == 4 and not request.resp_status == 404:
            # HTTP 4xx Client Error. Client update needed.
            # 404 error may be recovered after client update, so keep these packets.
            self.remove(eids=[request.packet.eid])
            if self.server_name == 'primary':
                show_float_message(repr(error).decode('unicode-escape'))
                if request.packet['type'] == 'input_event':
                    data = json.loads(request.req_body)
                    schedule('core.send_input_event_fatal_error', data, request, error)
        elif self.server_name == 'primary' and request.packet['type'] == 'input_event':
            data = json.loads(request.req_body)
            schedule('core.send_input_event_error', data, request, error)
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

        if packet['type'] == 'input_event':
            url = '%s/api/v1/events/' % get_server(self.server_name)
        elif packet['type'] == 'userprofile':
            url = '%s/api/v1/user/info/%s/' % (get_server(self.server_name), packet['data']['app_id'])
        elif packet['type'] == 'position':
            url = '%s/api/v1/user/position/' % get_server(self.server_name)

        #print url
        request = UrlRequest(
            url,
            req_body=json.dumps(make_packet(packet['data'])),
            req_headers={'Content-type': 'application/json'},
            timeout=20,
            on_success=self.on_success,
            on_error=self.on_error,
            on_failure=self.on_failure)
        request.packet = packet


def queue_send_input_event(data):
    App.send_queue.add_input_event(data)
    if config.HAS_BACKUP_SERVER:
        App.send_queue_backup.add_input_event(data)


def queue_send_userprofile(data):
    App.send_queue.add_userprofile(data)
    if config.HAS_BACKUP_SERVER:
        App.send_queue_backup.add_userprofile(data)


def queue_send_position(data):
    App.send_queue.add_position(data)
    if config.HAS_BACKUP_SERVER:
        App.send_queue_backup.add_position(data)
