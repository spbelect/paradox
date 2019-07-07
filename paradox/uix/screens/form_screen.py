# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import asyncio

from asyncio import sleep
from datetime import datetime, timedelta
from itertools import groupby

from app_state import state, on
from django.db.models import Q
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivy.effects.dampedscroll import DampedScrollEffect
from loguru import logger

#from .. import base_input 
from ..multibool_input import MultiBoolInput
from ..true_none_false import TrueNoneFalse
from ..numeric_input import NumericInput
from ..vbox import VBox
from paradox.models import InputEvent, Campaign
from paradox import uix


Builder.load_string('''
#:include constants.kv
#:import DampedScrollEffect kivy.effects.dampedscroll.DampedScrollEffect 

<FormScreen>:
    ScrollView:
        VBox:
            VBox:
                spacing: dp(4)

                Label:
                    padding_x: dp(4)
                    split_str: ' '
                    text_size: self.width, None
                    height: self.texture_size[1] + 10
                    text: root.json['name'] if root.json else ''
                    color: white
                    background_color: teal

                Label:
                    text: 'Долгое нажатие на текст выводит юридическую справку'
                    text_size: self.width, None
                    split_str: ' '
                    color: lightgray
                    font_size: sp(16)
                    height: self.texture_size[1]

                VBox:
                    id: content
                    spacing: dp(40)

            BoxLayout:
                height: height1
                spacing: dp(2)

                Button:
                    text: '< Назад'
                    on_press: root.manager.pop_screen()
                    halign: 'left'
                    text_size: self.size
                    size_hint: None, None
                    width: dp(150)
                    background_color: white
                    color: teal


                Widget:  # horizontal spacer

            Widget:  # vertical spacer
                id: trailing_spacer
                height: height1 * 8
                size_hint_y: None

''')


class FormScreen(Screen):
    json = ObjectProperty()

    #def on_keyboard_height(self, *args):
        #pass

    def __init__(self, form, *args, **kwargs):
        super(FormScreen, self).__init__(*args, **kwargs)
        self.json = form
        #raise Exception()
        
        #for item in self.ids['content'].children[:]:
            #self.ids['content'].remove_widget(item)
        
        asyncio.create_task(self.build())
        #Clock.schedule_once(lambda *a: self.build(), 0.5)
    
    async def build(self):
        await sleep(0.5)
        logger.debug(f'building form {self.json["name"]}')
        for input in self.json['inputs']:
            #if not input_data.get('help_text'):
                #input_data['help_text'] = txt
            
            self.add_input(input)
            await sleep(0.1)

        if self.json['form_type'] == 'GENERAL':
            self.remove_widget(self.ids['trailing_spacer'])
        
        logger.debug(f'building form {self.json["name"]} inputs added')
        uix.base_input.restore_past_events()
        logger.debug(f'building form {self.json["name"]} finished')

        
    def add_input(self, input_data):
        if input_data['input_type'] == 'NUMBER':
            input = NumericInput(json=input_data, form=self.json)
        elif input_data['input_type'] == 'MULTI_BOOL':
            input = TrueNoneFalse(json=input_data, form=self.json)
        else:
            return
        #input.ids['input_label'].bind(on_long_press=self.on_input_label_press)
        self.ids['content'].add_widget(input)

    def on_input_label_press(self, input_label):
        self.manager.show_handbook(input_data=input_label.parent.json)
