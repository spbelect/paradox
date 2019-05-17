# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from getinstance import InstanceManager
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors.togglebutton import ToggleButtonBehavior
from kivy.uix.togglebutton import ToggleButton
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty, Property

from .vbox import VBox
from .base_input import Input
from label import Label
from button import Button
from .choices import Choice
from paradox import utils
from .imagepicker import ImagePicker

Builder.load_string('''
#:include constants.kv

#:import state app_state.state

#:import uix paradox.uix

<Complaint>:
    #size_hint_y: None
    hidden: True
    
    Button:
        height: dp(20)
        size_hint_y: None
        #background_color: white
        #background_color: lightblue
        text: "Обжалование в УИК"
        color: black
        font_size: dp(20)
        #text: "Обжалование в УИК ◂"
        
        text_size: self.width, None
        #halign: 'left'
        
    BoxLayout:
        size_hint_y: None
        height: dp(16)
        Button:
            #background_color: lightblue
            
            #halign: 'left'
            text_size: self.width, None
            height: dp(16)
            color: lightblue
            size_hint_y: None
            #background_color: white
            text: 'пример жалобы'
            font_size: dp(16)
            #he
            on_release: uix.screeens.show_handbook(root.json['label'], root.json['example_uik_complaint'])
            
        Button:
            #halign: 'right'
            text_size: self.width, None
            height: dp(16)
            size_hint_y: None
            color: lightblue
            text: 'правила обжалования'
            font_size: dp(16)
            on_release: uix.screeens.show_handbook('правила обжалования', 'bla')

    Widget: #spacer
        height: dp(1)
    Label:
        font_size: dp(16)
        height: dp(16)
        size_hint_y: None
        text: 'сфотографируйте жалобу и акт'
        
        text_size: self.width, None
        #halign: 'left'
        
    ImagePicker:
        on_input: root.on_uik_complaint_image_input(type='uik_complaint', filepath=args[0])
        
    Widget: #spacer
        height: dp(1)
    Label:
        font_size: dp(16)
        height: dp(16)
        size_hint_y: None
        
        text_size: self.width, None
        text: 'укажите статус жалобы'
        #halign: 'left'
        
    Choices:
        height: dp(18)
        font_size: dp(18)
        height: self.texture_size[1]
        modal_header: 'Статус жалобы'
        text: 'выберите статус'
        text_size: self.width, None
        #halign: 'left'
        on_text: self.color = black
        padding: 0, 0
        on_input: root.on_uik_complaint_status_input(self.value)
        size_hint_y: None
                
        ComplaintStatusChoice:
            value: 'none'
            text: 'не подавалась'
            short_text: 'не подавалась'
            
        ComplaintStatusChoice:
            value: 'refuse_to_accept'
            text: 'отказ принять жалобу'
            short_text: 'отказ принять жалобу'
            
        ComplaintStatusChoice:
            value: 'refuse_to_resolve'
            text: 'отказ рассмотрения жалобы'
            short_text: 'отказ рассмотрения'
            
        ComplaintStatusChoice:
            value: 'waiting_reply'
            text: 'ожидание решения комиссии'
            short_text: 'ожидание решения'
            
        ComplaintStatusChoice:
            value: 'got_unfair_reply'
            text: 'получено неудовлетворительное решение'
            short_text: 'получено неуд. решение'
            
        ComplaintStatusChoice:
            value: 'got_fair_reply'
            text: 'получено удовлетворительное решение'
            short_text: 'получено удовл. решение'


''')


class Complaint(VBox):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.modal = ChoicesModal(choices=self)
        self.register_event_type('on_uik_complaint_status_input')
        self.register_event_type('on_uik_complaint_image_input')
        #self.hide()

    def on_uik_complaint_status_input(self, value):
        pass
    
    def on_uik_complaint_image_input(self, filepath, uuid):
        pass
    
    
