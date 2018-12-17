# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import time

from datetime import datetime
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen

from ...utils import utc_to_local, strptime
from ..vbox import VBox
from ..button import Button


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
    def __init__(self, *args, **kwargs):
        super(EventsScreen, self).__init__(*args, **kwargs)
        self.last_uik = None
        self.last_region = None
        self.last_date = None

    def add_event(self, event):
        t = utc_to_local(strptime(event['timestamp'], '%Y-%m-%dT%H:%M:%S.%f'))

        if self.last_uik != event['uik'] or self.last_region != event['region_id']:
            self.ids['content'].add_widget(
                EventLogItem(halign='center', text='[color=#444]\n{}\nУИК {}[/color]'.format(
                    App.regions.get(event['region_id'], {}).get('name'), event['uik'])))
            self.ids['content'].add_widget(
                EventLogItem(text='[color=#444]{}[/color]'.format(t.strftime('%d.%m.%Y'))))
            self.last_uik = event['uik']
            self.last_region = event['region_id']
            self.last_date = t.date()

        elif self.last_date != t.date():
            self.ids['content'].add_widget(
                EventLogItem(text='\n[color=#444]{}[/color]'.format(t.strftime('%d.%m.%Y'))))
            self.last_date = t.date()

        if isinstance(event['value'], bool):
            event['value'] = 'Да' if event['value'] else 'Нет'

        #print(App.inputs[event.get('input_id').encode()])
        item = EventLogItem(
            input_json=App.inputs[event.get('input_id')],
            text='[color=#444]{time}[/color] {title}: {value}'.format(
                time=time.strftime('%H:%M'),
                **event))
        self.ids['content'].add_widget(item)
        item.bind(on_long_press=self.on_event_press)

    def on_event_press(self, item):
        self.manager.show_handbook(input_data=item.input_json)
