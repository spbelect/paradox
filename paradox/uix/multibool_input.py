# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, StringProperty

from ..utils import strptime
from .vbox import VBox
from .base_input import Input

from button import Button

Builder.load_string('''
#:include constants.kv
#:import state app_state.state

<MoreButton@Button>:
    text: '+ Еще'
    color: teal
    size_hint: None, None
    pos_hint: {'center_x': .5}
    #halign: 'left'
    #text_size: self.size
    #size_hint: None, None
    #width: dp(150)
    background_color: white
    color: teal

<ValueLogItem@BoxLayout>:
    size_hint: 1, None
    height: height1

    Label:
        size_hint: 1, None
        text_size: self.size
        color: lightgray
        pos_hint: {'center_x': .5}
        halign: 'left'
        text: root.text
        height: height1

    Label:
        id: loader
        size_hint: 1, None
        #text_size: self.size
        color: lightgray
        pos_hint: {'center_x': .5}
        halign: 'left'
        text: 'отправляется'
        height: height1


<MultiBoolInput>:
    padding: 0
    spacing: 0
    #size_hint_x: None
    width: 0.9 * (self.parent.width if self.parent else 10)

    Button:
        id: input_label
        padding_x: dp(6)
        split_str: ' '
        text_size: self.width, None
        height: self.texture_size[1] + dp(10)
        text: self.parent.json['label']
        color: black
        #on_press: root.show

    TrueFalseButtons:
        id: true_false_buttons


<TrueFalseButtons@BoxLayout>:
    padding: 0
    spacing: dp(100)
    size_hint: None, None
    size: dp(300), height1
    pos_hint: {'center_x': .5}

    VButton:
        text: 'Да'
        value: True
        width: dp(100)

    VButton:
        text: 'Нет'
        value: False
        width: dp(100)


<VButton@Button>:
    # Button with value
    size_hint: None, None
    height: self.parent.height
    width: dp(60)
    #on_release: schedule('core.new_input_event', self.parent.parent, self.value)
    on_release: print(1)
    background_color: lightgray

''')


class TrueFalseButtons(BoxLayout):
    pass


class ValueLogItem(BoxLayout):
    text = StringProperty(None, allownone=True)
    input_id = StringProperty(None, allownone=True)
    timestamp = StringProperty(None, allownone=True)

    def __init__(self, *args, **kwargs):
        no_loader = kwargs.pop('no_loader', False)
        super(ValueLogItem, self).__init__(*args, **kwargs)
        if no_loader:
            self.remove_widget(self.ids.get('loader'))


class MoreButton(Button):
    pass


class MultiBoolInput(Input, VBox):
    def __init__(self, *args, **kwargs):
        
        #print(11, args, kwargs)
        #VBox.__init__(self)
        #print(22, args, kwargs)
        super().__init__(*args, **kwargs)
        #print(22, args, kwargs)
        self.more_button = None

    def add_past_event(self, event):
        try:
            self.remove_widget(self.ids['true_false_buttons'])
        except:
            pass
        try:
            self.remove_widget(self.more_button)
        except:
            pass
        ts = strptime(event['timestamp'], '%Y-%m-%dT%H:%M:%S.%f')
        text = '%s %s' % (utc_to_local(ts).strftime('%H:%M'), 'Да' if event['value'] else 'Нет')
        self.add_widget(ValueLogItem(text=text, timestamp=ts.isoformat(), input_id=self.input_id, no_loader=True))
        self.more_button = MoreButton()
        self.more_button.bind(on_press=self.on_more)
        self.add_widget(self.more_button)

    def on_save_success(self, eid, timestamp, value):
        #self.values.append((timestamp, value))
        text = '%s %s' % (utc_to_local(timestamp).strftime('%H:%M'), 'Да' if value else 'Нет')
        self.add_widget(ValueLogItem(text=text, timestamp=timestamp.isoformat(), input_id=self.input_id))
        self.more_button = MoreButton()
        self.more_button.bind(on_press=self.on_more)
        self.add_widget(self.more_button)
        self.remove_widget(self.ids['true_false_buttons'])

    def _get_loader(self, event):
        logitem = ValueLogItem.objects.get(input_id=self.input_id, timestamp=event['timestamp'])
        return logitem.ids.get('loader') if logitem else None

    def on_send_success(self, event):
        loader = self._get_loader(event)
        try:
            if loader:
                loader.parent.remove_widget(loader)
        except:
            pass

    def on_send_error(self, event, request, error_data):
        try:
            loader = self._get_loader(event)
            if loader:
                loader.text = 'отправляется (err)'   # .encode('utf8')
        except:
            pass

    def on_send_fatal_error(self, event, request, error_data):
        try:
            loader = self._get_loader(event)
            if loader:
                loader.text = 'fatal err'
        except:
            pass

    def on_more(self, *args):
        self.remove_widget(self.more_button)
        true_false_buttons = TrueFalseButtons()
        self.add_widget(true_false_buttons)
        self.ids['true_false_buttons'] = true_false_buttons
