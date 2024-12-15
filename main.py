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

import logging_setup

from kivy.config import Config
Config.set('graphics', 'multisamples', '0')
#Config.set('kivy', 'log_level', 'debug')

os.environ['KIVY_EVENTLOOP'] = 'asyncio'
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
    use_kivy_settings = False
    #errors = ListProperty([])
    app_has_started = False

    #def build_config(self, config):
        #config.setdefaults('kivy', {'keyboard_mode': 'system',})

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        logger.debug(f'ParadoxApp created: {self}')


    def _build(self):
        Clock.max_iteration = 1000

        # Initialize application state
        state._server_ping_success = asyncio.Event()
        state._server_ping_success.set()  # Assume success on app start.

        # import ipdb; ipdb.sset_trace()
        if 'country' not in state:
            logger.info('Creating default state.')

        state.setdefault('server', None)
        state.setdefault('app_id', randint(10 ** 19, 10 ** 20 - 1))
        state.setdefault('profile', {})
        state.setdefault('country', 'ru')
        state.setdefault('superior_ik', 'TIK')
        state.setdefault('tik', None)
        state.setdefault('uik', None)
        # state.setdefault('role', None)
        state.setdefault('role', 'prg')
        state.setdefault('munokrug', {})
        state.setdefault('region', {})
        state.setdefault('regions', {})

        # Dict of questions by id { question.id: {"label": "", "type": "", ...}, ... }
        state.setdefault('questions', {})

        # Dict of lists of quiz_topics by country. Topics list for each country is ordered.
        state.setdefault('quiz_topics', {'ru': [], 'ua': [], 'kz': [], 'by': []})

        from paradox import uix
        Window.bind(on_keyboard=uix.screenmgr.hook_keyboard)

        import main_task
        asyncio.create_task(main_task.main(self))

        #if platform == 'android':
            #from jnius import autoclass
            #autoclass('org.kivy.android.PythonActivity').mActivity.removeLoadingScreen()

        #state.user_data_dir = self.user_data_dir
        #for filename in glob('forms_*.json') + ['regions.json', 'mo_78.json']:
            #path = join(self.user_data_dir, filename)
            #if not exists(path):
                #logger.debug('copying %s to %s' % (filename, self.user_data_dir))
                #copyfile(filename, path)

        ####state._nursery.start_soon(on_start)


    def build(self):
        logger.info('Build started')
        try:
            self._build()

            from paradox.uix.main_widget import MainWidget
            return MainWidget()
        except Exception as e:
            try:
                paradox.exception_handler.send_debug_message(repr(e))
            except:
                pass

            logger.error(repr(e))

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
        asyncio.get_running_loop().stop()


    def open_settings(self, *largs):
        # Don't open default settings provided by kivy app
        pass

    
if __name__ == '__main__':
    logger.info('__main__ started')
    app = ParadoxApp()
    asyncio.run(app.async_run())

