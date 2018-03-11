# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import re

from datetime import datetime, timedelta
from os.path import join, exists

from kivy.app import App

from . import net

from .scheduler import schedule
from .uix.base_input import Input
from .uix.float_message import show_float_message
#from .uix.terms_dialog import show_terms_dialog
from .uix.newversion_dialog import show_new_version_dialog
from .uix.screens.position_screen import StatusChoice, RegionChoice
from .utils import strptime

#import config


def userprofile_errors():
    errors = []
    data = App.app_store.get(b'profile', {})
    if not data.get('phone'):
        errors.append('Телефон')
    if not data.get('first_name'):
        errors.append('Имя')
    if not data.get('last_name'):
        errors.append('Фамилия')
    if errors:
        errors = 'Пожалуйста заполните обязательные поля\n' + '\n'.join(errors)
        show_float_message(text=errors)
        return errors
    else:
        return False


def new_input_event(input, value):
    if userprofile_errors():
        App.screens.push_screen('userprofile')
        return

    if App.screens.get_screen('position').show_errors():
        App.screens.push_screen('position')
        return

    timestamp = datetime.utcnow()
    position = App.app_store.get(b'position', {})

    event = {
        'timestamp': timestamp.isoformat(),
        'uik': position.get(b'uik'),
        'region_id': position.get(b'region_id'),
        'input_id': input.input_id,
        'value': value}

    if input.form['form_type'] == 'GENERAL':
        event_title = input.json['label']
    else:
        event_title = '%s:\n %s' % (input.form['name'], input.json['label'])

    eid = App.event_store.insert(dict(event, title=event_title))

    input.on_save_success(eid, timestamp, value)
    App.screens.get_screen('events').add_event(dict(event, title=event_title))

    net.queue_send_input_event(event)


def send_input_event_success(event):
    input = Input.objects.get(input_id=event['input_id'])
    if input:
        input.on_send_success(event)


def send_input_event_error(event, request, error_data):
    input = Input.objects.get(input_id=event['input_id'])
    if input:
        input.on_send_error(event, request, error_data)


def send_input_event_fatal_error(event, request, error_data):
    input = Input.objects.get(input_id=event['input_id'])
    if input:
        input.on_send_fatal_error(event, request, error_data)


def leave_userprofile_screen():
    data = App.screens.get_screen('userprofile').get_data()
    stored = App.app_store.get(b'profile', {})
    if stored == data:
        return
    App.app_store[b'profile'] = data
    App.app_store.sync()

    timestamp = datetime.utcnow().isoformat()
    net.queue_send_userprofile(dict(data, timestamp=timestamp))


def load(filename):
    filepath = join(App.user_data_dir, filename)
    if not exists(filepath):
        return []
    with open(filepath) as f:
        return json.load(f)


def _get_local_forms():
    position = App.app_store.get(b'position')
    if not position or not position.get('region_id'):
        return []
    forms = load('forms_local_%s.json' % position.get('region_id'))
    return [x for x in forms if int(position.get('uik')) in x.get('uiks', [])]


def leave_position_screen():
    data = App.screens.get_screen('position').get_data()
    stored = App.app_store.get(b'position', {})
    if stored == data:
        return
    App.app_store[b'position'] = data
    App.app_store.sync()
    _update_position(data)

    timestamp = datetime.utcnow().isoformat()
    net.queue_send_position(dict(data, timestamp=timestamp))

    if data.get('region_id') and data.get('region_id') != stored.get('region_id'):
        App.get_queue.get_regional_forms(data.get('region_id'))


def _refresh_mo():
    position = App.app_store.get(b'position', {})
    region_id = position.get('region_id')
    if region_id and position.get('uik'):
        mo_json = load('mo_%s.json' % region_id)
        region_sos_phone = App.regions.get(region_id, {}).get('sos_phone')
        communication_screen = App.screens.get_screen('communication')
        communication_screen.build(position['uik'], region_sos_phone, mo_json)


def _rebuild_forms(form_type):
    position = App.app_store.get(b'position', {})
    formlist_screen = App.screens.get_screen('formlist')

    if form_type == 'general_forms':
        forms_json = load('forms_general.json')
    elif form_type == 'federal_forms':
        forms_json = load('forms_federal.json')
    elif form_type == 'regional_forms':
        forms_json = load('forms_regional_%s.json' % position.get('region_id'))
    elif form_type == 'local_forms':
        forms_json = _get_local_forms()

    formlist_screen.build(form_type, forms_json)
    for form in forms_json:
        for input_data in form['inputs']:
            App.inputs[input_data.get('input_id').encode()] = input_data
        App.inputs.sync()


def _update_position(data):
    if not data:
        return
    position_screen = App.screens.get_screen('position')

    if data.get('status'):
        position_screen.ids['status_choices'].choice = StatusChoice.objects.get(value=data.get('status'))

    if data.get('uik'):
        position_screen.ids['uik'].text = data.get('uik')
        App.root.ids['side_panel'].ids['uik'].text = 'УИК %s' % data.get('uik')

    # rebuild forms
    if data.get('region_id'):
        region_choice = RegionChoice.objects.get(value=data.get('region_id'))
        if region_choice:
            position_screen.ids['region_choices'].choice = region_choice
            App.root.ids['side_panel'].ids['region'].text = region_choice.text
        _rebuild_forms('regional_forms')
        if data.get('uik'):
            _rebuild_forms('local_forms')
            restore_inputs()
            _refresh_mo()


def screens_initialized():

    # TODO: this probably takes a lot of startup time, move to thread?
    regions = load('regions.json')
    App.screens.get_screen('position').build_regions(regions)
    App.regions = {x['id']: x for x in regions}

    _rebuild_forms('general_forms')
    _rebuild_forms('federal_forms')

    profile = App.app_store.get(b'profile', {})
    position = App.app_store.get(b'position', {})
    if position:
        schedule(_update_position, position)
        if position.get('region_id'):
            App.get_queue.get_regional_forms(position.get('region_id'))

    # Send initial position and profile.
    timestamp = datetime.utcnow().isoformat()
    if position and position.get('uik') and position.get('region_id'):
        net.queue_send_position(dict(position, timestamp=timestamp))
    if profile:
        net.queue_send_userprofile(dict(profile, timestamp=timestamp))

    for event in sorted(App.event_store.all(), key=lambda x: x['timestamp']):
        App.screens.get_screen('events').add_event(event)

    schedule(App.send_queue.loop)
    schedule(App.send_queue_backup.loop)
    schedule(App.send_queue_sentry.loop)
    schedule('net.get.get_loop')


def restore_inputs():
    for input in Input.objects.all():
        if input.json['input_type'] == 'NUMBER':
            input.reset()

    position = App.app_store.get(b'position', {})
    for event in sorted(App.event_store.all(), key=lambda x: x['timestamp']):
        if event['uik'] == position.get('uik') and event['region_id'] == position.get('region_id'):
            timestamp = strptime(event['timestamp'], '%Y-%m-%dT%H:%M:%S.%f')
            if datetime.now() - timestamp < timedelta(days=1):
                input = Input.objects.get(input_id=event['input_id'])
                if input:
                    input.add_past_event(event)


def get_regions_success(result):
    with open(join(App.user_data_dir, 'regions.json'), 'w+') as f:
        f.write(json.dumps(result))
    App.screens.get_screen('position').build_regions(result)
    App.regions = {x['id']: x for x in result}


def get_forms_general_success(result):
    with open(join(App.user_data_dir, 'forms_general.json'), 'w+') as f:
        f.write(json.dumps(result))
    _rebuild_forms('general_forms')


def get_forms_federal_success(result):
    with open(join(App.user_data_dir, 'forms_federal.json'), 'w+') as f:
        f.write(json.dumps(result))
    _rebuild_forms('federal_forms')


def get_forms_regional_success(result, region_id):
    filename = 'forms_regional_%s.json' % region_id
    with open(join(App.user_data_dir, filename), 'w+') as f:
        f.write(json.dumps(result))
    _rebuild_forms('regional_forms')


def get_forms_local_success(result, region_id):
    filename = 'forms_local_%s.json' % region_id
    with open(join(App.user_data_dir, filename), 'w+') as f:
        f.write(json.dumps(result))

    position = App.app_store.get(b'position')
    if position and position.get('uik') and position.get('region_id') and \
       position.get('region_id') == region_id:
        _rebuild_forms('local_forms')


def get_mo_list_success(result, region_id):
    filename = 'mo_%s.json' % region_id
    with open(join(App.user_data_dir, filename), 'w+') as f:
        f.write(json.dumps(result))

    _refresh_mo()


def get_changelog_success(result):
    #import ipdb; ipdb.sset_trace()
    vstring = u'Версия %s' % App.version[0:3]
    if vstring not in result:
        return

    try:
        before, after = result.split(vstring)

        changelog = '\n'.join(before.split('\n')[4:])  # skip first 4 lines of the file
        if changelog.strip():
            show_new_version_dialog(changelog)
    except:
        pass
