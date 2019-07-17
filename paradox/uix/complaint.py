# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from asyncio import sleep

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
from paradox.models import InputEventImage, InputEvent

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
        
        Label:
            pos: self.parent.pos
            size: self.parent.size
            id: loader
            font_size: dp(20)
            opacity: 0
            text: 'загрузка...'
            background_color: wheat4
        
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
                uix.screenmgr.show_handbook(root.input.json['label'], root.input.json['example_uik_complaint'])
            
        Button:
            #halign: 'right'
            text_size: self.width, None
            height: dp(32)
            size_hint_y: None
            color: lightblue
            text: 'правила обжалования'
            font_size: dp(14)
            on_release: uix.screenmgr.show_handbook('правила обжалования', 'TODO')

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
        #on_image_picked: root.on_image_picked(filepath)
        
        
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

class ComplaintStatusChoice(Choice):
    instances = InstanceManager()
    
    
class ComplaintPhotoPicker(ImagePicker):
    type = StringProperty()
    input = ObjectProperty()
    
    def on_image_picked(self, filepath):
        #existing = InputEventImage.objects.filter()
        logger.info(f'create image {filepath}')
        dbimage, created = InputEventImage.objects.get_or_create(
            type=self.type, 
            event=self.input.last_event,
            filepath=filepath
        )
        
        logger.debug(list(InputEventImage.objects.values_list('filepath', flat=True)))
        if dbimage.deleted:
            logger.debug('undelete')
            dbimage.update(deleted=False, time_updated=now())
            uxitem = self.add_image(filepath)
            uxitem.dbid = dbimage.id
        elif created:
            uxitem = self.add_image(filepath)
            uxitem.dbid = dbimage.id
        
    def on_cross_click(self, cross):
        super().on_cross_click(cross)
        InputEventImage.objects.get(id=cross.parent.dbid).update(
            deleted=True,
            time_updated=now()
        )

class Complaint(VBox):
    input = ObjectProperty()
    #event = ObjectProperty(None, allow_none=True)
    
    @utils.asynced
    async def on_event(self, event):
        #logger.debug(event, event.revoked)
        if event is None:
            self.visible = False
            return
        
        if event.revoked or not event.alarm:
            self.visible = False
            return
            
        self.visible = True
        self.ids.loader.opacity = 1
        self.ids.uik_complaint_status = ComplaintStatusChoice.instances.get(value=event.uik_complaint_status)
        
        await sleep(0.1)
        
        self.ids.uik_complaint_images.del_images()
        self.ids.uik_reply_images.del_images()
        
        logger.debug(f'{self.input.json["label"]}: restore {event.images.count()} images for event {event.id}')
        for dbimage in event.images.all():
            if dbimage.deleted:
                logger.debug(f'image {dbimage.filepath} was deleted by user')
                continue
            
            if dbimage.type == 'uik_complaint':
                uxitem = self.ids.uik_complaint_images.add_image(dbimage.filepath)
            elif dbimage.type == 'uik_reply':
                uxitem = self.ids.uik_reply_images.add_image(dbimage.filepath)
                
            uxitem.dbid = dbimage.id
            await sleep(0.1)
                #('tik_complaint', 'Подаваемые в ТИК жалобы'),
                #('tik_reply', 'Ответы, решения от ТИК'),'
        self.ids.loader.opacity = 0
                
    #def __init__(self, *args, **kwargs):
        #super().__init__(*args, **kwargs)
        
    def on_uik_complaint_status_input(self, value):
        logger.debug(f'{self.input.last_event.id}, {value}')
        InputEvent.objects.filter(id=self.input.last_event.id).update(
            uik_complaint_status=value, time_updated=now()
        )
        
        
