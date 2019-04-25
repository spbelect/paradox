# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import kivy.uix.label
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.properties import ListProperty


# NOTE: opened feature request "Move background_color property from Button up to Label"
# https://github.com/kivy/kivy/issues/6265

Builder.load_string("""
<Label>:
    canvas.before:
        Color:
            rgba: self.background_color if hasattr(self, 'background_color') else (0, 0, 0, 0)
        Rectangle:
            pos: self.pos
            size: self.size
""")


class Label(kivy.uix.label.Label):
    background_color = ListProperty([1, 1, 1, 0])


Factory.unregister('Label')
Factory.register('Label', cls=Label)
