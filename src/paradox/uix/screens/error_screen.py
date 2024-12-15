# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from textwrap import dedent

from kivy.lang import Builder
from kivy.properties import StringProperty, Property
from kivy.uix.screenmanager import Screen

from ...config import DEBUG


Builder.load_string('''
#:import Clock kivy.clock.Clock
#:include constants.kv

<ErrorScreen>:
    canvas.before:
        Color:
            #rgba: 1,1,1,1
            rgba: white
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: 'vertical'

        ScrollView:
            TextInput:
                font_size: sp(18)
                background_active: ''
                background_normal: ''
                size_hint_y: None
                height: self.minimum_height
                text: root.intro_text + (root.message if root.debug else '')
                readonly: True
                on_focus: Clock.schedule_once(lambda dt: self.select_all())
                on_double_tap: Clock.schedule_once(lambda dt: self.select_all())

        Button:
            text: 'Выйти'
            on_press: app.stop()
            background_color: darkgray


<Button>:
    #color: 1,1,1,1
    color: white
    height: dp(50)
    halign: 'center'
    size_hint: 1, None
    background_normal: ''

''')


class ErrorScreen(Screen):
    message = StringProperty()
    debug = DEBUG

    intro_text = dedent('''
    Произошла ошибка.
    При наличии связи разработчики будут уведомлены.
    
    ''')
