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
Config.set('graphics', 'multisamples', '0')
#Config.set('kivy', 'log_level', 'debug')

os.environ['KIVY_EVENTLOOP'] = 'asyncio'
os.environ['LOGURU_AUTOINIT'] = '0'
#os.environ['KIVY_PROFILE_LANG'] = '1'

from asyncio import sleep
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

logger.add(sys.stderr, colorize=True)
state._appstate_autocreate = True

#from typing import Dict, List
#from pydantic import BaseModel, ValidationError

from paradox import config
#from util import delay
import label
import button
import textinput

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


print(f'platform: {platform}')
if platform == 'android':
    from jnius import autoclass, cast
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    context = cast('android.content.Context', PythonActivity.mActivity)
    file_p = cast('java.io.File', context.getFilesDir())
    os.environ['DBDIR'] = file_p.getAbsolutePath()
elif platform == 'win':
    data_dir = join(os.environ['APPDATA'], 'paradox')
    if not exists(data_dir):
        os.mkdir(data_dir)
    os.environ.setdefault('DBDIR', data_dir)
else:
    data_dir = os.environ.get('XDG_CONFIG_HOME', '~/.config')
    os.environ.setdefault('DBDIR', expanduser(join(data_dir, 'paradox')))
    

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



    
    
def handle_traceback(err):
    from requests import post
    from os.path import join
    _traceback = traceback.format_tb(err.__traceback__)
    message = u''.join(_traceback) + '\n' + repr(err) + '\n' + str(err)
    logger.error(message)
    try:
        server = state.get('server', config.SERVER_ADDRESS)
        post(join(server, 'api/v2/errors/'), json={
            'app_id': state.get('app_id', '666'),
            #'hash': md5(_traceback.encode('utf-8')).hexdigest(),
            'timestamp': datetime.utcnow().isoformat(),
            'traceback': message
        })
    except:
        pass
    uix.screenmgr.show_error_screen(message)
    
    
def exchook(type, err, traceback):
    #import ipdb; ipdb.sset_trace()
    if str(err) == 'Event loop stopped before Future completed.':
        return
    handle_traceback(err)
    
def aexc_handler(loop, context):
    # TODO: 
    # File "/home/u1/.local/share/python-for-android/build/other_builds/python3-libffi-openssl-sqlite3/arm64-v8a__ndk_target_21/python3/Lib/ssl.py", line 763, in do_handshake
    # SSLZeroReturnError(6, 'TLS/SSL connection has been closed (EOF) (_ssl.c:1051)')
    # TLS/SSL connection has been closed (EOF) (_ssl.c:1051)
    # 
    # TODO: which one is https://bugs.python.org/issue36709 ?
    #‘message’: Error message;
    #‘exception’ (optional): Exception object;
    #‘future’ (optional): asyncio.Future instance;
    #‘handle’ (optional): asyncio.Handle instance;
    #‘protocol’ (optional): Protocol instance;
    #‘transport’ (optional): Transport instance;
    #‘socket’ (optional): socket.socket instance.
    logger.info(context['message'])
    if 'write error on socket transport' in context['message']:
        return
    if context['message'] in [
        'Event loop stopped before Future completed.',
        'Task was destroyed but it is pending!']:
        return
    handle_traceback(context['exception'])
    
    
sys.excepthook = exchook

class ParadoxApp(App):
    errors = ListProperty([])
    app_has_started = False

    #def build_config(self, config):
        #config.setdefaults('kivy', {'keyboard_mode': 'system',})

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        #import ipdb; ipdb.sset_trace()
        logger.debug(f'ParadoxApp created: {self}')
        
    def build(self):
        #import ipdb; ipdb.sset_trace()
        ExceptionManager.add_handler(self)
        Clock.max_iteration = 1000
        #print(Clock.max_iteration)
        #if platform == 'android':
            #from jnius import autoclass
            #autoclass('org.kivy.android.PythonActivity').mActivity.removeLoadingScreen()
            
        try:
            loop = asyncio.get_running_loop()
            loop.set_exception_handler(aexc_handler)

            logger.info('Build started')
            state.user_data_dir = self.user_data_dir
            for filename in glob('forms_*.json') + ['regions.json', 'mo_78.json']:
                path = join(self.user_data_dir, filename)
                if not exists(path):
                    logger.debug('copying %s to %s' % (filename, self.user_data_dir))
                    copyfile(filename, path)

            ####state._nursery.start_soon(on_start)
            asyncio.create_task(on_start(self))
            
            Window.bind(on_keyboard=uix.screenmgr.hook_keyboard)
            
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
            try:
                handle_traceback(e)
            except:
                pass

            from kivy.uix.label import Label

            if platform in ['linux', 'windows']:
                Window.size = (420, 800)

            self.label = Label()
            self.label.text_size = Window.width - 20, None
            self.label.halign = 'center'
            self.label.color = (155,55,55,1)
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
        handle_traceback(err)
        return ExceptionManager.PASS

        
    def run(self):
        '''Launches the app in standalone mode.
        '''
        super().run()
        logger.info('ParadoxApp.run() finished')
        
    async def async_run(self):
        #import ipdb; ipdb.sset_trace()
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
        
        # TODO: https://bugs.python.org/issue36709
        # Asyncio SSL keep-alive connections raise errors after loop close.
        asyncio.get_running_loop().stop()


from paradox import uix
from paradox import client

from django.core.management import call_command

mock_regions = {
    'ru_47': {
        'id': 'ru_47',
        'name': 'Лен. обл.',
        'tiks': [
            {
                'id': '68b7a-2533d-8dd43',
                'uik_ranges': [[21,800]],
                'name': 'Tik kingiseppskogo rayona',
                'email': 'tik-kingiseppskogo@lo.ru',
                'phone': '72727',
                'address': 'street 35'
            },
        ],
        'munokruga': [],
    },
    'ru_78': {
        'id': 'ru_78',
        'name': 'Spb',
        'tiks': [
            {
                'id': 'f8e424-235b-77a8a',
                'uik_ranges': [[21,800]],
                'name': 'Tik 7',
                'email': 'tik7@x.ru',
                'phone': '6463',
                'address': 'ulitsa 77'
            },
        ],
        'munokruga': [
            {
                'id': '6ab3-d1c23',
                'uik_ranges': [[1,100], [4010, 4055]],
                'name': 'Муниципальный округ Дачное',
                'ikmo_email': 'MOlol@x.ru',
                'ikmo_phone': '78796',
                'ikmo_address': 'leninsky 53'
            },
        ],
    }
}

mock_forms = [{
    "questions": [
      {
        "id": "ecc1deb3-5fe7-48b3-a07c-839993e4563b",
        "label": "Неиспользованные бюллетени убраны в сейф или лежат на видном месте.",
        "fz67_text": "ст.456 п.2 Неиспользованные бюллетени бла бла бла\n",
        "input_type": "YESNO",   # тип да\нет
        "incident_conditions": { "answer_equal_to": False },
        "example_uik_complaint": "жалоба: бла бла"
      },
      {
        "id": "b87436e0-e7f2-4453-b364-a952c0c7842d",
        "label": "Число проголосаваших досрочно",
        "fz67_text": "ст.123 п.9 Число проголосаваших досрочно бла бла бла\n",
        "input_type": "NUMBER",  # тип число
        "incident_conditions": { "answer_greater_than": 100 },
        "visible_if": {
            "elect_flags": ["dosrochka"],  # показать только если есть активная кампания с досрочкой
        },
        "example_uik_complaint": "жалоба: бла бла"
      },
      {
        "id": "77532eb3-5fe7-48b3-a07c-cd9b35773709",
        "label": "Все досрочные бюллетени считаются отдельно.",
        "input_type": "YESNO",
        # Считать ответ инцидетом если все заданные условия соблюдены
        "incident_conditions": { "answer_equal_to": False },
        # Показывать этот вопрос в анкете если:
        # - текущие выборы имеют заданные флаги
        # И
        # - даны разрешающие ответы на ограничивающие вопросы
        "visible_if": {
            "elect_flags": ["dosrochka"],  # показать только если есть активная кампания с досрочкой
            "limiting_questions": {
                # Возможные значения:
                # all: [] - все условия в списке должны быть соблюдены
                # any: [] - хотя бы одно условие в списке соблюдено
                "all": [
                    # Возможные условия:
                    # answer_equal_to, answer_greater_than, answer_less_than
                    {
                        "question_id": "ecc1deb3-5fe7-48b3-a07c-839993e4563b", 
                        "answer_equal_to": False
                    },
                    {
                        "question_id": "b87436e0-e7f2-4453-b364-a952c0c7842d", 
                        "answer_greater_than": 100,
                        "answer_less_than": 1000
                    }
                ]
            },
        },
        "example_uik_complaint": "жалоба: бла бла",
        "fz67_text": "ст. 778 ... \n",
      },
    ],
    "form_id": "14bf4a0a-30f4-4ed2-9bcb-9a16a65033d7",
    "elections": None,
    "form_type": "GENERAL",
    "name": "НАЧАЛО ПОДСЧЕТА"
  },
]
      
@uix.formlist.show_loader
async def on_start(app):
    #raise Exception('bb')
    from django.conf import settings
    logger.info(f"Using db {settings.DATABASES['default']}")
    
    await sleep(0.2)
    logger.info('Start migration.')
    call_command('migrate')
    logger.info('Finished migration.')
    await sleep(0.1)
    
    statefile = join(app.user_data_dir, 'state.db.shelve')
    logger.info(f'Reading state from {statefile}')
    state.autopersist(statefile)
    if 'country' not in state:
        logger.info('Creating default state.')
    
    state._server_ping_success = asyncio.Event()
    state._server_ping_success.set()  # Assume success on app start.

    state.setdefault('app_id', randint(10 ** 19, 10 ** 20 - 1))
    state.setdefault('profile', {})    
    state.setdefault('country', 'ru')
    state.setdefault('superior_ik', 'TIK')
    state.setdefault('tik', None)
    state.setdefault('questions', {})
    state.setdefault('regions', {})
    state.setdefault('forms', {'general': {'ru': []}})
    
    if not state.server:
        await client.get_server()
    
    await sleep(0.2)
    
    asyncio.create_task(client.check_new_version_loop())
    
    #state._pending_save_questions = set()
    
    uix.formlist.build_general()
        
    uix.events_screen.restore_past_events()
    logger.info('Restored past events.')
    
    #formdata = (await client.recv_loop(f'{state.country}/forms/')).json()
    #logger.info(formdata)
    #formdata = {'ru': json.load(open('forms_general.json'))}
    formdata = mock_forms
    
    for form in formdata:
        state.questions.update({x['id']: x for x in form['questions']})
            
    for question in state.questions.values():
        #import ipdb; ipdb.sset_trace()
        deps = question.get('visible_if', {}).get('limiting_questions', {})
        for condition in (deps.get('any') or deps.get('all') or []):
            precursor = state.questions.get(condition['question_id'], {})
            precursor.setdefault('dependants', []).append(question['id'])
        
    state.setdefault('forms', {})
    if not state.forms['general'].get(state.country) == formdata:
        state.forms.general[state.country] = formdata
        uix.formlist.build_general()
    
    regions = mock_regions
    #regions = (await client.recv_loop(f'{state.country}/regions/')).json()
    ###regions = {f'ru_{x["id"]}': dict(x, id=f'ru_{x["id"]}') for x in json.load(open('regions.json'))}
        
    #logger.debug(regions)
    state.regions.update(regions)
    logger.info('Regions updated.')
    if state.region:
        if not state.region == state.regions.get(state.region.id):
            logger.debug(f'Setting region to {state.regions.get(state.region.id)}')
            state.region = state.regions.get(state.region.id)
    
    uix.events_screen.restore_past_events()
    logger.info('Restored past events (fin).')
    
    asyncio.create_task(client.answer_send_loop())
    asyncio.create_task(client.answer_image_send_loop())
    app.app_has_started = True
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
    from os.path import basename
    import paradox.utils
    import requests_async as requests
    
    from paradox.models import AnswerImage
    #import paradox.utils
    #import requests_async as requests
    
    #state.app_id='123'
    image = AnswerImage.objects.first()
    md5 = paradox.utils.md5_file('4.jpg')
    try:
        response = await requests.post('http://127.0.0.1:8000/api/v2/upload_request/', timeout=0.1, json={
            'filename': image.md5 + '-4.jpeg',
            'md5': image.md5,
            'content-type': 'image/jpeg'
        })
    except requests.Timeout as e:
        logger.debug(repr(e))
        return
    except (requests.ProxyError, requests.SSLError) as e:
        logger.debug(repr(e))
        return
    except requests.ConnectionError as e:
        #import ipdb; ipdb.sset_trace()
        #if e.args and isinstance(e.args[0], OSError):
            #if e.args[0].errno
        logger.debug(repr(e))
        return
    except Exception as e:
        logger.debug(repr(e))
        return
    print(1)
    response.raise_for_status()
    #import ipdb; ipdb.sset_trace()
    response = response.json()
    #import requests
    res = await requests.post(response['url'], data=response['fields'], 
                  files={'file': ('unused.jpeg', open(image.filepath, 'rb'))})
    print(res.content)
    res.raise_for_status()
    print('ok')


async def upl():
    from os.path import basename
    from paradox.models import AnswerImage
    import paradox.utils
    import requests_async as requests
    
    state.app_id='123'
    image = AnswerImage.objects.first()
    
    #md5 = paradox.utils.md5_file(image.filepath)
    #logger.info(f'{image.md5}, {md5}')
    try:
        response = await client.api_request('POST', 'upload_request/', {
            'filename': image.md5 + basename(image.filepath),
            'md5': image.md5,
            'content-type': 'image/jpeg'
        })
    except Exception as e:
        logger.error(repr(e))
        #image.update(send_status='req_exception')
        return
    if not response.status_code == 200:
        logger.error(repr(response))
        #image.update(send_status=f'req_http_{response.status_code}')
        return
    
    response = s3params = response.json()
    #res = await requests.post(response['url'], data=response['fields'], 
                  #files={'file': ('unused.jpeg', open(image.filepath, 'rb'))})
    #print(res.content)
    #res.raise_for_status()
    #print('ok')
    print(s3params)
    try:
        response = await client.client.post(
            s3params['url'], data=s3params['fields'], 
            files={'file': open(image.filepath, 'rb')}
        )
    except Exception as e:
        logger.error(repr(e))
        #image.update(send_status='upload_exception')
        return
    if not response.status_code == 204:
        logger.error(repr(response))
        logger.error(response.text)
        import ipdb; ipdb.sset_trace()
        #image.update(send_status=f'upload_http_{response.status_code}')
        return
    
if __name__ == '__main__':
    logger.info('__main__ started')
    app = ParadoxApp()
    asyncio.run(app.async_run())
    #app.run()
    #trio.run(ParadoxApp().async_run)
    #asyncio.run(upl())
    #asyncio.run(xb())
