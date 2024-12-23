# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from kivy.lang import Builder
from kivy.properties import NumericProperty
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget

from paradox.uix.label import Label


Builder.load_string('''
#:import open_url paradox.utils.open_url

<ClickLabel>:
    #height: height1
    size_hint_y: None
    markup: True
    color: black
    text_size: self.width, None
    height: self.texture_size[1] + dp(10)
    halign: 'left'
    pos_hint: {'center_y':.5}

''')


class ClickLabel(Label):
    pass

