# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from app_state import state, on
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout


from .navigationdrawer.navigationdrawer import NavigationDrawer
from . import screeens

from button import Button

Builder.load_string('''
#:include constants.kv
#:import state app_state.state

<SidePanel>:
    orientation: 'vertical'
    spacing: dp(2)

    Widget:  # spacer
        height: 10
        size_hint: 1, None

    Button:
        id: region
        text: self.parent.region or 'Регион не выбран'
        on_release: root.on_click('position')
        background_color: transparent
        shorten: True
        text_size: self.width, None

    Button:
        id: uik
        text: f'УИК {self.parent.uik}' if self.parent.uik else 'УИК не выбран'
        on_release: root.on_click('position')
        background_color: transparent

    Button:
        text: 'Профиль'
        on_release: root.on_click('userprofile')
        background_color: teal

    Button:
        text: 'Анкеты'
        on_release: root.on_click('formlist')
        background_color: teal

    Button:
        text: 'Журнал'
        on_release: root.on_click('events')
        background_color: teal

    Button:
        text: 'Координаторы'
        on_release: root.on_click('coordinators')
        background_color: transparent
        disabled: True

    #Button:
        #text: 'Сообщения'
        #on_release: root.on_click('messages')
        #background_color: transparent
        #disabled: True

    Widget:  # spacer

    Button:
        text: 'О программе'
        on_release: root.on_click('about')
        background_color: transparent

''')


class SidePanel(BoxLayout):
    manager = ObjectProperty()
    uik = ObjectProperty(allownone=True)
    region = ObjectProperty(allownone=True)
        
    #async def init(self):
        #if 'region' in state:
            #self.region = state.region.name
            
    @on('state.uik')
    def set_uik(self):
        print(f'uik {state.get("uik")}')
        self.uik = state.get('uik')
        
    @on('state.region')
    def set_region(self):
        print(f'region {state.get("region")}')
        self.region = state.get('region', {}).get('name')
        
        
    def on_click(self, screen):
        main_widget = self.parent.parent
        screeens.push_screen(screen)
        main_widget.state = 'closed'
