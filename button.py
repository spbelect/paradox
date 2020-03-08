# -*- coding: utf-8 -*-
# TODO: move this into standalone package

#from functools import partial
import kivy.uix.button
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.properties import BooleanProperty, ListProperty


#Builder.load_string("""
#<Button>:
    #canvas.before:
        #Color:
            #rgba: getattr(self, 'long_touch_color') if getattr(self, 'long_touch', False) else self.background_color
            ##rgba: (9,0,0, 1)
        #Rectangle:
            #pos: self.pos
            #size: self.size
#""")


class Button(kivy.uix.button.Button):
    """
    Button with on_long_press event.
    """

    def __init__(self, *args, **kwargs):
        super(Button, self).__init__(*args, **kwargs)
        self.register_event_type('on_long_press')
        self.bind(
            on_touch_down=self.ontouchdown,
            on_touch_up=self.ontouchup,
            on_touch_move=self.ontouchmove
        )

    def ontouchdown(self, s, touch):
        if not self.collide_point(touch.x, touch.y):
            return False
        Clock.schedule_once(self.do_long_touch, 0.1),

    def ontouchup(self, *a):
        Clock.unschedule(self.do_long_touch)

    def ontouchmove(self, s, touch):
        if abs(touch.ox - touch.x) > 20 and abs(touch.oy - touch.y) > 20:
            Clock.unschedule(self.do_long_touch)

    def do_long_touch(self, *a):
        self.dispatch('on_long_press')

    def on_long_press(self, *args):
        pass


Factory.unregister('Button')
Factory.register('Button', cls=Button)
