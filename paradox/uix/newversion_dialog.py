# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.uix.modalview import ModalView
from kivy.lang import Builder

from ..scheduler import schedule

Builder.load_string('''

<NewVersionDialog>:
    size_hint: 0.9, 0.9
    #size: 0.9, 0.9 * app.root.height
    background: ''
    #background_color: transparent
    #_anim_duration: 3

    BoxLayout:
        orientation: 'vertical'
        ScrollView:
            Label:
                id: txt
                size_hint: 1, None
                background_color: white
                text_size: self.width, None
                height: self.texture_size[1] + 10
                color: black
                split_str: ' '
                markup: True
                halign: 'left'
                #font_name: 'DejaVuSansMono.ttf'
                font_size: font1 - sp(3)

        BoxLayout:
            orientation: 'horizontal'
            height: height1
            size_hint_y: None
            #Button:
                #text: 'обновить'
                #on_release: root.accept()
                #color: black
            Button:
                text: 'закрыть'
                on_release: root.dismiss()
                color: black
                background_color: lightgray

''')


text = '''
[b]Доступна новая версия[/b]

Рекомендуется обновить приложение. Старые версии могут работать некорректно

%s
'''


class NewVersionDialog(ModalView):
    def __init__(self, changelog, *args, **kwargs):
        super(NewVersionDialog, self).__init__(*args, **kwargs)
        self.ids['txt'].text = text % changelog
        self.open()
        #print 2

    #def do_layout(self, *args):
        #height = sum(x.height for x in self.children)

        ## Add top and bottom padding.
        #self.height = height + self.padding[1] + self.padding[3]

        #result = super(FloatMessage, self).do_layout(*args)
        #return result

    #def on_touch_down(self, *args):
        #self.dismiss()
        #super(FloatMessage, self).on_touch_down(*args)
        #return True

    def _handle_keyboard(self, window, key, *largs):
        if key == 27 and self.auto_dismiss:
            self.dismiss()
            return False


def show_new_version_dialog(changelog):
    #print 1
    NewVersionDialog(changelog)
