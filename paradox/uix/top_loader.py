# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import asyncio

from asyncio import sleep
from datetime import datetime, timedelta
from itertools import groupby

from app_state import state, on
from django.db.models import Q
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivy.core.window import Window
from loguru import logger


Builder.load_string('''
#:include constants.kv

<TopLoader>:
    canvas:
        Color:
            rgba: wheat4
        Rectangle:
            pos: self.pos
            size: self.width, dp(5)
    #y: self.parentd.height - dp(10)
    height: dp(5)
    
    LoaderDot:
        #pos: self.pos
        id: dot
        size: dp(5), dp(5)

<LoaderDot@Widget>:
    canvas:
        Color:
            #rgba: getattr(self, 'long_touch_color') if getattr(self, 'long_touch', False) else self.background_color
            rgba: white
            #rgba: 9,0,0,1
        Rectangle:
            pos: self.pos
            size: dp(10), dp(5)
    size: dp(10), dp(5)
    y: self.parent.y
    
    
    #pos: 200, 200

''')


class TopLoader(Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.anim = Animation(x=Window.width, duration=2) + Animation(x=0, duration=0)
        self.anim.repeat = True
        self.anim.start(self.ids.dot)
        
def show_loader():
    Window.loader = TopLoader(y=Window.height-dp(5))
    Window.add_widget(Window.loader)
    
def hide_loader():
    Window.loader.anim.stop(Window.loader)
    Window.remove_widget(Window.loader)
    del(Window.loader)

from inspect import iscoroutinefunction

def show(f):
    if iscoroutinefunction(f):
        async def wrapped(*a, **kw):
            show_loader()
            try:
                return await f(*a, **kw)
            finally:
                hide_loader()
    else:
        def wrapped(*a, **kw):
            show_loader()
            try:
                return f()
            finally:
                hide_loader()
        
    return wrapped
