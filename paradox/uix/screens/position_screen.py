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
from ...objects_manager import objects_manager
from ..vbox import VBox
from ..choices import Choice
from ..float_message import show_float_message



Builder.load_string('''
#:include constants.kv
#:import show_float_message paradox.uix.float_message.show_float_message
#:import schedule paradox.scheduler.schedule


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
                #on_choice: schedule('core.region_changed', self.choice)

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
                    #on_choice: schedule('core.status_changed', self.choice)

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

            Widget:  #spacer
                height: dp(15)

            Button:
                text: 'Продолжить'
                on_release: schedule(lambda: root.manager.push_screen('formlist'))
                background_color: darkgray

''')


@objects_manager
class RegionChoice(Choice):
    pass


@objects_manager
class StatusChoice(Choice):
    pass


class PositionScreen(Screen):
    data = ObjectProperty(None, allownone=True)

    #def __init__(self, *args, **kwargs):
        #super(PositionScreen, self).__init__(*args, **kwargs)
        #initial_data = App.app_store.get(b'position', {})
        #self.ids['uik'].text = initial_data.get('uik', '')
        #self.ids['region_choices'].text = initial_data.get('region_name', '')
        #self.ids['status_choices'].text = initial_data.get('status_name', '')
        #self.ids['uik'].bind(focus=self.input_focus)

    def get_data(self):
        return {
            'uik': self.ids['uik'].text,
            'region_id': self.ids['region_choices'].value,
            #'region_name': self.ids['region_choices'].text,
            'status': self.ids['status_choices'].value,
            #'status_name': self.ids['status_choices'].text,
        }

    #def input_focus(self, input, focus):
        #if not focus:
            ##data = {x: self.ids[x].text for x in self.inputs}
            #if input == self.ids['uik']:
                #schedule('core.uik_changed', self.ids['uik'].text)

    def build_regions(self, data):
        if data == self.data:
            return
        self.data = data

        for choice in self.ids['region_choices'].choices():
            self.ids['region_choices'].remove_choice(choice.value)

        msk = filter(lambda x: 'Москва' in x['name'], data)[0]
        spb = filter(lambda x: 'Санкт' in x['name'], data)[0]
        lo = filter(lambda x: 'Ленинградская' in x['name'], data)[0]

        #choice = RegionChoice(short_text='Москва', text='Москва', value=msk['id'])
        #self.ids['region_choices'].add_widget(choice)
        
        choice = RegionChoice(
            short_text='Санкт-Петербург', text='Санкт-Петербург', value=spb['id'])
        self.ids['region_choices'].add_widget(choice)

        choice = RegionChoice(
            short_text='Ленинградская область', text='Ленинградская область', value=lo['id'])
        self.ids['region_choices'].add_widget(choice)


        for region in sorted(data, key=lambda x: x['name']):
            if region in [spb, lo]:
                continue
            name = region['name'].encode('utf8')
            choice = RegionChoice(short_text=name, text=name, value=region['id'])
            self.ids['region_choices'].add_widget(choice)

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
