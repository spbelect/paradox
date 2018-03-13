# -*- coding: utf-8 -*-

from __future__ import unicode_literals
#from os.path import exists
import logging
import json
import traceback
import shelve

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
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.modalview import ModalView
from kivy.uix.vkeyboard import VKeyboard
from kivy.uix.behaviors.button import ButtonBehavior
#import plyer

from ...scheduler import schedule
from ..vbox import VBox
###from uix.navigationdrawer2 import NavigationDrawer
from ..float_message import show_float_message

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

<Screens>:
    canvas.before:
        Color:
            rgba: (4, 4, 9, 1)
        Rectangle:
            pos: self.pos
            size: self.size

''')


class Screens(ScreenManager):
    screen_history = ListProperty([])
    about_to_exit = BooleanProperty(False)

    def __init__(self, *args, **kwargs):
        super(Screens, self).__init__(*args, **kwargs)
        Clock.schedule_once(self.build_screens)
        EventLoop.window.bind(on_keyboard=self.hook_keyboard)
        #Window.bind(on_keyboard=self.hook_keyboard2)


    def push_screen(self, name):
        self.transition.direction = 'left'
        if self.current == 'userprofile' and name != 'userprofile':
            schedule('core.leave_userprofile_screen')
        if self.current == 'position' and name != 'position':
            if self.get_screen('position').show_errors():
                return
            schedule('core.leave_position_screen')

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
        super(Screens, self).on_current(*args)

    #def hook_keyboard2(self, *args):
        #print args
        #return True

    def hook_keyboard(self, window, key, *args):
        logging.info( "XXXXXXXXXXXXXXXXX key %d pressed" % key)
        if key in (1000, 27, 1073742095, 4):
            if App.root.state == 'open':
                App.root.toggle_state()
            elif len(self.screen_history) >= 1:
                self.pop_screen()
            elif self.about_to_exit:
                return False
            else:
                self.about_to_exit = True
                show_float_message(text='Нажмите еще раз для выхода')
        return True

    def build_screens(self, *a):
        self.add_widget(FormListScreen(name='formlist'))
        self.add_widget(HandBookScreen(name='handbook'))
        self.add_widget(PositionScreen(name='position'))
        self.add_widget(EventsScreen(name='events'))
        self.add_widget(AboutScreen(name='about'))
        self.add_widget(CommunicationScreen(name='communication'))
        self.add_widget(UserProfileScreen(name='userprofile'))
        self.push_screen('formlist')
        #self.push_screen('position')
        schedule('core.screens_initialized')

    def show_error_screen(self, message):
        if self.has_screen('error'):
            screen = self.get_screen('error')
            screen.message = message.encode('utf-8')
        else:
            screen = ErrorScreen(message=message.encode('utf8'), name='error')
            self.add_widget(screen)
        self.current = 'error'

    def show_form(self, form):
        screen_name = 'form_%(form_id)s' % form
        if not self.has_screen(screen_name):
            self.add_widget(FormScreen(form, name=screen_name))

        self.push_screen(screen_name)

    def show_handbook(self, input_data):
        self.get_screen('handbook').show_input_help(input_data)
        self.push_screen('handbook')

    def on_pause(self):
        pass
        #self.get_screen('formlist').ids['camera'].play = False

    def on_resume(self):
        pass
        #self.get_screen('formlist').ids['camera'].play = True
