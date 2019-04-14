#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import logging
import os
import shelve
import sys
import traceback

from app_state import state, on
from datetime import datetime
from glob import glob
from hashlib import md5
from lockorator import lock_or_exit
from os.path import join, exists
from random import randint
from shutil import copyfile

import trio
import asks
os.environ['KIVY_EVENTLOOP'] = 'trio'
asks.init('trio')

from kivy.utils import platform

from kivy.config import Config
if platform in ['linux', 'windows']:
    Config.set('kivy', 'keyboard_mode', 'system')

import kivy.uix.widget

from kivy.base import ExceptionManager
from kivy.properties import ListProperty
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.resources import resource_add_path
from requests import post
#from tinydb import TinyDB

from paradox import config
from util import delay




if getattr(sys, 'frozen', False):
    # we are running in a PyInstaller windows bundle
    bundle_dir = sys._MEIPASS
    logging.info(bundle_dir)
else:
    # we are running in a normal Python environment
    bundle_dir = os.path.dirname(os.path.abspath(__file__))


#from kivy.lang import Builder

#def load_later(string):
    #App.nursery.start_soon(load_async, string)
    
    
#async def load_async(string):
    ##import ipdb; ipdb.sset_trace()
    #print('load')
    #Builder.load_string(string)
    
#Builder.load_later = load_later


real_init = kivy.uix.widget.Widget.__init__

#async def delayed_init(self):
    ##print(self)
        #await self.init()
    
def _init(self, *a, **kw):
    #kw['__no_builder'] = True
    real_init(self, *a, **kw)
    #if hasattr(self, 'kv'):
        #Builder.load_string(self.kv)
        #Builder.apply(self)
        #Clock.schedule_once(lambda *a: self.init())
        
    if hasattr(self, 'init'):
        delay(self.init)

    
kivy.uix.widget.Widget.__init__ = _init



class ParadoxApp(App):
    errors = ListProperty([])

    #def build_config(self, config):
        #config.setdefaults('kivy', {
            #'keyboard_mode': 'system',
        #})

    def build(self):
        try:
            #import ipdb; ipdb.sset_trace()
            
            os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_settings")
            import django
            django.setup()

            App.nursery = self.nursery
            
            import kivy_scheduler
            kivy_scheduler.prefix = 'paradox.'
            
            logging.info( 'AAAAAAAAAAAAAAAAAAAAAAAAA')
            resource_add_path(join(bundle_dir, 'paradox/uix/'))
            App.version = self.version = config.version
            App.user_data_dir = self.user_data_dir
            
            if platform in ['linux', 'windows']:
                Window.size = (420, 800)

            Window.softinput_mode = 'below_target'

            #Window.softinput_mode = 'pan'

            for filename in glob('forms_*.json') + ['regions.json', 'mo_78.json']:
                path = join(App.user_data_dir, filename)
                if not exists(path):
                    print('copying %s to %s' % (filename, App.user_data_dir))
                    copyfile(filename, path)

            # https://github.com/kuri65536/python-for-android/issues/71
            def chmod(*a, **kw):
                pass
            os.chmod = chmod

            state.autopersist(join(App.user_data_dir, 'state.db.shelve'), nursery=App.nursery)

            if not state.get('app_id'):
                state['app_id'] = randint(10 ** 19, 10 ** 20 - 1)

            state.setdefault('country', 'ru')
            state.setdefault('regions', {
                'ru_78': {'id': 'ru_78', 'name': 'Санкт-Петербург'},
                'ru_47': {'id': 'ru_47', 'name': 'ЛО'}})
            state.setdefault('region', state.regions.ru_47)

            from paradox.uix.main_widget import MainWidget
            #import ipdb; ipdb.sset_trace()
            
            App.root = MainWidget()
            
            return App.root
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

            #post('https://spbelect2.herokuapp.com/errors/', json={
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
        try:
            self.screens.on_pause()
        except:
            self.handle_exception(self, None)
        return True

    def on_resume(self):
        self.screens.on_resume()
        #pass

    def handle_exception(self, err):
        _traceback = traceback.format_exc()
        if config.DEBUG:
            print(_traceback)
        if isinstance(_traceback, bytes):
            _traceback = _traceback.decode('utf-8')
        self.errors.append(_traceback)
        message = u'\n-----\n'.join(self.errors)
        if hasattr(App, 'screens'):
            App.screens.show_error_screen(message)
        if config.SENTRY and hasattr(App, 'send_queue_sentry'):
            App.send_queue_sentry.add_trace(message)
        return ExceptionManager.PASS

    def run(self):
        #try:
        ExceptionManager.add_handler(self)
        super(ParadoxApp, self).run()
        #except Exception as e:
            #msg = traceback.format_exc()
            #print msg
            #for ch in Window.children:
                #Window.remove_widget(ch)
            ##from kivy import lang
            ##lang._delayed_start = None
            #Clock._events = [[] for i in range(256)]

            #self.built = False
            #self.build = lambda *a: self.build_error_screen(msg)
            ##from kivy.uix.label import Label
            ##self.build = lambda *a: Label(text=msg, color=(1,1,1,1))
            #super(DemoApp, self).run()



    #def excepthook(self, type, value, tb):
        #''' if you set sys.excepthook to this function - it will log all exceptions
            #to log only some functions you may use log_trace decorator instead
        #'''
        #_traceback = "".join(traceback.format_exception(type, value, tb))
        #self.root.switch_to(ErrorScreen(message=_traceback, name='error'))
        ##log_exception(value, tb_msg)

    #def on_start(self):
        #sys.excepthook = self.excepthook
        
    async def async_run(self):
        '''Identical to :meth:`run`, but is a coroutine and can be
        scheduled in a running async event loop.

        .. versionadded:: 1.10.1
        '''
        from kivy.base import async_runTouchApp
        async with trio.open_nursery() as nursery:
            self.nursery = nursery
            self._run_prepare()
            await async_runTouchApp()
        self.stop()

if __name__ == '__main__':
    trio.run(ParadoxApp().async_run)
