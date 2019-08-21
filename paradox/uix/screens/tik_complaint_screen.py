# -*- coding: utf-8 -*-

from __future__ import unicode_literals

#from os.path import exists
import traceback

from django.utils.timezone import now
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
from loguru import logger


from ..float_message import show_float_message
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
                #text: 'Запрос отправлен'
                size_hint_y: None
                color: white
                background_color: wheat4
                #height: 0
                #opacity: 0
                
            VBox:
                id: complaint_preview
                Label:
                    id: complaint_label
                    text: root.text or ''
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
                    id: edit_button
                    text: 'Редактировать текст'
                    on_release: root.on_edit_pressed()
                    color: teal
                    
                Button:
                    id: send_button
                    text: 'Отправить'
                    on_release: root.on_send_pressed()
                    color: teal
                
            VBox:
                id: complaint_edit
                visible: False
                
                TextInput:
                    id: complaint_textinput
                    text: ''
                    color: black
                    multiline: True
                    #height: root.height * 0.6
                    
                    height: self.minimum_height
                    size_hint_y: None
                
                Button:
                    id: save
                    color: teal
                    text: 'Сохранить'
                    on_release: root.on_save_pressed()
                
            VBox:
                height: height1
                BoxLayout:
                    height: height1
                    spacing: dp(2)

                    Button:
                        id: back
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
        self.ids.complaint_preview.visible = False
        self.ids.complaint_textinput.text = self.text
        self.ids.complaint_edit.visible = True
        
    def on_save_pressed(self):
        self.ids.complaint_preview.visible = True
        self.text = self.ids.complaint_textinput.text
        self.ids.complaint_edit.visible = False
        
    def on_send_pressed(self):
        self.complaint.input.last_event.update(
            tik_complaint_status='request_pending',
            tik_complaint_text=self.text,
            time_updated=now()
        )
        show_float_message('Запрос отправляется')
        self.ids.header.text = 'ЗАПРОС ОТПРАВЛЯЕТСЯ'
        self.ids.edit_button.disabled = True
        self.ids.send_button.disabled = True
        
    def show(self, complaint):
        event = complaint.input.last_event
        #logger.debug(f'{complaint.input} {event}, tik_complaint_status: {event.tik_complaint_status}')
        self.text = event.tik_complaint_text or complaint.tik_text
        #if complaint.input.last_event.tik_complaint_text:
            #complaint.tik_text
        self.complaint = complaint
        #label = input_data['label'].upper()
        #help_text = input_data['help_text'] or imput_help_stub
        if not event.tik_complaint_status or event.tik_complaint_status == 'none':
            self.ids.header.text = 'ПРОВЕРЬТЕ ТЕКСТ ЖАЛОБЫ'
            self.ids.edit_button.disabled = False
            self.ids.send_button.disabled = False
        elif event.tik_complaint_status == 'request_pending':
            self.ids.header.text = 'ЗАПРОС ОТПРАВЛЯЕТСЯ'
            self.ids.edit_button.disabled = True
            self.ids.send_button.disabled = True
        elif event.tik_complaint_status == 'request_sent':
            self.ids.header.text = 'ЗАПРОС ОТПРАВЛЕН'
            self.ids.edit_button.disabled = True
            self.ids.send_button.disabled = True
        else:
            raise Exception(event.tik_complaint_status)
        
            
        #self.ids.complaint_label.text = self.text
        self.ids['scrollview'].scroll_y = 1
