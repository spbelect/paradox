# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors.togglebutton import ToggleButtonBehavior

from kivy.uix.togglebutton import ToggleButton
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty, Property
from .vbox import VBox
from .base_input import Input
from label import Label


Builder.load_string('''
#:include constants.kv

#:import state app_state.state

<TrueNoneFalse>:
    size_hint_y: None
    width: 0.9 * getattr(self.parent, 'width', 10)

    Button:
        id: input_label
        padding_x: dp(6)
        split_str: ' '
        text_size: self.width, None
        height: self.texture_size[1] + dp(10)
        text: self.parent.json['label']
        color: black

    BoxLayout:
        size_hint: None, None
        id: buttons
        size: dp(300), dp(50)
        pos_hint: {'center_x': .5}

        TNFButton:
            size_hint_x: .2
            text: 'Да'
            value: True
            on_press: root.on_input(True)

        TNFButton:
            size_hint_x: .6
            text: 'Неизвестно'
            value: None
            state: 'down'
            on_press: root.on_input(None)

        TNFButton:
            size_hint_x: .2
            text: 'Нет'
            value: False
            on_press: root.on_input(False)
            
    Label:
        color: lightgray
        font_size: dp(16)
        id: send_status


<TNFButton@ToggleButton>:
    height: self.parent.height - 10
    size_hint_y: None
    allow_no_selection: False
    group: self.parent.uid
    #on_press: self.parent.parent.on_click(self.value)
    background_color: lightgray

''')


#class TNFButton(ToggleButton):
    ## workaround for kivy BUG: https://github.com/kivy/kivy/issues/4379
    #value = ObjectProperty(allownone=True)


class TrueNoneFalse(Input, VBox):
    text = StringProperty('')
    input_id = StringProperty()


    #def on_send_start(self, event):
        #self.ids['send_status'].text = 'отправляется'
    
    def on_send_success(self, event):
        self.ids['send_status'].text = ''

    def on_send_error(self, event):
        self.ids['send_status'].text = 'отправляется (error)'

    #def on_send_fatal_error(self, event, request, error_data):
        #self.ids['send_status'].text = 'ошибка'
    
    def on_input(self, value):
        self.ids['send_status'].text = 'отправляется'
        super().on_input(value)
        
    def set_past_events(self, events):
        if events:
            print('set past', events[-1].get_value())
            for button in self.ids['buttons'].children:
                if button.value == events[-1].get_value():
                    button.state = 'down'
                else:
                    button.state = 'normal'
        super().set_past_events(events)
