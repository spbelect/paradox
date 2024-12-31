# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from app_state import state, on
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout


#from .navigationdrawer.navigationdrawer import NavigationDrawer
from paradox import uix

from paradox.uix.button import Button

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
        text: state.region.name or 'Регион не выбран'
        on_release: root.on_screen_click('position')
        background_color: transparent
        shorten: True
        text_size: self.width, None

    Button:
        id: uik
        text: f'УИК {state.uik}' if state.uik else 'УИК не выбран'
        on_release: root.on_screen_click('position')
        background_color: transparent

    Button:
        text: 'Профиль'
        on_release: root.on_screen_click('userprofile')
        background_color: teal

    Button:
        text: 'Анкеты'
        on_release: root.on_screen_click('home')
        background_color: teal

    Button:
        text: 'Журнал'
        on_release: root.on_screen_click('events')
        background_color: teal

    Button:
        text: 'Координаторы'
        on_release: root.on_screen_click('organizations')
        #background_color: transparent
        background_color: teal
        #disabled: True

    #Button:
        #text: 'Сообщения'
        #on_release: root.on_screen_click('messages')
        #background_color: transparent
        #disabled: True

    Widget:  # spacer

    Button:
        text: 'О программе'
        on_release: root.on_screen_click('about')
        background_color: transparent

''')


class SidePanel(BoxLayout):
    #manager = ObjectProperty()
    #async def init(self):
        #if 'region' in state:
            #self.region = state.region.name
            
    def on_screen_click(self, screen: str):
        main_widget = self.parent.parent
        uix.screenmgr.push_screen(screen)
        main_widget.state = 'closed'
