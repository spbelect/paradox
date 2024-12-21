# -*- coding: utf-8 -*-

import kivy.uix.label
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.properties import ListProperty


from loguru import logger

# NOTE: opened feature request "Move background_color property from Button up to Label"
# https://github.com/kivy/kivy/issues/6265


class Label(kivy.uix.label.Label):
    background_color = ListProperty([1, 1, 1, 0])

Factory.unregister('Label')
Factory.register('Label', cls=Label)

logger.info('Registered custom Label widget')


Builder.load_string("""
<Label>:
    canvas.before:
        Color:
            rgba: self.background_color if hasattr(self, "background_color") else (1,1,1,1)
        Rectangle:
            pos: self.pos
            size: self.size
""")
