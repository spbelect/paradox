# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.vkeyboard import VKeyboard

from ...scheduler import schedule
from ..vbox import VBox



Builder.load_string('''
#:include constants.kv
#:import schedule paradox.scheduler.schedule

<NiceTextInput@TextInput>:
    background_active: ''
    background_normal: ''
    multiline: False
    size_hint: 1, None

<UserProfileScreen>:
    ScrollView:
        VBox:
            NiceTextInput:
                id: email
                hint_text: 'Email'

            NiceTextInput:
                id: last_name
                hint_text: 'Фамилия'

            NiceTextInput:
                id: first_name
                hint_text: 'Имя'

            NiceTextInput:
                id: middle_name
                hint_text: 'Отчество'

            BoxLayout:
                height: height1

                Label:
                    size_hint: None, None
                    text_size: self.size
                    text: '+7'
                    size: dp(40), height1

                NiceTextInput:
                    id: phone
                    hint_text: 'Телефон'
                    input_filter: 'int'
                    input_type: 'number'

            Button:
                text: 'Продолжить'
                on_release: schedule(lambda: root.manager.push_screen('position'))
                #on_release: root.on_continue()
                background_color: darkgray

''')


class UserProfileScreen(Screen):
    inputs = 'email last_name first_name middle_name phone'.split()

    def __init__(self, *args, **kwargs):
        super(UserProfileScreen, self).__init__(*args, **kwargs)
        initial_data = App.app_store.get('profile', {})
        for input in self.inputs:
            self.ids[input].text = initial_data.get(input, '')
            #self.ids[input].bind(focus=self.input_focus)

    def get_data(self):
        return {x: self.ids[x].text for x in self.inputs}

    #def input_focus(self, input, focus):
        #if not focus:
            #data = {x: self.ids[x].text for x in self.inputs}
            #schedule('core.userprofile_changed', data)

    #def on_continue(self):
        #data = {x: self.ids[x].text for x in self.inputs}
        #schedule('core.userprofile_next', data)
