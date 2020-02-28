# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from app_state import state, on
from django.core.validators import ValidationError, validate_email
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
from loguru import logger

from ..vbox import VBox
from paradox import uix
from paradox.uix import float_message


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
                on_focus_out: state.profile.email = self.text

            NiceTextInput:
                id: last_name
                hint_text: 'Фамилия'
                on_focus_out: state.profile.last_name = self.text
                #text: root.last_name

            NiceTextInput:
                id: first_name
                hint_text: 'Имя'
                on_focus_out: state.profile.first_name = self.text
                #text: root.name

            NiceTextInput:
                id: middle_name
                hint_text: 'Отчество'
                on_focus_out: state.profile.middle_name = self.text
                #text: root.middle_name

            NiceTextInput:
                id: telegram
                hint_text: 'telegram'
                on_focus_out: state.profile.telegram = self.text
                
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
                    on_focus_out: state.profile.phone = self.text
                    #text: root.phone

            Button:
                id: next
                text: 'Продолжить'
                on_release: root.manager.push_screen('formlist')
                background_color: darkgray

''')


class UserProfileScreen(Screen):
    inputs = 'email last_name first_name middle_name phone telegram'.split()
    #email = Ob last_name first_name middle_name phone

    def __init__(self, *args, **kwargs):
        super(UserProfileScreen, self).__init__(*args, **kwargs)
        #initial_data = state.get('profile', {})
        #for input in self.inputs:
            #self.ids[input].text = initial_data.get(input, '')
            #self.ids[input].bind(focus=self.input_focus)

    #def get_data(self):
        #return {x: self.ids[x].text for x in self.inputs}

    @on('state.profile')
    def update_inputs(self):
        for input in self.inputs:
            self.ids[input].text = state.get('profile', {}).get(input, '')
        

    @staticmethod
    def userprofile_errors():
        errors = []
        missing = []
        data = state.get('profile', {})
        if not data.get('phone'):
            missing.append('Телефон')
        if not data.get('first_name'):
            missing.append('Имя')
        if not data.get('last_name'):
            missing.append('Фамилия')
        if not data.get('email'):
            missing.append('Email')
        else:
            try:
                validate_email(data.get('email'))
            except ValidationError as e:
                errors.append('Некорректный email')
    
        if missing:
            errors.append('Пожалуйста заполните обязательные поля\n' + '\n'.join(missing))
        if errors:
            uix.float_message.show(text='\n'.join(errors))
            return errors
        else:
            return False
        
    def on_leave(self):
        data = {x: self.ids[x].text for x in self.inputs}
        stored = state.get('profile', {})
        #logger.debug(f'{stored}\n {data}')
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
