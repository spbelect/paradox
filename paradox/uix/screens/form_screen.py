# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget

from ...scheduler import schedule
from ...objects_manager import objects_manager
from ..multibool_input import MultiBoolInput
from ..numeric_input import NumericInput
from ..vbox import VBox


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


@objects_manager
class FormScreen(Screen):
    json = ObjectProperty()

    def __init__(self, form, *args, **kwargs):
        super(FormScreen, self).__init__(*args, **kwargs)
        self.json = form
        schedule(self.load_inputs, timeout=0.41)
        #Window.bind(keyboard_height=self.on_keyboard_height)

    #def on_keyboard_height(self, *args):
        #pass

    def load_inputs(self):
        for n, input_data in enumerate(self.json['inputs']):
            #if not input_data.get('help_text'):
                #input_data['help_text'] = txt

            schedule(self.add_input, input_data, timeout=0.0 + 0.04 * n)

        if self.json['form_type'] == 'GENERAL':
            self.remove_widget(self.ids['trailing_spacer'])

        schedule('core.restore_inputs', timeout=0.1 + 0.04 * n)

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