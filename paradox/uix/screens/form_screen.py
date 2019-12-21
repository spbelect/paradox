# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import asyncio

from asyncio import sleep
from datetime import datetime, timedelta
from itertools import groupby

from app_state import state, on
from django.db.models import Q
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.properties import BooleanProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.effects.dampedscroll import DampedScrollEffect
from loguru import logger

from ..multibool_input import MultiBoolInput
from ..true_none_false import TrueNoneFalse
from ..numeric_input import NumericInput
from ..vbox import VBox
from paradox.models import Answer, Campaign
from paradox.uix import top_loader
from paradox import uix


Builder.load_string('''
#:include constants.kv
#:import DampedScrollEffect kivy.effects.dampedscroll.DampedScrollEffect 

<FormScreen>:
    ScrollView:
        id: scrollview
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
    load_finished = BooleanProperty(False)

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
    
    @uix.top_loader.show
    async def build(self):
        await sleep(0.05)
        logger.debug(f'building form {self.json["name"]}')
        for question in self.json['inputs']:
            #if not question.get('help_text'):
                #question['help_text'] = txt
            
            self.add_widget(question)
            await sleep(0.01)

        self.remove_widget(self.ids['trailing_spacer'])
        
        logger.debug(f'building form {self.json["name"]} inputs added')
        await uix.quiz_widgets.base.restore_past_answers()
        logger.debug(f'building form {self.json["name"]} finished')
        await sleep(0.7)
        self.load_finished = True
        
    def add_widget(self, question):
        if question['input_type'] == 'NUMBER':
            quizwidget = NumericInput(json=question, form=self)
        elif question['input_type'] == 'MULTI_BOOL':
            quizwidget = TrueNoneFalse(json=question, form=self)
        else:
            return
        #question.ids['question_label'].bind(on_long_press=self.on_question_label_press)
        self.ids.content.add_widget(quizwidget)

    def on_question_label_press(self, question_label):
        self.manager.show_handbook(question=question_label.parent.json)

    #def __del__(self):
        #logger.debug(f'del {self.json["name"]}')
        
