# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from app_state import state
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

from ..vbox import VBox



Builder.load_string('''
#:include constants.kv
#:import state app_state.state

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
                on_focus: state.profile.email = self.text

            NiceTextInput:
                id: last_name
                hint_text: 'Фамилия'
                on_focus: state.profile.last_name = self.text

            NiceTextInput:
                id: first_name
                hint_text: 'Имя'
                on_focus: state.profile.first_name = self.text

            NiceTextInput:
                id: middle_name
                hint_text: 'Отчество'
                on_focus: state.profile.middle_name = self.text

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
                    on_focus: state.profile.phone = self.text

            Button:
                text: 'Продолжить'
                on_release: root.manager.push_screen('formlist')
                background_color: darkgray

''')


class UserProfileScreen(Screen):
    inputs = 'email last_name first_name middle_name phone'.split()

    def __init__(self, *args, **kwargs):
        super(UserProfileScreen, self).__init__(*args, **kwargs)
        initial_data = state.get('profile', {})
        for input in self.inputs:
            self.ids[input].text = initial_data.get(input, '')
            #self.ids[input].bind(focus=self.input_focus)

    def get_data(self):
        return {x: self.ids[x].text for x in self.inputs}


    @staticmethod
    def userprofile_errors():
        errors = []
        data = state.get('profile', {})
        if not data.get('phone'):
            errors.append('Телефон')
        if not data.get('first_name'):
            errors.append('Имя')
        if not data.get('last_name'):
            errors.append('Фамилия')
        if errors:
            errors = 'Пожалуйста заполните обязательные поля\n' + '\n'.join(errors)
            show_float_message(text=errors)
            return errors
        else:
            return False
        
    def on_leave(self):
        data = {x: self.ids[x].text for x in self.inputs}
        stored = state.get('profile', {})
        if stored == data:
            return
        state.profile = data

        #timestamp = datetime.utcnow().isoformat()
        #net.queue_send_userprofile(dict(data, timestamp=timestamp))

    #def input_focus(self, input, focus):
        #if not focus:
            #data = {x: self.ids[x].text for x in self.inputs}
            #schedule('core.userprofile_changed', data)

    #def on_continue(self):
        #data = {x: self.ids[x].text for x in self.inputs}
        #schedule('core.userprofile_next', data)
