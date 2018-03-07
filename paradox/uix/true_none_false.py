# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors.togglebutton import ToggleButtonBehavior

from kivy.uix.togglebutton import ToggleButton
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty, Property
from vbox import VBox
from .label import Label

Builder.load_string('''
#:include constants.kv

<TrueNoneFalse>:
    size_hint_y: None
    width: 0.9 * app.root.width

    Label:
        padding_x: dp(6)
        font_size: sp(22)
        split_str: ' '
        text_size: self.width, None
        height: self.texture_size[1] + 10
        text: self.parent.text
        width: 0.9 * app.root.width

    BoxLayout:
        size_hint: None, None
        id: buttons
        size: dp(300), dp(50)
        pos_hint: {'center_x': .5}

        TNFButton:
            size_hint_x: .2
            text: 'Да'
            value: True

        TNFButton:
            size_hint_x: .6
            text: 'Не известно'
            value: None
            state: 'down'

        TNFButton:
            size_hint_x: .2
            text: 'Нет'
            value: False


<TNFButton>:
    height: self.parent.height - 10
    size_hint_y: None
    allow_no_selection: False
    group: self.parent.uid
    on_press: self.parent.parent.value = self.value
    background_color: lightgray

''')


class TNFButton(ToggleButton):
    # workaround for kivy BUG: https://github.com/kivy/kivy/issues/4379
    value = ObjectProperty(allownone=True)


class TrueNoneFalse(VBox):
    text = StringProperty('')
    input_id = StringProperty()
    value = ObjectProperty(None, allownone=True)
