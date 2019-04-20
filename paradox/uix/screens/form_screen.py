# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import datetime, timedelta

from app_state import state
from django.db.models import Q
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget

from ..multibool_input import MultiBoolInput
from ..numeric_input import NumericInput
from ..vbox import VBox
from paradox.models import InputEvent


Builder.load_string('''
#:include constants.kv

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
        #schedule(self.load_inputs, timeout=0.41)
        #Window.bind(keyboard_height=self.on_keyboard_height)

        #def load_inputs(self):
        #print self.json['inputs']
        for n, input_data in enumerate(self.json['inputs']):
            #if not input_data.get('help_text'):
                #input_data['help_text'] = txt

            self.add_input(input_data)

        if self.json['form_type'] == 'GENERAL':
            self.remove_widget(self.ids['trailing_spacer'])

        filter = Q(uik=state.uik, region=state.region.id, timestamp__gt=datetime.now()-timedelta(days=1))
        for event in InputEvent.objects.filter(filter):
            Input.instances.filter(input_id=event.input_id).add_past_event(event)

    def add_input(self, input_data):
        if input_data['input_type'] == 'NUMBER':
            input = NumericInput(json=input_data, form=self.json)
        elif input_data['input_type'] == 'MULTI_BOOL':
            input = MultiBoolInput(json=input_data, form=self.json)
        else:
            return
        input.ids['input_label'].bind(on_long_press=self.on_input_label_press)
        self.ids['content'].add_widget(input)

    def on_input_label_press(self, input_label):
        self.manager.show_handbook(input_data=input_label.parent.json)
