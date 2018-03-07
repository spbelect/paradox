# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from kivy.lang import Builder
from kivy.properties import NumericProperty
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget

from ..label import Label


Builder.load_string('''
#:import Clock kivy.clock.Clock
#:import open_url paradox.utils.open_url
#:include constants.kv

<AboutScreen>:
    ScrollView:
        VBox:
            padding: '10dp'

            Label:
                text: 'Paradox v%s' % app.version
                text_size: self.width, None
                halign: 'left'

            Widget:  #spacer

            Label:
                text: 'Техподдержка:'
                text_size: self.width, None
                halign: 'left'

            BoxLayout:
                height: height1 * 2
                size_hint_y: None

                Image:
                    source: 'Telegram_alternative_logo.png'
                    width: height1 + dp(20)
                    size_hint_x: None


                ClickLabel:
                    text: '[color=#4AABFF][ref=https://telegram.me/spbelect_mobile]@spbelect_mobile[/ref][/color]'

            BoxLayout:
                height: height1 * 2
                size_hint_y: None

                Image:
                    source: 'fb_icon_325x325.png'
                    width: height1 + dp(20)
                    size_hint_x: None

                ClickLabel:
                    text: '[color=#4AABFF][ref=https://www.facebook.com/groups/npmobile/]npmobile[/ref][/color]'

            BoxLayout:
                height: height1 * 2
                size_hint_y: None

                Image:
                    source: 'vkontakte-256.png'
                    width: height1 + dp(20)
                    size_hint_x: None

                ClickLabel:
                    text: '[color=#4AABFF][ref=https://vk.com/spbelect_mobile]spbelect_mobile[/ref][/color]'


<ClickLabel@Label>:
    height: height1
    size_hint_y: None
    on_ref_press: open_url(args[1])
    markup: True
    color: black
    text_size: self.width, None
    halign: 'left'
    pos_hint: {'center_y':.5}

#<Icon>:
    #scale: 1

    #Widget:
        #size: root.scale * self.parent.height, root.scale * self.parent.height
        #center: self.parent.center
        #canvas:
            #Rectangle:
                #source: root.filename
                #size: self.size
                #pos: self.pos
''')


#class Icon(Label):
    #filename = StringProperty()
    #scale = NumericProperty()


class AboutScreen(Screen):
    pass