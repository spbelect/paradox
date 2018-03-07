# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout

# Workaround for issue with rules precedence
Builder.load_file(b'base.kv')

# It has to be imported first to register new Label and Button with Factory
from .label import Label
from .button import Button

from .navigationdrawer.navigationdrawer import NavigationDrawer
from .screens.screens import Screens


Builder.load_string('''
#:include constants.kv

<SidePanel>:
    orientation: 'vertical'
    spacing: dp(2)

    Widget:  # spacer
        height: 10
        size_hint: 1, None

    Button:
        id: region
        text: 'Регион не выбран'
        on_release: root.on_click('position')
        background_color: transparent
        shorten: True
        text_size: self.width, None

    Button:
        id: uik
        text: 'УИК не выбран'
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
        text: 'Связь'
        on_release: root.on_click('communication')
        background_color: transparent

    Widget:  # spacer

    Button:
        text: 'О программе'
        on_release: root.on_click('about')
        background_color: transparent



<MainWidget>:
    touch_accept_width: dp(45)  # width to toggle navigation drawer
    side_panel_width: min(dp(450), 0.8*self.width)
    min_dist_to_open: 0.25
    min_dist_to_close: 0.1
    opening_transition: 'linear'
    closing_transition: 'linear'
    anim_time: 0.1

    SidePanel:
        id: side_panel

    Screens:
        id: screens

''')


class MainWidget(NavigationDrawer):
    pass


class SidePanel(BoxLayout):
    manager = ObjectProperty()

    def on_click(self, screen):
        main_widget = self.parent.parent
        main_widget.ids['screens'].push_screen(screen)
        main_widget.state = 'closed'
