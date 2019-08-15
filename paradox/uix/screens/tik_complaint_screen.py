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

<TikComplaintScreen>:
    ScrollView:
        id: scrollview

        VBox:
            Label:
                id: header
                #text: 'Запрос отравлен'
                size_hint_y: None
                #height: 0
                #opacity: 0
            VBox:
                id: complaint_preview
                Label:
                    id: complaint_label
                    text: root.text
                    #split_str: ' '
                    #text_size: self.width, None
                    ##height: dp(100)
                    #height: self.texture_size[1]
                    #background_color: lightgray
                    #text: root.text
                    #halign: 'left'
                    #padding: dp(10), dp(10)

                    font_size: sp(18)
                    size_hint_y: None
                    #background_active: ''
                    #background_normal: ''
                    #height: self.minimum_height
                    #readonly: True
                    #on_double_tap: Clock.schedule_once(lambda dt: self.select_all())

                    split_str: ' '
                    text_size: self.width, None
                    height: self.texture_size[1]
                    markup: True
                    halign: 'left'

                Button:
                    text: 'Редактировать текст'
                    on_release: root.on_edit_pressed()
                    
                Button:
                    text: 'Отправить'
                    on_release: root.on_send_pressed()
                
            VBox:
                id: complaint_edit
                visible: False
                
                TextInput:
                    id: complaint_textinput
                
                Button:
                    text: 'Сохранить'
                    on_release: root.on_save_pressed()
                
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


class TikComplaintScreen(Screen):
    text = StringProperty(None, allownone=True)
    
    def on_edit_pressed(self):
        self.complaint_preview.visible = False
        self.complaint_textinput.text = self.text
        self.complaint_edit.visible = True
        
    def on_save_pressed(self):
        self.complaint_preview.visible = True
        self.text = self.complaint_textinput.text
        self.complaint_edit.visible = False
        
    def on_send_pressed(self):
        self.complaint.input.last_event.update(
            tik_complaint_status='request_pending',
            tik_complaint_text=self.text
        )
        self.ids.header.text = 'ЗАПРОС ОТПРАВЛЯЕТСЯ'
        
    def show(self, complaint):
        event = complaint.input.last_event
        self.text = event.tik_complaint_text or complaint.tik_text
        #if complaint.input.last_event.tik_complaint_text:
            #complaint.tik_text
        self.complaint = complaint
        #label = input_data['label'].upper()
        #help_text = input_data['help_text'] or imput_help_stub
        if not event.tik_complaint_status:
            self.ids.header.text = 'ПРОВЕРЬТЕ ТЕКСТ ЖАЛОБЫ'
        elif event.tik_complaint_status == 'request_pending':
            self.ids.header.text = 'ЗАПРОС ОТПРАВЛЯЕТСЯ'
        elif event.tik_complaint_status == 'request_sent':
            self.ids.header.text = 'ЗАПРОС ОТПРАВЛЕН'
            
        #self.ids.complaint_label.text = self.text
        self.ids['scrollview'].scroll_y = 1
