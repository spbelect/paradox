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
    size_hint: 1, None
    padding: dp(4)
    spacing: dp(8)
''')


class VBox(BoxLayout):
    background_color = ListProperty([1, 1, 1, 0])
    visible = BooleanProperty(default=True)

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.funbind('size', self._trigger_layout)
        self.fbind('width', self._trigger_layout)
        
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
            self.height = 0
            
        result = super().do_layout(*args)
        #print(self.height)
        return result


    def on_visible(self, *a):
        if self.visible:
            self.size_hint = 1, 1
            self.size = 100,100
            
            self.opacity = 1
            self.disabled = False
        else:
            self.size_hint = None, None
            self.size = 0,0
            self.opacity = 0
            self.disabled = True
        self.do_layout()
        
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
