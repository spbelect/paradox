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
from .complaint import Complaint

Builder.load_string('''
#:include constants.kv

#:import state app_state.state

#:import uix paradox.uix


###:import ImagePicker paradox.uix.imagepicker.ImagePicker

<TrueNoneFalse>:
    size_hint_y: None
    width: 0.9 * getattr(self.parent, 'width', 10)
    padding_y: 0

    Button:
        id: input_label
        padding_x: dp(6)
        split_str: ' '
        text_size: self.width, None
        height: self.texture_size[1] + dp(10)
        text: self.parent.json['label']
        color: black
        on_long_press: uix.screenmgr.show_handbook(root.json['label'], root.json['help_text'])

    BoxLayout:
        size_hint: None, None
        id: buttons
        size: dp(300), dp(50)
        pos_hint: {'center_x': .5}

        TNFButton:
            size_hint_x: .2
            text: 'Да'
            value: True
            #on_press: root.on_input(True)

        TNFButton:
            id: neizvestno
            size_hint_x: .6
            text: 'Неизвестно'
            value: None
            state: 'down'
            #on_press: root.on_input(None)

        TNFButton:
            size_hint_x: .2
            text: 'Нет'
            value: False
            
    Label:
        color: lightgray
        font_size: dp(16)
        id: send_status
        #background_color: lightgray
        size_hint_y: None
        height: dp(16)
        #text: '124'

    Complaint:
        id: complaint
        input: root
        
<TNFButton@ToggleButton>:
    height: self.parent.height - 10
    size_hint_y: None
    allow_no_selection: False
    group: self.parent.uid
    #on_press: self.parent.parent.on_click(self.value)
    on_press: self.parent.parent.on_input(self)
    background_color: lightgray


''')

#class TNFButton(ToggleButton):
    ## workaround for kivy BUG: https://github.com/kivy/kivy/issues/4379
    #value = ObjectProperty(allownone=True)


class TrueNoneFalse(Input, VBox):
    text = StringProperty('')
    input_id = StringProperty()

    def on_send_start(self, event):
        self.ids.send_status.text = 'отправляется'
    
    def on_send_success(self, event):
        self.ids.send_status.text = ''

    def on_send_error(self, event):
        self.ids.send_status.text = 'отправляется (error)'

    #def on_send_fatal_error(self, event, request, error_data):
        #self.ids.send_status.text = 'ошибка'
    
    def on_save_success(self, event):
        super().on_save_success(event)
        self.ids.send_status.text = 'отправляется'
        self.on_event(event)
        
    def on_input(self, button):
        super().on_input(button.value)
        
    def set_past_events(self, events):
        if events:
            #print('set past', events[-1].get_value())
            self.on_event(events[-1])
        else:
            self.set_state(None)
            
        super().set_past_events(events)

    def on_event(self, event):
        if event.revoked:
            self.set_state(None)
        else:
            self.set_state(event.get_value())
            
    def set_state(self, value):
        for button in self.ids.buttons.children:
            if button.value == value:
                button.state = 'down'
            else:
                button.state = 'normal'
                
