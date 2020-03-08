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
#from ..float_message import show_float_message

from paradox import uix
from paradox.uix import float_message
from paradox.models import Campaign


Builder.load_string('''
#:include constants.kv
##:import show_float_message paradox.uix.float_message.show
#:import state app_state.state


<NiceTextInput@TextInput>:
    background_active: ''
    background_normal: ''
    multiline: False
    size_hint: 1, None
    

<PositionScreen>:
    ScrollView:
        VBox:

            ChoicePicker:
                id: regions
                modal_header: 'Ваш регион:'
                text: 'выберите регион'
                shorten: True
                halign: 'left'
                on_text: self.color = black
                height: height1
                on_new_pick: state.region = state.regions[self.value]

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
                    text: str(state.uik) if state.uik else ''
                    on_focus_out: state.uik = int(self.text) if self.text.isnumeric() else None

            VBox:
                spacing: 0
                height: 2*height1
                size_hint_y: None

                Label:
                    text: 'Ваш статус:'
                    halign: 'left'
                    text_size: self.width, None
                    padding: 0, 0

                ChoicePicker:
                    id: roles
                    choice: self.getchoice(state.role)
                    height: self.texture_size[1]
                    modal_header: 'Ваш статус:'
                    text: 'выберите статус'
                    halign: 'left'
                    on_text: self.color = black
                    padding: 0, 0
                    on_value: state.role = self.value

                    Choice:
                        text: 'Член комиссии с правом решающего голоса (ПРГ)'
                        short_text: 'ПРГ'
                        value: 'prg'

                    Choice:
                        text: 'Член комиссии с правом совещательного голоса (ПСГ)'
                        short_text: 'ПСГ'
                        value: 'psg'

                    Choice:
                        text: 'Наблюдатель'
                        value: 'nabludatel'

                    Choice:
                        text: 'Представитель СМИ (Журналист)'
                        short_text: 'Журналист'
                        value: 'smi'

                    Choice:
                        text: 'Кандидат'
                        value: 'kandidat'

                    Choice:
                        text: 'Избиратель (это ваш участок для голосования)'
                        short_text: 'Избиратель'
                        value: 'izbiratel'

                    Choice:
                        text: 'Мимо проходил (это не ваш участок для голосования)'
                        short_text: 'Мимо проходил'
                        value: 'other'
                        
                    Choice:
                        text: 'Видео-наблюдатель'
                        value: 'videonabl'

            Label:
                text: state.munokrug.name if state.munokrug else ''
                
            Label:
                text: 'ТИК ' + state.tik.name if state.tik else ''
                
            Widget:  #spacer
                height: dp(15)

            Button:
                id: next
                text: 'Продолжить'
                on_release: root.manager.push_screen('userprofile')
                background_color: darkgray

''')


#from getinstance import InstanceManager


class PositionScreen(Screen):
    #def __init__(self, *args, **kwargs):
        #super().__init__(*args, **kwargs)
        
    @on('state.regions')
    def build_regions(self):
        if not state.get('regions', None):
            return
        #import ipdb; ipdb.sset_trace()
        logger.debug('rebuilding region choices')
        #regions = state.regions.values()
        self.ids.regions.clear()

        msk, spb, lo = 'ru_77', 'ru_78', 'ru_47'
        #msk = list(filter(lambda x: 'Москва' in x['name'], regions))
        #spb = list(filter(lambda x: 'Санкт' in x['name'], regions))
        #lo = list(filter(lambda x: 'Ленинградская' in x['name'], regions))

        #choice = Choice(text='Москва', value=)
        #self.ids.regions.add_widget(choice)
        
        choice = Choice(text='Санкт-Петербург', value='ru_78')
        self.ids.regions.add_widget(choice)

        choice = Choice(text='Ленинградская область', value='ru_47')
        self.ids.regions.add_widget(choice)

        for region in sorted(state.regions.values(), key=lambda x: x['name']):
            if region['id'] in (spb, lo) or not region['id'].startswith(state.country):
                continue
            self.ids.regions.add_widget(Choice(text=region['name'], value=region['id']))
            
        if state.get('region'):
            choice = self.ids.regions.getchoice(state.region.id)
            if choice:
                self.ids.regions.choice = choice
                
    #@on('state.role')
    #def set_role(self):
        ##if state.get('role'):
        #self.ids.roles.choice = self.ids.roles.getchoice(state.get('role'))
            
    #@on('state.uik')
    #def set_uik(self):
        #self.uik = str(state.get('uik', '') or '')
  
    @on('state.uik', 'state.region')
    def update_munokrug_tik(self):
        #import ipdb; ipdb.sset_trace()
        state.munokrug = self.get_munokrug()
        state.tik = self.get_tik()
        #logger.debug(f'Mokrug: {self.munokrug}. Tik: {self.tik}')
        
    def get_munokrug(self):
        if not state.uik or not state.region:
            return None
        for munokrug in state.region.get('munokruga', []):
            for first, last in munokrug.uik_ranges:
                if first <= int(state.uik) <= last:
                    return munokrug
        return None
    
    def get_tik(self):
        if not state.uik or not state.region:
            return None
        for tik in state.region.get('tiks', []):
            #if isinstance()
            for first, last in tik.uik_ranges:
                if first <= int(state.uik) <= last:
                    return tik
        return None
                   
    def show_errors(self):
        errors = []
        if not self.ids.regions.choice:
            errors.append('Выберите регион')
        if not self.ids.uik.text:
            errors.append('Введите номер УИК')
        if not self.ids.roles.choice:
            errors.append('Укажите ваш статус')
        if errors:
            errors = 'Пожалуйста заполните обязательные поля\n\n' + '\n'.join(errors)
            uix.float_message.show(text=errors)
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
        
        ###munokrug = get_munokrug(state.region, state.uik)
        ###if munokrug == state.munokrug and munokrug is not None:
            ###return  # same munokrug
        
        ###state.munokrug = munokrug
        
        ###if state.munokrug is None and self.region == state.region:
            ###return  # same region
        #import client
        #if not self.prev_regionid == state.get('region', {}).get('id'):
            #state._nursery.start_soon(client.update_campaigns)
        
