# -*- coding: utf-8 -*-
# TODO: move this into standalone package

import kivy.uix.textinput
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.lang import Builder
#from kivy.properties import BooleanProperty, ListProperty



class TextInput(kivy.uix.textinput.TextInput):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.register_event_type('on_focus_in')
        self.register_event_type('on_focus_out')
        
    def on_focus_in(self, *args):
        pass
    
    def on_focus_out(self, *args):
        pass

    def on_focus(self, selff, f):
        if f is True:
            self.dispatch('on_focus_in')
        else:
            self.dispatch('on_focus_out')

Factory.unregister('TextInput')
Factory.register('TextInput', cls=TextInput)
