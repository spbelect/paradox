# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from kivy.properties import ListProperty
from kivy.properties import BooleanProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.app import App
from kivy.lang import Builder


Builder.load_string('''
<VBox>:
    visible: True
    #canvas.before:
        #Color:
            #rgba: self.background_color
        #Rectangle:
            #pos: self.pos
            #size: self.size

    orientation: 'vertical'
    size_hint_x: 1 if self.visible else None
    size_hint_y: None
    width: 1 if self.visible else 0
    opacity: 1 if self.visible else 0
    padding: dp(4)
    spacing: 0
    disabled: not self.visible
''')


class VBox(BoxLayout):
    background_color = ListProperty([1, 1, 1, 0])
    visible = BooleanProperty(default=True)

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        #self.funbind('size', self._trigger_layout)
        #self.funbind('size_hint', self._trigger_layout)
        #self.fbind('width', self._trigger_layout)
        #self.fbind('size_hint_x', self._trigger_layout)
        #self.fbind('width', self.set_wi)
        
    #def set_wi(self, *a):
        #print('set_wi', self, self.width)
        
    def do_layout(self, *args):
        #import ipdb; ipdb.sset_trace()
        #result = super(VBox, self).do_layout(*args)
        
        if self.visible:
            height = 0
            for child in self.children:
                height += child.height + self.spacing

            # Remove one redundant spacing, add top and bottom padding.
            self.height = height - self.spacing + self.padding[1] + self.padding[3]
            #print('1  ', self, self.height)
        else:
            #print('0  ', self, self.height)
            self.size = (0, 0)
            return
            
        #return super().do_layout(*args)
        if not self.children:
            l, t, r, b = self.padding
            self.minimum_size = l + r, t + b
            return

        for i, x, y, w, h in self._iterate_layout(
                [(c.size, c.size_hint, c.pos_hint, c.size_hint_min,
                  c.size_hint_max) for c in self.children]):
            c = self.children[i]
            c.pos = x, y
            if c.size_hint_x is not None:
                c.width = w

    def on_touch_down(self, *a):
        if not self.visible:
            return False
        return super().on_touch_down(*a)

    #def on_visible(self, *a):
        ##print(self, self.visible)
        #if self.visible:
            #self.size_hint = 1, 1
            #self.size = 100,100
            
            #self.opacity = 1
            #self.disabled = False
        #else:
            #self.size_hint = None, None
            #self.size = 0,0
            #self.opacity = 1
            #self.disabled = True
        #self.do_layout()
        
        
    #def add_widget(self, widget, index=0, canvas=None):
        #result = super().add_widget(widget, index, canvas)
        #widget.funbind('size', self._trigger_layout)
        #widget.funbind('size_hint', self._trigger_layout)
        #widget.funbind('size_hint_max', self._trigger_layout)
        #widget.funbind('size_hint_min', self._trigger_layout)
        ##fbind = widget.fbind
        #widget.fbind('height', self._trigger_layout)
        ##widget.fbind('size_hint_y', self._trigger_layout)
        #return result
    
    #def add_widget(self, *args):
        #super(VBox, self).add_widget(*args)
        #self.do_layout()

if __name__ == '__main__':
    class Demo(ScrollView):
        pass

    class DemoApp(App):
        def build(self):
            from textwrap import dedent
            from kivy.core.window import Window
            Window.size = (200, 400)

            Builder.load_string(dedent('''
                <Demo>:
                    VBox:
                        padding: 5
                        spacing: 8

                        Button:
                            text: 'lol'
                            height: 100

                        Button:
                            text: 'lol2'
                            height: 100

                        Button:
                            text: 'lol3'
                            height: 100

                        Button:
                            text: 'lol4'
                            height: 100
                '''))

            return Demo()

    DemoApp().run()
