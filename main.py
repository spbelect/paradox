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

import kivy
#from typing import Dict, List
#from pydantic import BaseModel, ValidationError

import paradox
from paradox import config
from paradox import exception_handler
#from util import delay
from label import Label
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
# dumbdbm on SD card (FAT) devices, tries to use chmod, resulting in
# error. This monkey-patch workarounds the issue.
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

from django import conf
from django.core import management

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
    #errors = ListProperty([])
    app_has_started = False

    #def build_config(self, config):
        #config.setdefaults('kivy', {'keyboard_mode': 'system',})

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        logger.debug(f'ParadoxApp created: {self}')
        
    def build(self):
        #import ipdb; ipdb.sset_trace()
        Clock.max_iteration = 1000
        #print(Clock.max_iteration)
        #if platform == 'android':
            #from jnius import autoclass
            #autoclass('org.kivy.android.PythonActivity').mActivity.removeLoadingScreen()
            
        try:
            logger.info('Build started')
            #state.user_data_dir = self.user_data_dir
            #for filename in glob('forms_*.json') + ['regions.json', 'mo_78.json']:
                #path = join(self.user_data_dir, filename)
                #if not exists(path):
                    #logger.debug('copying %s to %s' % (filename, self.user_data_dir))
                    #copyfile(filename, path)

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
                paradox.exception_handler.send_debug_message(repr(e))
            except:
                pass

            logger.error(repr(e))
            from kivy.uix.label import Label

            self.label = Label()
            self.label.text_size = Window.width - 20, None
            self.label.halign = 'center'
            self.label.color = (155,55,55,1)
            self.label.text = u'Произошла ошибка. Разработчики были уведомлены об этом.'
            return self.label

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

        
    #def run(self):
        #""" Launches the app in standalone mode. """
        ##super().run()
        #logger.info('ParadoxApp.run() finished')
        
        
    async def async_run(self, async_lib=None):
        
        loop = asyncio.get_running_loop()
        loop.set_exception_handler(paradox.exception_handler.aioloop_exc_handler)

        kivy.base.ExceptionManager.add_handler(paradox.exception_handler.KivyExcHandler())
        
        from kivy.base import async_runTouchApp
        #async with trio.open_nursery() as nursery:
            #state._nursery = nursery
        #Clock.init_async_lib('asyncio')
        self._run_prepare()
        
        await async_runTouchApp()
        
        logger.info('App about to exit')
        self.stop()
        logger.info('App stopped')
        
        # TODO: https://bugs.python.org/issue36709
        # Asyncio SSL keep-alive connections raise errors after loop close.
        asyncio.get_running_loop().stop()


from paradox import uix
from paradox import client


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

mock_quiz_topics = [{
    "id": "14bf4a0a-30f4-4ed2-9bcb-9a16a65033d7",
    "elections": None,
    "name": "НАЧАЛО ПОДСЧЕТА",
    "questions": [
      {
        "id": "ecc1deb3-5fe7-48b3-a07c-839993e4563b",
        "label": "Неиспользованные бюллетени убраны в сейф или лежат на видном месте.",
        "fz67_text": "ст.456 п.2 Неиспользованные бюллетени бла бла бла\n",
        "type": "YESNO",   # тип да\нет
        "incident_conditions": { "answer_equal_to": False },
        "example_uik_complaint": "жалоба: бла бла"
      },
      {
        "id": "b87436e0-e7f2-4453-b364-a952c0c7842d",
        "label": "Число проголосаваших досрочно",
        "fz67_text": "ст.123 п.9 Число проголосаваших досрочно бла бла бла\n",
        "type": "NUMBER",  # тип число
        "incident_conditions": { "answer_greater_than": 100 },
        "visible_if": {
            "elect_flags": ["dosrochka"],  # показать только если есть активная кампания с досрочкой
        },
        "example_uik_complaint": "жалоба: бла бла"
      },
      {
        "id": "77532eb3-5fe7-48b3-a07c-cd9b35773709",
        "label": "Все досрочные бюллетени считаются отдельно.",
        "type": "YESNO",
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
  },
]
      
@uix.homescreen.show_loader
async def on_start(app):
    logger.info(f"Using db {django.conf.settings.DATABASES['default']}")
    
    await sleep(0.2)
    logger.info('Start migration.')
    django.core.management.call_command('migrate')
    logger.info('Finished migration.')
    await sleep(0.1)
    
    
    # Initialize application state
    state._server_ping_success = asyncio.Event()
    state._server_ping_success.set()  # Assume success on app start.
    
    statefile = join(app.user_data_dir, 'state.db.shelve')
    logger.info(f'Reading state from {statefile}')
    state.autopersist(statefile)
    if 'country' not in state:
        logger.info('Creating default state.')
    
    state.setdefault('app_id', randint(10 ** 19, 10 ** 20 - 1))
    state.setdefault('profile', {})    
    state.setdefault('country', 'ru')
    state.setdefault('superior_ik', 'TIK')
    state.setdefault('tik', None)
    state.setdefault('regions', {})
    
    # Dict of questions by id { question.id: {"label": "", "type": "", ...}, ... }
    state.setdefault('questions', {})
    
    # Dict of lists of quiz_topics by country. Topics list for each country is ordered.
    state.setdefault('quiz_topics', {'ru': [], 'ua': [], 'kz': [], 'by': []})
    
    if not state.server:
        await client.get_server()
    
    await sleep(0.2)
    
    
    asyncio.create_task(client.check_new_version_loop())
    
    uix.homescreen.build_topics()
    uix.events_screen.restore_past_events()
    logger.info('Restored past events.')
    
    
    logger.info('Updating questions.')
    
    #quiz_topics = mock_quiz_topics
    quiz_topics = (await client.recv_loop(f'{state.country}/questions/')).json()
    #logger.info(quiz_topics)
    #quiz_topics = {'ru': json.load(open('forms_general.json'))}
    
    # Update state.questions - build dict by id for all questions of all received quiz_topics.
    for topic in quiz_topics:
        try:
            state.questions.update({q['id']: q for q in topic['questions']})
        except Exception as e:
            logger.error(repr(e))
            uix.float_message.show('Ошибка при обновлении анкет')
            uix.homescreen.ids.messages.add_widget(Label(
                text='Ошибка при обновлении анкет. Возможно вы используете старую версию программы.'    
            ))
            paradox.exception_handler.send_debug_message(e)
            return
            
    # Build each question dependants list - i.e. list of questions that may be
    # hidden or displayed depending on the answer to the current question.
    # This is the reverse of `limiting_questions` list, used in uix.quiz_widgets.base
    for dependant_question in state.questions.values():
        rules = dependant_question.get('visible_if', {}).get('limiting_questions', {})
        for rule in (rules.get('any') or rules.get('all') or []):
            # Parent (limiting_question).
            parent = state.questions.get(rule.question_id, {})
            # Add this dependant_question to the `dependants` list of its parent.
            parent.setdefault('dependants', []).append(dependant_question['id'])
        
    # Update topics for current country.
    if not state.quiz_topics.get(state.country) == quiz_topics:
        state.quiz_topics[state.country] = quiz_topics
        uix.homescreen.build_topics()
    
    #regions = mock_regions
    regions = (await client.recv_loop(f'{state.country}/regions/')).json()
    ###regions = {f'ru_{x["id"]}': dict(x, id=f'ru_{x["id"]}') for x in json.load(open('regions.json'))}
        
    #logger.debug(regions)
    state.regions.update(regions)
    logger.info('Regions updated.')
    if state.region.id:
        if not state.region == state.regions.get(state.region.id):
            logger.debug(f'Setting region to {state.region.id}')
            state.region = state.regions.get(state.region.id)
    
    uix.events_screen.restore_past_events()
    logger.info('Restored past events (fin).')
    
    asyncio.create_task(client.answer_send_loop())
    asyncio.create_task(client.answer_image_send_loop())
    app.app_has_started = True
    logger.info('Startup finished.')

    
if __name__ == '__main__':
    logger.info('__main__ started')
    app = ParadoxApp()
    asyncio.run(app.async_run())

