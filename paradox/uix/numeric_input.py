# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime
from time import sleep
import traceback

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors.togglebutton import ToggleButtonBehavior
from kivy.uix.behaviors.focus import FocusBehavior
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty, Property

from .vbox import VBox
from label import Label
from .base_input import Input


Builder.load_string('''
#:include constants.kv
#:import state app_state.state

<NumericInput>:
    size_hint_y: None
    
    padding: 0
    spacing: 0
    width: 0.9 * getattr(self.parent, 'width', 10)

    Button:
        id: input_label
        #size_hint: None, None
        #width: 0.9 * self.parent.width
        height: self.texture_size[1] + 10
        text: self.parent.json['label']
        color: black
        split_str: ' '
        text_size: self.width, None

    SerialTextInput:
        id: value_input
        input_type: 'number'
        input_filter: 'int'
        background_active: self.background_normal
        hint_text: 'Введите число'
        padding: dp(4), dp(4)
        multiline: False
        size_hint: None, None
        width: dp(250)
        height: dp(40)
        pos_hint: {'center_x': .5}
        #on_focus: if not args[1]: root.value = self.text

    Loader:
        id: loader
        size_hint: None, None
        color: lightgray
        pos_hint: {'center_x': .5}
        #halign: 'left'
        height: dp(20)
        width: dp(300)
        font_size: sp(16)


''')


class Loader(Label):
    timestamp = ObjectProperty()


FOCUS_IN = True
FOCUS_OUT = False


class SerialTextInput(TextInput):
    #def keyboard_on_key_down(self, window, keycode, text, modifiers):
        ##print 111, keycode
        #next_input = self._get_focus_next('focus_next')

        ##import ipdb; ipdb.set_trace()
        ##print next_input
        #if keycode[1] == 'enter':
            #if next_input:
                ##print next_input.parent.ids['input_label'].text
                #self._keyboard.release()
                #self.focus = False
                ##if self._keyboard:
                ##del FocusBehavior._keyboards[self._keyboard]
                #self._requested_keyboard = False
                ##self._keyboard = None
                ##self._unbind_keyboard()
                #schedule(lambda *a: setattr(next_input, 'focus', True), 3)

            #return True
        #return super(SerialTextInput, self).keyboard_on_key_down(window, keycode, text, modifiers)

    def on_focus(self, s, f):
        if f == FOCUS_OUT:
            self.parent.on_input(self.text or '')



class NumericInput(Input, VBox):
    value = ObjectProperty(None, allownone=True)
    #loader = ObjectProperty(None, allownone=True)

    def add_past_events(self, events):
        if events:
            self.ids['value_input'].text = events[-1].value
        super().add_past_events(events)

    def reset(self):
        self.ids['value_input'].text = ''
        
    #def on_value(self, *args):
        #schedule('core.new_input_event', self, self.value)

    def on_save_success(self, eid, timestamp, value):
        self.ids['loader'].timestamp = timestamp.isoformat()
        self.ids['loader'].text = 'отправляется'

    def on_send_success(self, event):
        if self.ids['loader'].timestamp == event['timestamp']:
            self.ids['loader'].text = ''

    def on_send_error(self, event, request, error_data):
        if self.ids['loader'].timestamp == event['timestamp']:
            self.ids['loader'].text = 'отправляется (err)'

    def on_send_fatal_error(self, event, request, error_data):
        if self.ids['loader'].timestamp == event['timestamp']:
            self.ids['loader'].text = 'отправляется (err)'
