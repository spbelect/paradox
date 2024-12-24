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

import paradox.uix.screens

from . import (
    home, communication, position, quiztopic, userprofile,
    handbook, organizations, events, complaint, about, error
)
# from .communication import CommunicationScreen
# from .error import ErrorScreen
# from .userprofile import UserProfileScreen
# from .position import PositionScreen
# from .events import EventsScreen
# from .quiztopic import QuizTopicScreen
# from .about import AboutScreen



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

        # import ipdb; ipdb.sset_trace()
        super().__init__(*args, **kwargs)
        #Clock.schedule_once(self.build_screens)
        #Window.bind(on_keyboard=self.hook_keyboard2)
            #self.init()
            
        #def init(self):
        self.add_widget(uix.screens.home.home)
        self.add_widget(uix.screens.handbook.HandBookScreen(name='handbook'))
        #uix.screens.position.position = PositionScreen(name='position')
        self.add_widget(uix.screens.position.position)
        self.add_widget(uix.screens.organizations.organizations)
        self.add_widget(uix.screens.events.events)
        self.add_widget(uix.screens.complaint.complaint)
        self.add_widget(uix.screens.about.AboutScreen(name='about'))
        self.add_widget(uix.screens.communication.CommunicationScreen(name='communication'))
        self.add_widget(uix.screens.userprofile.userprofile)
        self.push_screen('home')
        #self.push_screen('position')
        #schedule('core.screens_initialized')


    def push_screen(self, name):
        if self.current == 'error':
            return
        logger.info(f'push screen "{name}". {self.screen_history=} {self.current=}')
        #import ipdb; ipdb.sset_trace()
        self.transition.direction = 'left'
        #if self.current == 'userprofile' and name != 'userprofile':
            #schedule('core.leave_userprofile_screen')
        if self.current == 'position' and name != 'position':
            if self.get_screen('position').show_errors():
                return
            #schedule('core.leave_position_screen')

            self.screen_history = []
        if name == 'home':
            self.current = 'home'
        elif self.current != name:
            if self.current == 'home':
                self.screen_history = [name]
            else:
                self.screen_history.append(name)
            self.current = name

    def pop_screen(self):
        self.transition.direction = 'right'
        logger.info(f'pop screen. Screen_history: {self.screen_history}')
        if len(self.screen_history) > 1:
            self.screen_history.pop()
            self.current = self.screen_history[-1]
        elif len(self.screen_history) == 1:
            self.screen_history.pop()
            self.current = 'home'

    def on_current(self, *args):
        self.about_to_exit = False
        super().on_current(*args)

    #def hook_keyboard2(self, *args):
        #print args
        #return True

    def hook_keyboard(self, window, key, scancode, codepoint, modifier):
        #logging.info( "XXXXXXXXXXXXXXXXX scancode %d pressed" % scancode)
        #if platform != 'android':
            #if key == ord('p'):
                #self.profile = cProfile.Profile()
                #self.profile.enable()
            #elif key == ord('o'):
                #self.profile.disable()
                #self.profile.dump_stats('myapp.profile')
        # if codepoint is None:
        # logger.info(f'{key=}, {scancode=}, {codepoint=}')

        if key in (1000, 27, 1073742095, 4):
            # TODO: on android 15 emulator back button does not work, but adb
            # command does:
            # adb shell input keyevent KEYCODE_BACK

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
            screen = uix.screens.error.ErrorScreen(message=message, name='error')
            self.add_widget(screen)
        self.current = 'error'

    def show_quiztopic(self, topic):
        name = f'topic_{topic["id"]}'
        if not self.has_screen(name):
            self.add_widget(uix.screens.quiztopic.QuizTopicScreen(topic, name=name))

        self.push_screen(name)

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
    def remove_quiztopic_sreens(self):
        self.screen_history = []
        if self.current.startswith('topic_'):
            self.push_screen('home')
        #logger.debug(f'{self.screens}')
        for screen in self.screens:
            if screen.name.startswith('topic_'):
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
