#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import shelve
import sys
import traceback

from datetime import datetime
from glob import glob
from hashlib import md5
from os.path import join, exists
from random import randint
from shutil import copyfile

from kivy.utils import platform

from kivy.config import Config
if platform in ['linux', 'windows']:
    Config.set('kivy', 'keyboard_mode', 'system')

from kivy.base import ExceptionManager
from kivy.properties import ListProperty
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.resources import resource_add_path
from requests import post
from tinydb import TinyDB

from paradox import config



if getattr(sys, 'frozen', False):
    # we are running in a PyInstaller windows bundle
    bundle_dir = sys._MEIPASS
    logging.info(bundle_dir)
else:
    # we are running in a normal Python environment
    bundle_dir = os.path.dirname(os.path.abspath(__file__))


class ParadoxApp(App):
    errors = ListProperty([])

    #def build_config(self, config):
        #config.setdefaults('kivy', {
            #'keyboard_mode': 'system',
        #})

    def build(self):
        try:
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

            App.app_store = shelve.open(join(App.user_data_dir, 'app_store.db.shelve'))
            App.inputs = shelve.open(join(App.user_data_dir, 'inputs.db.shelve'))
            App.event_store = TinyDB(join(App.user_data_dir, 'events.json'))
            App.regions = {}

            if not App.app_store.get(b'app_id'):
                App.app_store[b'app_id'] = randint(10 ** 19, 10 ** 20 - 1)
                App.app_store.sync()

            position = App.app_store.get(b'position', {})
            position.setdefault('region_id', '78')
            App.app_store[b'position'] = position


            from paradox.net import SentrySendQueue, SendQueue, GetQueue
            App.send_queue = SendQueue('primary', join(App.user_data_dir, 'send_queue.json'))
            App.send_queue_backup = SendQueue('backup', join(App.user_data_dir, 'send_queue_bak.json'))
            App.send_queue_sentry = SentrySendQueue(join(App.user_data_dir, 'send_queue_sentry.json'))
            App.get_queue = GetQueue()

            from paradox.uix.main_widget import MainWidget
            App.root = MainWidget()
            App.screens = App.root.ids['screens']
            return App.root
        except Exception as e:
            _traceback = traceback.format_exc()
            if config.DEBUG:
                print _traceback
            if isinstance(_traceback, str):
                _traceback = _traceback.decode('utf-8')

            try:
                app_id = App.app_store[b'app_id']
            except:
                app_id = 'xz'

            post('https://spbelect2.herokuapp.com/errors/', json={
                'app_id': app_id,
                'hash': md5(_traceback).hexdigest(),
                'timestamp': datetime.utcnow().isoformat(),
                'traceback': _traceback
            })
            from kivy.uix.label import Label
            self.label = Label()
            self.label.text = u'Произошла ошибка. Разработчики были уведомлены об этом.'
            return self.label

    def build_error_screen(self, msg):
        from paradox.uix.screens.error_screen import ErrorScreen
        scr = ErrorScreen(message=msg)
        Clock.schedule_once(lambda *a: Window._set_size((Window.width, Window.height + 1)))
        return scr

    def on_pause(self):
        print 'PAUSE'
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
            print _traceback
        if isinstance(_traceback, str):
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


if __name__ == '__main__':
    ParadoxApp().run()
