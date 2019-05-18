# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.timezone import now
from getinstance import InstanceManager
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors.togglebutton import ToggleButtonBehavior
from kivy.uix.togglebutton import ToggleButton
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty, Property
from loguru import logger

from .vbox import VBox
from .base_input import Input
from label import Label
from button import Button
from .choices import Choice
from paradox import utils
from .imagepicker import ImagePicker
from paradox.models import InputEventImage

Builder.load_string('''
#:include constants.kv

#:import state app_state.state

#:import uix paradox.uix

<Complaint>:
    #size_hint_y: None
    visible: False
    #visible: True
    
    #json: self.input.json
    #example_uik_complaint: self.input.json['example_uik_complaint']
    
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
            on_release: 
                uix.screeens.show_handbook(root.input.json['label'], root.input.json['example_uik_complaint'])
            
        Button:
            #halign: 'right'
            text_size: self.width, None
            height: dp(16)
            size_hint_y: None
            color: lightblue
            text: 'правила обжалования'
            font_size: dp(16)
            on_release: uix.screeens.show_handbook('правила обжалования', 'TODO')

    Widget: #spacer
        height: dp(1)
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
        input: root.input
        
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
            input: root.input
            #on_input: root.input.complaint_image_create(*args[1:])
            
<ComplaintPhotoPicker>:

''')

class ComplaintPhotoPicker(ImagePicker):
    type = StringProperty()
    input = ObjectProperty()
    
    def on_image_picked(self, filepath):
        #existing = InputEventImage.objects.filter()
        dbimage, created = InputEventImage.objects.get_or_create(
            type=self.type, 
            event=self.input.last_event,
            filepath=filepath
        )
        if dbimage.deleted:
            logger.debug('undelete')
            dbimage.update(deleted=False, time_updated=now())
            uxitem = self.add_image(filepath)
            uxitem.dbid = dbimage.id
        elif created:
            uxitem = self.add_image(filepath)
            uxitem.dbid = dbimage.id
        
    def del_image(self, cross):
        super().del_image(cross)
        InputEventImage.objects.get(id=cross.parent.dbid).update(
            deleted=True,
            time_updated=now()
        )

class Complaint(VBox):
    input = ObjectProperty()
    
    def set_past_events(self, events):
        last_event = events[-1]
        
        self.visible = last_event.alarm
        for dbimage in last_event.images.filter(deleted=False):
            if dbimage.type == 'uik_complaint':
                uxitem = self.ids.uik_complaint_images.add_image(dbimage.filepath)
                
            elif dbimage.type == 'uik_reply':
                uxitem = self.ids.uik_reply_images.add_image(dbimage.filepath)
            uxitem.dbid = dbimage.id
                #('tik_complaint', 'Подаваемые в ТИК жалобы'),
                #('tik_reply', 'Ответы, решения от ТИК'),'
                
    #def __init__(self, *args, **kwargs):
        #super().__init__(*args, **kwargs)
        
    def on_uik_complaint_status_input(self, value):
        self.input.last_event.update(uik_complaint_status=value, time_updated=now())
