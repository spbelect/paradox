# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from asyncio import sleep

from app_state import state, on
from django.utils.timezone import now
from getinstance import InstanceManager
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors.togglebutton import ToggleButtonBehavior
from kivy.uix.togglebutton import ToggleButton
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty, Property
from loguru import logger

from .vbox import VBox
from label import Label
from button import Button
from .choices import Choice
from paradox import utils
from .imagepicker import ImagePicker
from paradox.models import AnswerImage, Answer

Builder.load_string('''
#:include constants.kv

#:import state app_state.state

#:import uix paradox.uix

<Complaint>:
    #size_hint_y: None
    visible: False

    #padding: 0
    #spacing: 0
    #visible: True
    
    #width: 0.9 * getattr(self.parent, 'width', 10)
    #json: self.quizwidget.json
    #example_uik_complaint: self.quizwidget.question.example_uik_complaint
    
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
        
        #Label:
            #pos: self.parent.pos
            #size: self.parent.size
            #id: loader
            #font_size: dp(20)
            #opacity: 0
            #text: 'загрузка...'
            #background_color: wheat4
        
    BoxLayout:
        size_hint_y: None
        height: dp(22)
        padding: 0
        spacing: 0
        Button:
            #background_color: lightblue
            
            #halign: 'left'
            text_size: self.width, None
            height: dp(32)
            color: lightblue
            size_hint_y: None
            #background_color: white
            text: 'пример жалобы'
            font_size: dp(14)
            #he
            on_release: 
                uix.screenmgr.show_handbook(root.quizwidget.question.label, root.uik_complaint_text)
            
        Button:
            #halign: 'right'
            text_size: self.width, None
            height: dp(32)
            size_hint_y: None
            color: lightblue
            text: 'правила обжалования'
            font_size: dp(14)
            on_release: uix.screenmgr.show_handbook('правила обжалования', root.complaint_rules)

    Widget: #spacer
        height: dp(1)
        size_hint_y: None
        
    Label:
        font_size: dp(16)
        height: dp(16)
        size_hint_y: None
        text: 'сфотографируйте жалобу и акт'
        
        text_size: self.width, None
        #halign: 'left'
        
    ComplaintPhotoPicker:
        id: uik_complaint_images
        type: 'uik_complaint'
        quizwidget: root.quizwidget
        compress_quality: 40
        #on_image_picked: root.on_image_picked(filepath)
        
        
    Widget: #spacer
        height: dp(1)
        size_hint_y: None
        
    Label:
        font_size: dp(16)
        height: dp(16)
        size_hint_y: None
        
        text_size: self.width, None
        text: 'укажите статус жалобы'
        #halign: 'left'
        
    ChoicePicker:
        id: uik_complaint_status
        height: dp(18)
        font_size: dp(18)
        height: self.texture_size[1]
        modal_header: 'Статус жалобы'
        text: 'выберите статус'
        text_size: self.width, None
        #halign: 'left'
        on_text: self.color = black
        padding: 0, 0
        on_new_pick: root.on_uik_complaint_status_input(self.value)
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
            
        #ComplaintStatusChoice:
            #value: 'refuse_to_copy_reply'
            #text: 'отказ выдать копию решения'
            #short_text: 'отказ выдать копию решения'
            
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

    Widget: #spacer
        height: dp(1)
        size_hint_y: None
        
    VBox:
        #id: uik_reply_images
        Label:
            font_size: dp(16)
            height: dp(16)
            size_hint_y: None
            text: 'сфотографируйте решение'
            
            text_size: self.width, None
            #halign: 'left'
            
        ComplaintPhotoPicker:
            id: uik_reply_images
            type: 'uik_reply'
            quizwidget: root.quizwidget
            compress_quality: 40
            #on_new_pick: root.quizwidget.complaint_image_create(*args[1:])
            
    
    VBox:
        id: tik_complaint
        #size_hint: None, None
        size_hint_y: None
            
        #padding: 0
        #spacing: 0
        visible: False
            
        Widget: #spacer
            height: dp(1)
            size_hint_y: None
        
        Button:
            height: dp(20)
            size_hint_y: None
            text: "Обжалование в ТИК"
            color: black
            font_size: dp(20)
            #text: "Обжалование в ТИК ◂"
            
            text_size: self.width, None
            
            
        VBox:
            id: refuse_akt
            visible: False
            size_hint_y: None
            
            padding: 0
            spacing: 0
        
            Button:
                #halign: 'right'
                text_size: self.width, None
                height: dp(40)
                size_hint_y: None
                color: lightblue
                text: 'составьте акт об отказе'
                font_size: dp(14)
                on_release: uix.screenmgr.show_handbook('Составьте акт', root.refuse_akt_text())

            Widget: #spacer
                height: dp(1)
                size_hint_y: None
            
                
            Label:
                font_size: dp(16)
                height: dp(16)
                size_hint_y: None
                text: 'сфотографируйте акт'
                
                text_size: self.width, None
                #halign: 'left'
                
            ComplaintPhotoPicker:
                id: refuse_akt_images
                type: 'tik_complaint'
                quizwidget: root.quizwidget
                compress_quality: 40
                #on_image_picked: root.on_image_picked(filepath)
            
        
        
        VBox:
            
            id: refuse_person
            #visible: False
            size_hint_y: None
            
            #padding: 0
            spacing: 0
        
            Widget: #spacer
                height: dp(1)
                size_hint_y: None
                
            Label:
                font_size: dp(16)
                height: dp(16)
                size_hint_y: None
                
                text_size: self.width, None
                text: 'Укажите кому подавали жалобу'
                #halign: 'left'
                
            ChoicePicker:
                id: refuse_person_status
                height: dp(18)
                font_size: dp(18)
                height: self.texture_size[1]
                modal_header: 'Выберите статус'
                text: 'выберите статус'
                text_size: self.width, None
                #halign: 'left'
                on_text: self.color = black
                padding: 0, 0
                on_new_pick: root.on_refuse_person(self.value)
                size_hint_y: None
                        
                RefusePersonChoice:
                    value: 'член комиссии'
                    text: 'член комиссии (или неизвестно)'
                    short_text: 'член комиссии'
                    
                RefusePersonChoice:
                    value: 'председатель'
                    text: 'председатель'
                    short_text: 'председатель'
                    
                RefusePersonChoice:
                    value: 'зам. председателя'
                    text: 'зам. председателя'
                    short_text: 'зам. председателя'
                    
                RefusePersonChoice:
                    value: 'секретарь'
                    text: 'секретарь'
                    short_text: 'секретарь'
                    
        Button:
            id: preview_tik_complaint
            height: dp(40)
            size_hint_y: None
            text: "Обжаловать по Email"
            color: teal
            font_size: dp(20)
            text_size: self.width, None
            on_release: 
                uix.screenmgr.show_tik_complaint(root)
                #uix.screenmgr.show_handbook('Проверьте текст жалобы', root.tik_text)
            
            
#<ComplaintPhotoPicker>:

''')

