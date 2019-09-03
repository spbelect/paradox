# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json
import itertools
from functools import wraps

from kivy.lang import Builder
#from kivy.properties import NumericProperty
#from kivy.properties import StringProperty

from app_state import state, on
from kivy.metrics import dp
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty, Property
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivy.uix.stacklayout import StackLayout
from kivy.uix.boxlayout import BoxLayout

from loguru import logger
import plyer
#import plyer.call

from label import Label
from ..click_label import ClickLabel
from ..vbox import VBox
from paradox import utils
from paradox import config
from paradox.models import Campaign, Coordinator


Builder.load_string('''
#:import Clock kivy.clock.Clock
#:import open_url paradox.utils.open_url
#:include constants.kv

#:import state app_state.state


<CoordinatorsScreen>:
    ScrollView:
        VBox:
            padding: '10dp'

            Label:
                #pos_hint: {'top': 1}
                #pos: self.parent.pos
                id: loader
                text: "Координаторы обновляются..."
                height: dp(40)
                opacity: 1
                font_size: sp(18)
                #width: self.parent.width
                #size_hint_y: None
                #size: self.parent.size
                background_color: wheat4
            
            VBox:
                spacing: '50dp'
                id: content
                
                
<CoordinatorItem>:
    Label:
        text: root.coordinator.name
        text_size: self.width, None
        #halign: 'left'

    VBox:
        id: contacts
        padding: 0
        spacing: 0
        

<ContactItem>:
    Image:
        source: root.image
        width: height1 + dp(20)
        size_hint_x: None

    ClickLabel:
        id: label
        text: root.text
            
''')


class ContactItem(BoxLayout):
    image = StringProperty()
    text = StringProperty()
    
    def __init__(self, *a, on_ref_press, **kw):
        super().__init__(*a, **kw)
        self.ids.label.bind(on_ref_press=on_ref_press)
        
        #input.ids['input_label']
        
    @staticmethod
    def open_url(*a):
        utils.open_url(a[1])
        
    @staticmethod
    @utils.asynced
    async def call(*a):
        
        #def call_permissionresult(permissions, grants):
            #logger.debug(f'{permissions} {grants}')
        #from android.permissions import request_permissions, Permission
        #logger.debug('request_permissions')
        if not await utils.ask_permissions('CALL_PHONE'):
            return
        plyer.call.makecall(a[1])
    
    
    
class CoordinatorItem(VBox):
    coordinator = ObjectProperty()
    
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.add_phones(self.coordinator.phones)
        self.add_channels(self.coordinator.external_channels)
        
        for campaign in self.coordinator.campaigns.positional().current():
            self.add_phones(campaign.phones)
            self.add_channels(campaign.external_channels)
            
    def add_channels(self, channels):
        images = {
            'vk': 'img/vkontakte-256.png',
            'fb': 'img/fb_icon_325x325.png',
            'tg': 'img/Telegram_alternative_logo.png',
            'wa': 'img/whatsapp.png'
        }
                
        for channel in json.loads(channels or '[]'):
            self.ids.contacts.add_widget(ContactItem(
                image=images[channel['type']],
                text='[color=#4AABFF][ref={url}]{name}[/ref][/color]'.format(**channel),
                on_ref_press=ContactItem.open_url
            ))
            
    def add_phones(self, phones):
        for phone in json.loads(phones or '[]'):
            self.ids.contacts.add_widget(ContactItem(
                image='img/Phone.png',
                text='[color=#4AABFF][ref={number}]{name} {number}[/ref][/color]'.format(**phone),
                on_ref_press=ContactItem.call
            ))


class CoordinatorsScreen(Screen):
    #def __init__(self, *a, **kw):
        #super().__init__(*a, **kw)
        
    def show(self, coordinators):
        for item in self.ids.content.children[:]:
            self.ids.content.remove_widget(item)
            
        for coord in coordinators:
            if coord.campaigns.positional().current().exists():
                if config.SHOW_TEST_COORDINATORS is False and 'test' in coord.name:
                    continue
                self.ids.content.add_widget(CoordinatorItem(coordinator=coord))
            
    @on('state.region')
    def show_current(self):
        #from paradox.models import Campaign, Coordinator
        campaigns = Campaign.objects.positional().current()
        #logger.debug(f'Active campaigns: {campaigns.values()}')
        self.show(Coordinator.objects.filter(campaigns__in=campaigns))
    
    def show_loader(self, f):
        @wraps(f)
        async def wrapped(*a, **kw):
            self.ids.loader.height = dp(40)
            self.ids.loader.opacity = 1
            #logger.debug(f'show coord loader {f}')
            try:
                return await f(*a, **kw)
            finally:
                #logger.debug(f'hide coord loader {f}')
                self.ids.loader.height = 0
                self.ids.loader.opacity = 0
        return wrapped

