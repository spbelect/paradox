# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from app_state import state, on
from datetime import datetime
from getinstance import InstanceManager
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen

from ...utils import strptime
from ..vbox import VBox
from button import Button
from paradox.models import InputEvent


Builder.load_string('''
#:include constants.kv

<EventsScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(4)
        spacing: dp(8)

        Label:
            padding_x: dp(4)
            split_str: ' '
            text_size: self.width, None
            height: self.texture_size[1] + 10
            text: root.form_name
            color: white
            background_color: teal
            text: 'Журнал'
            size_hint_y: None

        ScrollView:
            scroll_y: 0
            VBox:
                id: content
                spacing: 0

<EventLogItem>:
    text_size: self.width, None
    font_size: sp(16)
    height: self.texture_size[1]
    size_hint_y: None
    halign: 'left'
    markup: True
    color: black


''')


class EventLogItem(Button):
    input_json = ObjectProperty(None)


#class PositionItem(Label):
    #pass


class EventsScreen(Screen):
    #instances = InstanceManager()
    
    def __init__(self, *args, **kwargs):
        super(EventsScreen, self).__init__(*args, **kwargs)
        self.last_uik = None
        self.last_region = None
        self.last_date = None
        #events = 
        
    def restore_past_events(self):
        for item in self.ids.content.children[:]:
            self.ids.content.remove_widget(item)
            
        for event in InputEvent.objects.order_by('time_created'):
            self.add_event(event)

    def add_event(self, event):
        if event.input_id not in state.get('inputs', {}):
            return
        
        uptime = event.time_updated.astimezone()
        if self.last_uik != event.uik or self.last_region != event.region:
            region = state.regions.get(event.region, {}).get('name')
            self.ids['content'].add_widget(EventLogItem(
                halign='center', 
                text=f'[color=#444]\n{region}\nУИК {event.uik}[/color]'
            ))
            self.last_uik, self.last_region = event.uik, event.region

        if self.last_date != uptime.date():
            self.ids['content'].add_widget(EventLogItem(
                text=f'[color=#444]{uptime.strftime("%d.%m.%Y")}[/color]'
            ))
            self.last_date = uptime.date()

        #if isinstance(event['value'], bool):
            #event['value'] = 'Да' if event['value'] else 'Нет'

        uptime = uptime.strftime("%H:%M")
        ctime = event.time_created.astimezone().strftime("%H:%M")
        
        if event.revoked:
            text = f'[color=#444]{uptime}[/color] отозвано: [s]{ctime} {event.input_label}: {event.get_value()}[/s]'
        else:
            text = f'[color=#444]{uptime}[/color] {event.input_label}: {event.get_value()}'
        item = EventLogItem(input_json=state.inputs[event.input_id], text=text)
        self.ids['content'].add_widget(item)
        item.bind(on_long_press=self.on_event_press)

    def on_event_press(self, item):
        self.manager.show_handbook(item.input_json['label'], item.input_json['fz67_text'])
