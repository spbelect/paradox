# -*- coding: utf-8 -*-

from __future__ import unicode_literals
#from os.path import exists
import logging
import json
import traceback
import shelve
import cProfile

import kivy

from app_state import state, on
from loguru import logger
from kivy.app import App
from kivy.base import EventLoop
#from kivy.garden.anchoredscrollview import AnchoredScrollView
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.lang.parser import global_idmap
from kivy.properties import StringProperty
from kivy.properties import ObjectProperty
from kivy.properties import ListProperty
from kivy.properties import BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
#from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix import screenmanager
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.modalview import ModalView
from kivy.uix.vkeyboard import VKeyboard
from kivy.uix.behaviors.button import ButtonBehavior
from kivy.utils import platform
#import plyer

from paradox import uix
from paradox.uix import float_message
from ..vbox import VBox

from .handbook_screen import HandBookScreen
from .communication_screen import CommunicationScreen
from .error_screen import ErrorScreen
from .userprofile_screen import UserProfileScreen
from .position_screen import PositionScreen
from .events_screen import EventsScreen
from .form_screen import FormScreen
from .formlist_screen import FormListScreen
from .about_screen import AboutScreen



Builder.load_string('''
#:include constants.kv

<ScreenManager>:
    canvas.before:
        Color:
            rgba: (4, 4, 9, 1)
        Rectangle:
            pos: self.pos
            size: self.size

''')


class ScreenManager(kivy.uix.screenmanager.ScreenManager):
    screen_history = ListProperty([])
    about_to_exit = BooleanProperty(False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #Clock.schedule_once(self.build_screens)
        #Window.bind(on_keyboard=self.hook_keyboard2)
            #self.init()
            
        #def init(self):
        self.add_widget(uix.formlist)
        self.add_widget(HandBookScreen(name='handbook'))
        #uix.position = PositionScreen(name='position')
        self.add_widget(uix.position)
        self.add_widget(uix.coordinators)
        self.add_widget(uix.events_screen)
        self.add_widget(uix.complaint)
        self.add_widget(AboutScreen(name='about'))
        self.add_widget(CommunicationScreen(name='communication'))
        self.add_widget(uix.userprofile)
        self.push_screen('formlist')
        #self.push_screen('position')
        #schedule('core.screens_initialized')


    def push_screen(self, name):
        self.transition.direction = 'left'
        #if self.current == 'userprofile' and name != 'userprofile':
            #schedule('core.leave_userprofile_screen')
        if self.current == 'position' and name != 'position':
            if self.get_screen('position').show_errors():
                return
            #schedule('core.leave_position_screen')

        if name == 'formlist':
            self.screen_history = []
            self.current = 'formlist'
        elif self.current != name:
            self.screen_history.append(name)
            self.current = name

    def pop_screen(self):
        self.transition.direction = 'right'
        if len(self.screen_history) > 1:
            self.screen_history.pop()
            self.current = self.screen_history[-1]
        elif len(self.screen_history) == 1:
            self.screen_history.pop()
            self.current = 'formlist'

    def on_current(self, *args):
        self.about_to_exit = False
        super().on_current(*args)

    #def hook_keyboard2(self, *args):
        #print args
        #return True

    def hook_keyboard(self, window, key, *args):
        #logging.info( "XXXXXXXXXXXXXXXXX key %d pressed" % key)
        #if platform != 'android':
            #if key == ord('p'):
                #self.profile = cProfile.Profile()
                #self.profile.enable()
            #elif key == ord('o'):
                #self.profile.disable()
                #self.profile.dump_stats('myapp.profile')
        
        if key in (1000, 27, 1073742095, 4):
            #if App.root.state == 'open':
                #App.root.toggle_state()
            if len(self.screen_history) >= 1:
                self.pop_screen()
            elif self.about_to_exit:
                return False
            else:
                self.about_to_exit = True
                uix.float_message.show('Нажмите еще раз для выхода')
        return True

    def show_error_screen(self, message):
        if self.has_screen('error'):
            screen = self.get_screen('error')
            screen.message = message
        else:
            screen = ErrorScreen(message=message, name='error')
            self.add_widget(screen)
        self.current = 'error'

    def show_form(self, form):
        screen_name = f'form_{form["form_id"]}'
        if not self.has_screen(screen_name):
            self.add_widget(FormScreen(form, name=screen_name))

        self.push_screen(screen_name)

    def show_handbook(self, title, text):
        if 'handbook' in self.screen_history:
            self.screen_history.remove('handbook')
        self.get_screen('handbook').show_help(title, text)
        self.push_screen('handbook')
        
    def show_complaint(self, answer):
        if 'complaint' in self.screen_history:
            self.screen_history.remove('complaint')
        self.get_screen('complaint').show(answer)
        self.push_screen('complaint')

    @on('state.uik', 'state.region')
    def remove_formsreens(self):
        self.screen_history = ['formlist']
        #logger.debug(f'{self.screens}')
        for screen in self.screens:
            if screen.name.startswith('form_'):
                self.remove_widget(screen)
                del screen
        import gc
        gc.collect()
        #logger.debug(f'{self.screens}')
        
    def on_pause(self):
        pass
        #self.get_screen('formlist').ids['camera'].play = False

    def on_resume(self):
        pass
        #self.get_screen('formlist').ids['camera'].play = True
