# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from itertools import chain

from app_state import state, on
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
from ..choices import Choice
from ..float_message import show_float_message

from paradox import uix
from paradox.models import Campaign


Builder.load_string('''
#:include constants.kv
##:import show_float_message paradox.uix.float_message.show_float_message
#:import state app_state.state


<NiceTextInput@TextInput>:
    background_active: ''
    background_normal: ''
    multiline: False
    size_hint: 1, None
    

<PositionScreen>:
    ScrollView:
        VBox:

            Choices:
                id: region_choices
                modal_header: 'Ваш регион:'
                text: 'выберите регион'
                text_size: self.width, None
                shorten: True
                halign: 'left'
                on_text: self.color = black
                height: height1
                size_hint_y: None
                on_input:
                    state.region = state.regions[self.value]

            BoxLayout:
                height: height1
                size_hint_y: None

                Label:
                    size_hint: None, None
                    text_size: self.size
                    text: 'УИК:'
                    size: dp(70), height1
                    halign: 'left'

                NiceTextInput:
                    id: uik
                    input_filter: 'int'
                    input_type: 'number'
                    #max_len: 4
                    hint_text: 'введите номер'
                    text: root.uik or ''
                    on_focus: state.uik = int(self.text) if self.text.isnumeric() else None

            VBox:
                spacing: 0
                height: 2*height1
                size_hint_y: None

                Label:
                    text: 'Ваш статус:'
                    halign: 'left'
                    text_size: self.width, None
                    padding: 0, 0

                Choices:
                    id: status_choices
                    height: self.texture_size[1]
                    modal_header: 'Ваш статус:'
                    text: 'выберите статус'
                    text_size: self.width, None
                    halign: 'left'
                    on_text: self.color = black
                    padding: 0, 0
                    on_value: state.role = self.value

                    StatusChoice:
                        text: 'Член комиссии с правом решающего голоса (ПРГ)'
                        short_text: 'ПРГ'
                        value: 'prg'

                    StatusChoice:
                        text: 'Член комиссии с правом совещательного голоса (ПСГ)'
                        short_text: 'ПСГ'
                        value: 'psg'

                    StatusChoice:
                        text: 'Наблюдатель'
                        short_text: 'Наблюдатель'
                        value: 'nabludatel'

                    StatusChoice:
                        text: 'Представитель СМИ (Журналист)'
                        short_text: 'Журналист'
                        value: 'smi'

                    StatusChoice:
                        text: 'Кандидат'
                        short_text: 'Кандидат'
                        value: 'kandidat'

                    StatusChoice:
                        text: 'Избиратель (это ваш участок для голосования)'
                        short_text: 'Избиратель'
                        value: 'izbiratel'

                    StatusChoice:
                        text: 'Мимо проходил (это не ваш участок для голосования)'
                        short_text: 'Мимо проходил'
                        value: 'other'

            Label:
                #id: mokrug
                #text: state.get('mokrug', {}).get('name', '') if state.get('mokrug') else ''
                text: root.mokrug['name'] if root.mokrug else ''
                #text: "lol"
                
            Widget:  #spacer
                height: dp(15)

            Button:
                text: 'Продолжить'
                on_release: root.manager.push_screen('userprofile')
                background_color: darkgray

''')


from getinstance import InstanceManager

class RegionChoice(Choice):
    instances = InstanceManager()


class StatusChoice(Choice):
    instances = InstanceManager()


class PositionScreen(Screen):
    mokrug = ObjectProperty(None, allownone=True)
    uik = ObjectProperty(None, allownone=True)

    #def __init__(self, *args, **kwargs):
        #super().__init__(*args, **kwargs)
        
    @on('state.regions')
    def build_regions(self):
        logger.debug('rebuilding region choices')
        regions = state.regions.values()
        
        for choice in self.ids['region_choices'].choices():
            self.ids['region_choices'].remove_choice(choice.value)

        msk = list(filter(lambda x: 'Москва' in x['name'], regions))
        spb = list(filter(lambda x: 'Санкт' in x['name'], regions))
        lo = list(filter(lambda x: 'Ленинградская' in x['name'], regions))

        #choice = RegionChoice(short_text='Москва', text='Москва', value=msk['id'])
        #self.ids['region_choices'].add_widget(choice)
        
        choice = RegionChoice(
            short_text='Санкт-Петербург', text='Санкт-Петербург', value='ru_78')
        self.ids['region_choices'].add_widget(choice)

        choice = RegionChoice(
            short_text='Ленинградская область', text='Ленинградская область', value='ru_47')
        self.ids['region_choices'].add_widget(choice)

        for region in sorted(regions, key=lambda x: x['name']):
            if region in spb + lo or not region['id'].startswith(state.country):
                continue
            name = region['name']
            choice = RegionChoice(short_text=name, text=name, value=region['id'])
            self.ids['region_choices'].add_widget(choice)
            
        if state.get('region'):
            region_choice = RegionChoice.instances.get(value=state.region.id)
            if region_choice:
                self.ids['region_choices'].choice = region_choice
                
    @on('state.role')
    def set_role(self):
        if state.get('role'):
            self.ids['status_choices'].choice = StatusChoice.instances.get(value=state.role)
            
    @on('state.uik')
    def set_uik(self):
        self.uik = str(state.get('uik', '') or '')
  
    def get_mokrug(self):
        if not (state.get('uik') and state.get('region')):
            return None
        for mokrug in state.region.get('mokruga', []):
            if int(state.uik) in mokrug.get('uiks', []):
                return mokrug
            for first, last in mokrug.get('ranges', []):
                if first <= int(state.uik) <= last:
                    return mokrug
        return None
        
    @on('state.uik', 'state.region')
    def update_mokrug(self):
        self.mokrug = state.mokrug = self.get_mokrug()
        logger.debug(f'Mokrug: {self.mokrug}')
        
                   
    def show_errors(self):
        errors = []
        if not self.ids['region_choices'].choice:
            errors.append('Выберите регион')
        if not self.ids['uik'].text:
            errors.append('Введите номер УИК')
        if not self.ids['status_choices'].choice:
            errors.append('Укажите ваш статус')
        if errors:
            errors = 'Пожалуйста заполните обязательные поля\n\n' + '\n'.join(errors)
            show_float_message(text=errors)
            return errors
        else:
            return False

    #def on_enter(self):
        #self.prev_regionid = state.get('region', {}).get('id')
        #self.prev_uik = state.get('uik')
        
    #def on_leave(self):
        #changes = {k: v for k, v in state.position.items() if not self.enter_data[k] == state.position[k]}
        
        #uix.sidepanel.sidepanel.region = state.get('region').get('name')
        #uix.sidepanel.sidepanel.uik = state.get('uik')
        
        ###if not (self.region == state.region) or not (self.uik == state.uik):
            ###schedule('send_position')
        
        ###mokrug = get_mokrug(state.region, state.uik)
        ###if mokrug == state.mokrug and mokrug is not None:
            ###return  # same mokrug
        
        ###state.mokrug = mokrug
        
        ###if state.mokrug is None and self.region == state.region:
            ###return  # same region
        #import client
        #if not self.prev_regionid == state.get('region', {}).get('id'):
            #state._nursery.start_soon(client.update_campaigns)
        
