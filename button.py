# -*- coding: utf-8 -*-
# TODO: move this into standalone package

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
    Button with long_press event.
    """
    long_touch = BooleanProperty(False)
    long_touch_color = ListProperty([0.137, 0.451, 0.565, 0.5])  # teal

    def get_bg_color(self):
        self.long_touch_color if self.long_touch else self.background_color


    def __init__(self, *args, **kwargs):
        super(Button, self).__init__(*args, **kwargs)
        self.register_event_type('on_long_press')
        self.bind(
            on_touch_down=self.ontouchdown,
            on_touch_up=self.on_stop_longpress,)

    def ontouchdown(self, s, touch):
        if not self.collide_point(touch.x, touch.y):
            return False
        Clock.schedule_once(self.set_long_touch, 0.6),

    def set_long_touch(self, *a):
        self.long_touch = True

    #def on_touch_down(self, e):
        #print(e.grab_state, e.grab_list, e.is_mouse_scrolling, e.ud, '\n')
        
    def on_touch_cancel(self, *a):
        Clock.unschedule(self.set_long_touch)
        self.long_touch = False

    def on_stop_longpress(self, s, touch):
        Clock.unschedule(self.set_long_touch)
        if self.long_touch:
            if self.collide_point(touch.x, touch.y):
                self.dispatch('on_long_press')
            self.long_touch = False

    def on_long_press(self, *args):
        pass


Factory.unregister('Button')
Factory.register('Button', cls=Button)
