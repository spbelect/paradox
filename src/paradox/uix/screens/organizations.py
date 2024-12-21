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

from paradox.uix.label import Label
from ..click_label import ClickLabel
from ..vbox import VBox
from paradox import utils
from paradox import config
from paradox.models import Campaign, Organization


Builder.load_string('''
#:import Clock kivy.clock.Clock
#:import open_url paradox.utils.open_url
#:include constants.kv

#:import state app_state.state


<OrganizationsScreen>:
    ScrollView:
        VBox:
            padding: '10dp'

            Label:
                id: loader
                text: "Координаторы обновляются..."
                height: dp(40)
                opacity: 1
                font_size: sp(18)
                background_color: wheat4
                
            Label:
                id: hint
                text: ""
                height: dp(40)
                opacity: 1
                font_size: sp(18)
                #background_color: wheat4
            
            VBox:
                spacing: '50dp'
                id: content
                
                
<OrganizationItem>:
    Label:
        text: root.organization.name
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
        
        #quizwidget.ids['question_label']
        
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
    
    
    
class OrganizationItem(VBox):
    organization = ObjectProperty()
    
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        contacts = json.loads(self.organization.contacts or '[]')
        self.add_phones(contacts)
        self.add_channels(contacts)
        
        #import ipdb; ipdb.sset_trace()
        for campaign in self.organization.campaigns.positional().current():
            contacts = json.loads(campaign.contacts or '[]')
            self.add_phones(contacts)
            self.add_channels(contacts)
            
    def add_channels(self, contacts):
        images = {
            'vk': 'img/vkontakte-256.png',
            'fb': 'img/fb_icon_325x325.png',
            'tg': 'img/Telegram_alternative_logo.png',
            'wa': 'img/whatsapp.png',
            'uk': ''
        }
                
        for contact in contacts:
            if not contact['type'] == 'ph':
                self.ids.contacts.add_widget(ContactItem(
                    image = images.get(contact['type'], None),
                    text = '[color=#4AABFF][ref={value}]{name}[/ref][/color]'.format(**contact),
                    on_ref_press = ContactItem.open_url
                ))
            
    def add_phones(self, contacts):
        for contact in contacts:
            if contact['type'] == 'ph':
                self.ids.contacts.add_widget(ContactItem(
                    image='img/Phone.png',
                    text='[color=#4AABFF][ref={value}]{name} {value}[/ref][/color]'.format(**contact),
                    on_ref_press=ContactItem.call
                ))


class OrganizationsScreen(Screen):
    #def __init__(self, *a, **kw):
        #super().__init__(*a, **kw)
        
    def show(self, organizations):
        for item in self.ids.content.children[:]:
            self.ids.content.remove_widget(item)
            
        for org in organizations:
            if org.campaigns.positional().current().exists():
                if config.SHOW_TEST_COORDINATORS is False and 'test' in org.name:
                    continue
                self.ids.content.add_widget(OrganizationItem(organization=org))
            
    @on('state.region', 'state.uik')
    def show_current(self):
        if not state.get('region'):
            self.ids.hint.text = 'Регион не выбран'
            return
        if not state.get('uik'):
            self.ids.hint.text = 'УИК не выбран'
            return
        self.ids.hint.text = ''
        #from paradox.models import Campaign, Organization
        campaigns = Campaign.objects.positional().current()
        #logger.debug(f'Active campaigns: {campaigns.values()}')
        self.show(Organization.objects.filter(campaigns__in=campaigns))
    
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



organizations = OrganizationsScreen(name='organizations')
