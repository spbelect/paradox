# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.uix.modalview import ModalView
from kivy.lang import Builder


Builder.load_string('''

<FloatMessage>:
    size_hint: None, None
    width: dp(300)
    background: ''
    #background_color: transparent
    #_anim_duration: 3

    Label:
        id: label
        size_hint: 1, None
        background_color: wheat4
        text_size: self.width, None
        height: self.texture_size[1] + 10
        color: black
        text: root.text
        split_str: ' '

''')


class FloatMessage(ModalView):
    text = StringProperty()

    def __init__(self, *args, **kwargs):
        super(FloatMessage, self).__init__(*args, **kwargs)
        self.open()
        Clock.schedule_once(self.dismiss, 3.5)
        anim = Animation(background_color=self.ids['label'].background_color[:-1] + [0], color=(1, 1, 1, 0), duration=3.5, t='in_cubic')
        anim.start(self.ids['label'])
        anim = Animation(background_color=(0, 0, 0, 0), duration=3.5, t='in_expo')
        anim.start(self)

    def do_layout(self, *args):
        height = sum(x.height for x in self.children)

        # Add top and bottom padding.
        self.height = height + self.padding[1] + self.padding[3]

        result = super(FloatMessage, self).do_layout(*args)
        return result

    def on_touch_down(self, *args):
        self.dismiss()
        super(FloatMessage, self).on_touch_down(*args)
        return True

    def _handle_keyboard(self, window, key, *largs):
        if key == 27 and self.auto_dismiss:
            self.dismiss()
            return False


def show_float_message(text):
    FloatMessage(text=text)
