#!/usr/bin/env python
# -*- coding: utf-8 -*-


import asyncio
import logging
import json
import os
import shelve
import sys
import time
import traceback

from kivy.config import Config
#Config.set('graphics', 'multisamples', '0')
Config.set('kivy', 'log_level', 'debug')

os.environ['KIVY_EVENTLOOP'] = 'async'

from datetime import datetime
from glob import glob
from hashlib import md5
from os.path import join, exists, dirname, expanduser
from random import randint
from shutil import copyfile

import django
from app_state import state, on
from kivy.app import App
from kivy.base import ExceptionManager
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import ListProperty
from kivy.resources import resource_add_path
from kivy.utils import platform
from lockorator.asyncio import lock_or_exit
from loguru import logger

from paradox import config
#from util import delay
import label
import button

#import trio
#import asks
#os.environ['KIVY_EVENTLOOP'] = 'trio'
#asks.init('trio')

if platform in ['linux', 'windows']:
    Config.set('kivy', 'keyboard_mode', 'system')
    Window.size = (420, 800)

#Window.softinput_mode = 'below_target'
#Window.softinput_mode = 'pan'

# https://github.com/kuri65536/python-for-android/issues/71
def chmod(*a, **kw):
    pass
os.chmod = chmod


if platform == 'android':
    from jnius import autoclass, cast
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    context = cast('android.content.Context', PythonActivity.mActivity)
    file_p = cast('java.io.File', context.getFilesDir())
    os.environ['DBDIR'] = file_p.getAbsolutePath()
else:
    data_dir = os.environ.get('XDG_CONFIG_HOME', '~/.config')
    os.environ['DBDIR'] = expanduser(join(data_dir, 'paradox'))
    

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_settings")
django.setup()

if platform == 'linux':
    if 'TZ' in os.environ:
        del os.environ['TZ']  # use local timezone instead of django default setting
    time.tzset()


if getattr(sys, 'frozen', False):
    # we are running in a PyInstaller windows bundle
    bundle_dir = sys._MEIPASS
    logging.info(bundle_dir)
else:
    # we are running in a normal Python environment
    bundle_dir = os.path.dirname(os.path.abspath(__file__))

resource_add_path(join(bundle_dir, 'paradox/uix/'))

Builder.load_file('base.kv')

state._config = config


class ParadoxApp(App):
    errors = ListProperty([])

    #def build_config(self, config):
        #config.setdefaults('kivy', {'keyboard_mode': 'system',})

    def build(self):
        ExceptionManager.add_handler(self)
        try:

            logger.info('Build started')
            state.user_data_dir = self.user_data_dir
            for filename in glob('forms_*.json') + ['regions.json', 'mo_78.json']:
                path = join(self.user_data_dir, filename)
                if not exists(path):
                    logger.debug('copying %s to %s' % (filename, self.user_data_dir))
                    copyfile(filename, path)

            ####state._nursery.start_soon(on_start)
            asyncio.create_task(on_start(self))
            
            from paradox.uix.main_widget import MainWidget
            return MainWidget()
        
            #from label import Label
            ##from kivy.uix.label import Label
            #from button import Button

            ###if platform in ['linux', 'windows']:
                ###Window.size = (420, 800)

            #self.label = Label()
            ##self.label.text_size = Window.width - 20, None
            ##self.label.halign = 'center'
            #self.label.text = 'lolol'
            #self.label.color = (55,0,50,0)
            #self.label.size = (100,100)
            #self.label.background_color = (255,255,0)
            ##raise Exception('00')
            #return Button(text='lol')
            #return self.label
        except Exception as e:
            _traceback = traceback.format_exc()
            if config.DEBUG:
                print(_traceback)
            if isinstance(_traceback, bytes):
                _traceback = _traceback.decode('utf-8')

            try:
                app_store = shelve.open(join(self.user_data_dir, 'app_store.db.shelve'))
                app_id = app_store['app_id']
            except:
                app_id = 'xz'

            #post('https://xz.herokuapp.com/errors/', json={
                #'app_id': app_id,
                #'hash': md5(_traceback.encode('utf-8')).hexdigest(),
                #'timestamp': datetime.utcnow().isoformat(),
                #'traceback': _traceback
            #})
            from kivy.uix.label import Label

            if platform in ['linux', 'windows']:
                Window.size = (420, 800)

            self.label = Label()
            self.label.text_size = Window.width - 20, None
            self.label.halign = 'center'
            self.label.text = u'Произошла ошибка. Разработчики были уведомлены об этом.'
            return self.label

    def build_error_screen(self, msg):
        from paradox.uix.screens.error_screen import ErrorScreen
        scr = ErrorScreen(message=msg)
        Clock.schedule_once(lambda *a: Window._set_size((Window.width, Window.height + 1)))
        return scr

    def on_pause(self):
        print('PAUSE')
        #try:
            #self.screens.on_pause()
        #except:
            #self.handle_exception(self, None)
        return True

    #def on_resume(self):
        #self.screens.on_resume()
        #pass

    def handle_exception(self, err):
        #import ipdb; ipdb.sset_trace()
        _traceback = traceback.format_exc()
        if config.DEBUG:
            print(_traceback)
        if isinstance(_traceback, bytes):
            _traceback = _traceback.decode('utf-8')
        self.errors.append(_traceback)
        message = u'\n-----\n'.join(self.errors)
        
        uix.screenmgr.show_error_screen(message)
        #if config.SENTRY and hasattr(App, 'send_queue_sentry'):
            #App.send_queue_sentry.add_trace(message)
        return ExceptionManager.PASS

    #def excepthook(self, type, value, tb):
        #''' if you set sys.excepthook to this function - it will log all exceptions
            #to log only some functions you may use log_trace decorator instead
        #'''
        #_traceback = "".join(traceback.format_exception(type, value, tb))
        #self.root.switch_to(ErrorScreen(message=_traceback, name='error'))
        ##log_exception(value, tb_msg)
        
    def run(self):
        '''Launches the app in standalone mode.
        '''
        super().run()
        logger.info('Paradox finished')
        
    async def async_run(self):
        from kivy.base import async_runTouchApp
        #async with trio.open_nursery() as nursery:
            #state._nursery = nursery
        self._run_prepare()
        
        await async_runTouchApp()
        #logger.info('Cancelling async tasks')
        #nursery.cancel_scope.cancel()
        logger.info('App about to exit')
        self.stop()
        logger.info('App stopped')
        
        #asyncio.get_running_loop().stop()


from paradox import uix
from paradox import client

from django.core.management import call_command

mock_forms = {'ru': [{
    "inputs": [
      {
        "help_text": "aoejgoa \n",
        "input_type": "MULTI_BOOL",
        "input_id": "ecc1deb3-5fe7-48b3-a07c-839993e4563b",
        "label": "Неиспользованные бюллетени убраны в сейф или лежат на видном месте.",
        "alarm": { "eq": False },
        "example_uik_complaint": "это пример"
      },
      {
        "help_text": "pwijgpw \n",
        "input_type": "MULTI_BOOL",
        "input_id": "b87436e0-e7f2-4453-b364-a952c0c7842d",
        "label": "Этот только досрочка",
        "elect_flags": ["dosrochka"],
        "example_uik_complaint": "это пример"
      }
    ],
    "form_id": "14bf4a0a-30f4-4ed2-9bcb-9a16a65033d7",
    "elections": None,
    "form_type": "GENERAL",
    "name": "НАЧАЛО ПОДСЧЕТА"
  },
]}
      
@uix.formlist.show_loader
async def on_start(app):
    logger.info('Start migration.')
    call_command('migrate')
    logger.info('Finished migration.')
    
    statefile = join(app.user_data_dir, 'state.db.shelve')
    logger.info(f'Reading state from {statefile}')
    state.autopersist(statefile)

    state.setdefault('app_id', randint(10 ** 19, 10 ** 20 - 1))
    state.setdefault('profile', {})
    
    #formdata = await client.recv_loop(f'/forms/general/')
    #formdata = {'ru': json.load(open('forms_general.json'))}
    formdata = mock_forms
    
    state.setdefault('country', 'ru')
    state.setdefault('inputs', {})
    for country in formdata:
        for form in formdata[country]:
            for input in form['inputs']:
                state.inputs[input['input_id']] = input
            
    state.setdefault('forms', {})
    if not state.forms.get('general') == formdata:
        state.forms.general = formdata
    uix.formlist.build_general()
    
    #state.regions = await client.recv_loop('/regions/')
    state.regions = {f'ru_{x["id"]}': dict(x, id=f'ru_{x["id"]}') for x in json.load(open('regions.json'))}
    
    uix.events_screen.restore_past_events()
    
    logger.info('Restored past events.')
    await client.update_campaigns()
    await client.send_position()
    ##await client.send_userprofile()
    asyncio.create_task(client.event_send_loop())
    asyncio.create_task(client.event_image_send_loop())
    logger.info('Startup finished.')

    
def z(filename):
    import os, google.auth
    from google.auth.transport import requests
    from google.auth import compute_engine
    from datetime import datetime, timedelta
    from google.cloud import storage

    #auth_request = 
    credentials, project = google.auth.default()
    storage_client = storage.Client(project, credentials)
    signed_blob_path = storage_client.lookup_bucket('ekc-uploads').blob(filename)
    expires_at_ms = datetime.now() + timedelta(minutes=3600)
    # This next line is the trick!
    signing_credentials = compute_engine.IDTokenCredentials(requests.Request(), "", service_account_email=credentials.service_account_email)
    return signed_blob_path.generate_signed_url(expires_at_ms, credentials=signing_credentials, version="v4")


async def x():
    from google.cloud import storage

    # If you don't specify credentials when constructing the client, the
    # client library will look for credentials in the environment.
    storage_client = storage.Client()

    # Make an authenticated API request
    buckets = list(storage_client.list_buckets())
    print(buckets)
    

    import requests_async as requests
    #import requests
    su = z('123.jpeg')
    print(su)
    res = await requests.post(su, 
                  files={'file': ('123.jpeg', open('Screenshot_20190112_132357.jpeg', 'rb'))})
    print(res.content)
    res.raise_for_status()
    print('ok')
    
async def xb():
    import paradox.utils
    import requests_async as requests
    md5 = paradox.utils.md5_file('4.jpg')
    try:
        response = await requests.post('http://8.8.8.8:8000/api/v1/upload_request/', timeout=0.1, json={
            'filename': md5 + '-4.jpeg',
            'md5': md5,
            'content-type': 'image/jpeg'
        })
    except requests.Timeout as e:
        logger.debug(repr(e))
        #get_server()
    except (requests.ProxyError, requests.SSLError) as e:
        logger.debug(repr(e))
    except requests.ConnectionError as e:
        #import ipdb; ipdb.sset_trace()
        #if e.args and isinstance(e.args[0], OSError):
            #if e.args[0].errno
        logger.debug(repr(e))
    except Exception as e:
        logger.debug(repr(e))
        return
    print(1)
    response.raise_for_status()
    #import ipdb; ipdb.sset_trace()
    response = response.json()
    #import requests
    res = await requests.post(response['url'], data=response['fields'], 
                  files={'file': ('4.jpeg', open('4.jpg', 'rb'))})
    print(res.content)
    res.raise_for_status()
    print('ok')

if __name__ == '__main__':
    app = ParadoxApp()
    asyncio.run(app.async_run())
    #app.run()
    #trio.run(ParadoxApp().async_run)
    #asyncio.run(xb())
