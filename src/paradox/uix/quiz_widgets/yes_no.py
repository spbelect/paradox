# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from asyncio import sleep

from getinstance import InstanceManager
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors.togglebutton import ToggleButtonBehavior
from kivy.uix.togglebutton import ToggleButton
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty, Property

from loguru import logger
from ..vbox import VBox
from . import base
from label import Label
from button import Button
from paradox import utils

Builder.load_string('''
#:include constants.kv

#:import state app_state.state

#:import uix paradox.uix



<YesNoCancel>:
    disabled: not self.screen.load_finished or not self.visible
    size_hint_y: None
    #width: 0.9 * getattr(self.parent, 'width', 10)
    padding_y: 0
    spacing: 0
    #canvas.before:
        #Color:
            #rgba: teal
        #Rectangle:
            #pos: self.pos
            #size: self.size
    Button:
        id: question_label
        padding_x: dp(6)
        split_str: ' '
        text_size: self.width, None
        height: self.texture_size[1] + dp(10)
        text: self.parent.question.label
        color: black
        #color: wheat4
        on_long_press: root.show_help()
        #on_release: print(66)

    Label:
        #id: send_status
        color: lightgray
        font_size: dp(14)
        size_hint_y: None
        height: dp(14)
        halign: 'left' if getattr(root.answer, 'value', False) else 'right'
        #text: '124'
        text: root.status_text or ' '
        #background_color: teal
        
    BoxLayout:
        size_hint: None, None
        id: buttons
        padding: 0, 0, 0, dp(10)
        spacing: dp(100)
        size: dp(300), height1
        pos_hint: {'center_x': .5, 'top': 1}
        background_color: lightgray

        YesNoButton:
            id: yes
            size_hint_x: .2
            text: 'Да'
            value: True

        YesNoButton:
            id: no
            size_hint_x: .2
            text: 'Нет'
            value: False
            
        
    VBox:
        #visible: root.complaint_visible
        
        Button:
            id: complaint
            height: dp(30)
            font_size: dp(24)
            color: teal
            disabled: not root.complaint_visible
            opacity: 1 if root.complaint_visible else 0
            text: "обжаловать"
            on_press: uix.screenmgr.show_complaint(root.answer)

        
<YesNoButton@ToggleButton>:
    height: self.parent.height - 10
    size_hint_y: 1
    allow_no_selection: False
    group: self.parent.uid
    #on_press: self.parent.parent.on_click(self.value)
    on_press: self.parent.parent.add_new_answer(self.value)
    background_color: lightgray
    #disabled: True


''')

#class TNFButton(ToggleButton):
    ## workaround for kivy BUG: https://github.com/kivy/kivy/issues/4379
    #value = ObjectProperty(allownone=True)


class YesNoCancel(base.QuizWidget, VBox):
    #text = StringProperty('')
    #question_id = StringProperty()

    #def on_send_start(self, answer):
        #self.ids.send_status.text = 'отправляется'
    
    #def on_send_success(self, answer):
        #super().on_send_success(answer)
        #self.ids.send_status.text = ''

    #def on_send_error(self, answer):
        #self.ids.send_status.text = 'отправляется (error)'

    ##def on_send_fatal_error(self, answer, request, error_data):
        ##self.ids.send_status.text = 'ошибка'
    
    #def on_save_success(self, answer):
        #super().on_save_success(answer)
        #self.ids.send_status.text = 'отправляется'
        ##self.show_state(None if answer.revoked else answer.value)
        
    #def on_save_start(self, answer):
        #super().on_save_start(answer)
        #self.ids.send_status.text = 'сохраняется'
        ##self.show_state(None if answer.revoked else answer.value)
        
    @property
    def val(self):
        if not self.answer:
            return None
        return None if self.answer.revoked else self.answer.value
        
    @utils.asynced
    async def add_new_answer(self, value):
        if self.val == value:
            value = None
        #self.disabled = True
        #import ipdb; ipdb.sset_trace()
        #if not value == self.val:
        success = await super().add_new_answer(value)
        if not success:
            self.show_cur_state()
        #await sleep(0.2)
        #self.disabled = False
        
    #async def set_past_answers(self, answers):
        ##logger.debug(f'{self}, {self.question.label}, {answers}')
        #if answers:
            ##print('set past', answers[-1].value)
            #answer = answers[-1]
            #self.show_state(None if answer.revoked else answer.value)
        #else:
            #self.show_state(None)
            
        #await super().set_past_answers(answers)
            
    #def on_answer(self, *a):
        #return super().on_answer(*a)
    
    def show_cur_state(self):
        #logger.debug(f'{self}, {self.question.label}, {self.val}')
        self.ids.yes.state = 'down' if self.val is True else 'normal'
        self.ids.no.state = 'down' if self.val is False else 'normal'
                
