# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from kivy.properties import ObjectProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.app import App
from kivy.lang import Builder


class ValuedButton(Button):
    # workaround for kivy BUG: https://github.com/kivy/kivy/issues/4379
    value = ObjectProperty(allownone=True)
