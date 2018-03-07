# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from hashlib import md5

from kivy.app import App
from kivy.network.urlrequest import UrlRequest
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage

from .. import config
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


class GetQueue(TinyDB):
    def __init__(self, *args, **kwargs):
        super(GetQueue, self).__init__(*args, storage=MemoryStorage, **kwargs)
        self.insert_multiple([
            {
                'url': '/api/v1/regions/',
                'on_success': 'core.get_regions_success',
            },
            {
                'url': '/api/v1/blockforms/general/',
                'on_success': 'core.get_forms_general_success',
            },
            {
                'url': '/api/v1/blockforms/federal/',
                'on_success': 'core.get_forms_federal_success',
            },
            {
                'url': config.CHANGELOG_URL,
                'on_success': 'core.get_changelog_success',
                'priority': 1  # lower priority
            }
        ])

    def pop(self):
        events = sorted(self.all(), key=lambda x: x.get('priority', 0))
        return events[0] if events else None

    def get_regional_forms(self, region_id):
        self.remove(x.on_success == 'core.get_forms_regional_success')
        self.remove(x.on_success == 'core.get_forms_local_success')
        self.remove(x.on_success == 'core.get_mo_list_success')
        self.insert_multiple([
            {
                'url': '/api/v1/blockforms/regional/%s/' % region_id,
                'on_success': 'core.get_forms_regional_success',
                'args': (region_id,)
            },
            {
                'url': '/api/v1/blockforms/local/%s/' % region_id,
                'on_success': 'core.get_forms_local_success',
                'args': (region_id,)
            },
            {
                'url': '/api/v1/regions/%s/mo' % region_id,
                'on_success': 'core.get_mo_list_success',
                'args': (region_id,)
            }])


def on_get_error(request, error):
    #print repr(error).decode('unicode-escape')
    schedule('net.get.get_loop', timeout=10)


def get(url, on_success, args):
    def on_get_success(request, result):
        App.get_queue.remove(x.url == url)
        schedule(on_success, result, *args)
        schedule('net.get.get_loop')

    if url.startswith('http'):
        full_url = url
    else:
        full_url = get_server('primary') + url

    UrlRequest(
        full_url,
        timeout=20,
        on_success=on_get_success,
        on_error=on_get_error,
        on_failure=on_get_error)


def get_loop():
    task = App.get_queue.pop()
    #print task
    if task:
        get(task['url'], task['on_success'], task.get('args', []))
    else:
        schedule('net.get.get_loop', timeout=5)
