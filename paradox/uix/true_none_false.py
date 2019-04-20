# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors.togglebutton import ToggleButtonBehavior

from kivy.uix.togglebutton import ToggleButton
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty, Property
from .vbox import VBox
from .label import Label
from .base_input import Input
from util import nurse


Builder.load_string('''
#:include constants.kv

#:import state app_state.state

<TrueNoneFalse>:
    size_hint_y: None
    width: 0.9 * self.parent.width

    Label:
        padding_x: dp(6)
        font_size: sp(22)
        split_str: ' '
        text_size: self.width, None
        height: self.texture_size[1] + 10
        text: self.parent.json['label']
        #width: 0.9 * self.parent..width

    BoxLayout:
        size_hint: None, None
        id: buttons
        size: dp(300), dp(50)
        pos_hint: {'center_x': .5}

        TNFButton:
            size_hint_x: .2
            text: 'Да'
            #value: True
            on_press: root.on_click(True)

        TNFButton:
            size_hint_x: .6
            text: 'Неизвестно'
            #value: None
            state: 'down'
            on_press: root.on_click(None)

        TNFButton:
            size_hint_x: .2
            text: 'Нет'
            #value: False
            on_press: root.on_click(False)
            
    Label:
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
    value = ObjectProperty(None, allownone=True)


    #def on_send_start(self, event):
        #self.ids['send_status'].text = 'отправляется'
    
    def on_send_success(self, event):
        self.ids['send_status'].text = ''

    def on_send_error(self, event, request, error_data):
        self.ids['send_status'].text = 'ошибка'

    #def on_send_fatal_error(self, event, request, error_data):
        #self.ids['send_status'].text = 'ошибка'
    
    @nurse
    async def on_click(self, value):
        self.ids['send_status'].text = 'отправляется'
        forms.on_input(self.iid, value)
        #if not App.profile_ok():
            #App.show_fill_profile()
            #return
        #emit(f'uix/input/{self.iid}/changed')
        #event = InputEvent.save()
        
        
