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
<VBox>:
    canvas.before:
        Color:
            rgba: self.background_color
        Rectangle:
            pos: self.pos
            size: self.size

    orientation: 'vertical'
    size_hint: 1, None
    padding: dp(4)
    spacing: dp(8)
''')


class VBox(BoxLayout):
    background_color = ListProperty([1, 1, 1, 0])

    def do_layout(self, *args):
        #import ipdb; ipdb.sset_trace()
        height = 0
        for child in self.children:
            height += child.height + self.spacing

        # Remove one redundant spacing, add top and bottom padding.
        self.height = height - self.spacing + self.padding[1] + self.padding[3]
        #print '1  ', self.height

        result = super(VBox, self).do_layout(*args)
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
