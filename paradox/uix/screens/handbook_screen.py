# -*- coding: utf-8 -*-

from __future__ import unicode_literals

#from os.path import exists
import traceback

from kivy.core.window import Window
from kivy.app import App
#from kivy.garden.anchoredscrollview import AnchoredScrollView
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.vkeyboard import VKeyboard
from kivy.utils import platform


#from kivy.uix.textinput import TextInput
#from


Builder.load_string('''
#:include constants.kv

<HandBookScreen>:
    #text: 'lol'
    #header: 'lol'
    ScrollView:
        id: scrollview

        VBox:
            Label:
                id: text
                #split_str: ' '
                #text_size: self.width, None
                ##height: dp(100)
                #height: self.texture_size[1]
                #background_color: lightgray
                #text: root.text
                #halign: 'left'
                #padding: dp(10), dp(10)

                font_size: sp(18)
                #background_active: ''
                #background_normal: ''
                size_hint_y: None
                #height: self.minimum_height
                #readonly: True
                #on_double_tap: Clock.schedule_once(lambda dt: self.select_all())

                split_str: ' '
                text_size: self.width, None
                height: self.texture_size[1]
                markup: True
                halign: 'left'


            VBox:
                height: height1
                BoxLayout:
                    height: height1
                    spacing: dp(2)

                    Button:
                        text: '< Назад'
                        on_press: root.manager.pop_screen()
                        halign: 'left'
                        text_size: self.size
                        size_hint: None, None
                        width: dp(150)
                        background_color: white
                        color: teal


                    Widget:  # spacer


''')



#txt = '''
#[TODO] Согласно п.13 статьи 62 закона об Основных Гарантиях Избирательных Прав бла-бла
#На практике иногда бла-бла
#Нарушение попадает под п. такой-то п статьи такой-то КоАП.
#Обжаловать нарушение закона можно будет после голосования в течение Х дней в Территориальной комиссии. Также нарушитель может быть привлечен к отвественности по заявлению от ... в течение Х дней в ... Суд.
#'''


#imput_help_stub = '''
#Здесь будет справочная информация: ссылки на закон, порядок действий в случае нарушения, итд.
#'''


class HandBookScreen(Screen):
    def show_help(self, title, text):
        #label = question['label'].upper()
        #help_text = question['help_text'] or imput_help_stub
        self.ids['text'].text = f'{title.upper()}\n\n{text}'
        self.ids['scrollview'].scroll_y = 1
