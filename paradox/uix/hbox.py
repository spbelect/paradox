# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from kivy.properties import ListProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.app import App
from kivy.lang import Builder


Builder.load_string('''
<HBox>:
    canvas.before:
        Color:
            rgba: self.background_color
        Rectangle:
            pos: self.pos
            size: self.size

    orientation: 'horizontal'
    size_hint: None, 1
    padding: dp(4), 0
    spacing: dp(8)
''')


class HBox(BoxLayout):
    background_color = ListProperty([1, 1, 1, 0])

    def do_layout(self, *args):
        #import ipdb; ipdb.sset_trace()
        w = 0
        for child in self.children:
            w += child.width + self.spacing

        # Remove one redundant spacing, add top and bottom padding.
        self.width = w - self.spacing + self.padding[0] + self.padding[2]
        #print '1  ', self.height

        result = super(HBox, self).do_layout(*args)
        return result

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
                    HBox:
                        padding: 5
                        spacing: 8

                        Button:
                            text: 'lol'
                            width: 100

                        Button:
                            text: 'lol2'
                            width: 100

                        Button:
                            text: 'lol3'
                            width: 100

                        Button:
                            text: 'lol4'
                            width: 100
                '''))

            return Demo()

    DemoApp().run()
