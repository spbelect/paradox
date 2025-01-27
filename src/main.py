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

from paradox import logging_setup

from kivy.config import Config
Config.set('graphics', 'multisamples', '0')
#Config.set('kivy', 'log_level', 'debug')

os.environ['KIVY_EVENTLOOP'] = 'asyncio'
#os.environ['KIVY_PROFILE_LANG'] = '1'

from asyncio import sleep
from datetime import datetime
from glob import glob
from hashlib import md5
from os.path import join, exists, dirname, expanduser, abspath
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
from kivy.utils import platform
from kivy.uix.widget import Widget
from lockorator.asyncio import lock_or_exit
from loguru import logger

state._appstate_autocreate = True

import kivy
import kivy.resources
#from typing import Dict, List
#from pydantic import BaseModel, ValidationError

import paradox
from paradox import config
from paradox import exception_handler
#from util import delay

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
    

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "paradox.django_settings")
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
else:
    # we are running in a normal Python environment
    bundle_dir = dirname(abspath(__file__))

logging.info(f'Adding kivy resources dir {bundle_dir}')
kivy.resources.resource_add_path(join(bundle_dir, 'paradox/uix/'))

Builder.load_file('base.kv')

state._config = config



class ParadoxApp(App):
    use_kivy_settings = False
    #errors = ListProperty([])
    app_has_started = False

    #def build_config(self, config):
        #config.setdefaults('kivy', {'keyboard_mode': 'system',})

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        logger.debug(f'ParadoxApp created: {self}')


    def _build(self) -> Widget:
        Clock.max_iteration = 1000

        # Initialize application state
        state._server_ping_success = asyncio.Event()
        state._server_ping_success.set()  # Assume success on app start.

        logger.info('Creating default state.')

        state.update(dict(
            server = None,
            app_id = randint(10 ** 19, 10 ** 20 - 1),
            profile = {},
            country = 'ru',
            superior_ik = 'TIK',
            tik = None,
            uik = None,
            role = 'prg',
            munokrug = {},
            region = {},
            regions = {},
            # Dict of questions by id { question.id: {"label": "", "type": "", ...}, ... }
            questions = {},
            # Dict of lists of quiz_topics by country. Topics list for each country is ordered.
            quiz_topics = {
                'ru': json.load(open(config.SRCDIR / 'quiz_topics_ru.json')),
                'ua': [],
                'kz': [],
                'by': []
            }
        ))

        import paradox.main_task
        import paradox.uix.main_widget

        asyncio.create_task(paradox.main_task.init(app=self))

        Window.bind(on_keyboard=paradox.uix.screenmgr.hook_keyboard)

        return paradox.uix.main_widget.MainWidget()

        #if platform == 'android':
            #from jnius import autoclass
            #autoclass('org.kivy.android.PythonActivity').mActivity.removeLoadingScreen()


    def build(self) -> Widget:
        logger.info('Build started')

        try:
            return self._build()
        except Exception as err:
            logger.exception(repr(err))
            paradox.exception_handler.send_debug_message(err)

        from kivy.uix.label import Label

        self.label = Label()
        self.label.text_size = Window.width - 20, None
        self.label.halign = 'center'
        # self.label.valign = 'center'
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


    def open_settings(self, *largs):
        pass  # Don't open default settings provided by kivy app

    
if __name__ == '__main__':
    logger.info('__main__ started')
    app = ParadoxApp()
    asyncio.run(app.async_run())

