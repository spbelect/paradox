# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime
from time import sleep
import re
import traceback

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors.togglebutton import ToggleButtonBehavior
from kivy.uix.behaviors.focus import FocusBehavior
from kivy.uix.button import Button
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty, Property

from ..vbox import VBox
from paradox.label import Label
from paradox.textinput import TextInput
from . import base
from paradox import utils


Builder.load_string('''
#:include constants.kv
#:import state app_state.state

<NumericInput>:
    size_hint_y: None
    
    disabled: not self.screen.load_finished or not self.visible
    padding: 0
    spacing: 0
    #width: 0.9 * getattr(self.parent, 'width', 10)

    Button:
        id: question_label
        #size_hint: None, None
        #width: 0.9 * self.parent.width
        height: self.texture_size[1] + 10
        text: self.parent.question.label
        color: black
        split_str: ' '
        text_size: self.width, None
        on_long_press: root.show_help()

    SerialTextInput:
        id: value_input
        input_type: 'number'
        #input_filter: 'int'
        background_active: self.background_normal
        hint_text: 'Введите число'
        padding: dp(4), dp(4)
        multiline: False
        size_hint: None, None
        width: dp(250)
        height: dp(40)
        pos_hint: {'center_x': .5}
        #on_focus: if not args[1]: root.value = self.text

    Label:
        size_hint_y: None
        color: lightgray
        #pos_hint: {'center_x': .5}
        height: dp(14)
        #width: dp(300)
        #font_size: sp(16)
        text: root.status_text

    VBox:
        id: complaint
        visible: root.complaint_visible
        
        Button:
            height: dp(49)
            color: teal
            text: "Обжаловать"
            on_press: uix.screenmgr.show_complaint(root.answer)
            
            

''')


#class Loader(Label):
    #timestamp = ObjectProperty()


#FOCUS_IN = True
#FOCUS_OUT = False


class SerialTextInput(TextInput):
    
    def insert_text(self, substring, from_undo=False):
        return super().insert_text(substring[:6], from_undo)
    
    def input_filter(self, substring, from_undo=False):
        return re.sub('[^0-9]', '', substring)[:6 - len(self.text)]
        #return super().insert_text(substring[:6], from_undo)
    
        
    #def keyboard_on_key_down(self, window, keycode, text, modifiers):
        ##print 111, keycode
        #next_input = self._get_focus_next('focus_next')

        ##import ipdb; ipdb.set_trace()
        ##print next_input
        #if keycode[1] == 'enter':
            #if next_input:
                ##print next_input.parent.ids['question_label'].text
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

    @utils.asynced
    async def on_focus_out(self, *a):
        if self.text is not None:
            await self.parent.add_new_answer(self.text)



class NumericInput(base.QuizWidget, VBox):
    #value = ObjectProperty(None, allownone=True)
    #loader = ObjectProperty(None, allownone=True)

    def show_cur_state(self):
        if self.answer:
            self.ids.value_input.text = str(self.answer.value or '')
        else:
            self.ids.value_input.text = ''
        
    #def on_answer(self, *a):
        #return super().on_answer(*a)
        
    async def add_new_answer(self, text):
        if self.answer and str(self.answer.value) == text:
            return
        success = await super().add_new_answer(text)
        if not success:
            self.show_cur_state()
        
    #async def set_past_answers(self, answers):
        #if answers:
            #self.show_state(answers[-1].value)
        #await super().set_past_answers(answers)

    #def reset(self):
        #self.ids.value_input.text = ''
        
    #def on_value(self, *args):
        #schedule('core.new_input_event', self, self.value)

    #def on_save_success(self, answer):
        #super().on_save_success(answer)
        ##self.ids['loader'].timestamp = timestamp.isoformat()
        #self.ids.loader.text = 'отправляется'

    #def on_send_success(self, answer):
        ##if self.ids['loader'].timestamp == answer['timestamp']:
        #self.ids.loader.text = ''

    #def on_send_error(self, answer):
        ##if self.ids['loader'].timestamp == answer['timestamp']:
        #self.ids.loader.text = 'отправляется (err)'

    #def on_send_fatal_error(self, answer, request, error_data):
        #if self.ids['loader'].timestamp == answer['timestamp']:
            #self.ids['loader'].text = 'отправляется (err)'
