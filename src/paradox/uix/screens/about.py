# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from kivy.lang import Builder
from kivy.properties import NumericProperty
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget

from paradox.uix.label import Label
from ..click_label import ClickLabel


Builder.load_string('''
#:import Clock kivy.clock.Clock
#:import open_url paradox.utils.open_url
#:include constants.kv

#:import state app_state.state


<AboutScreen>:
    ScrollView:
        VBox:
            padding: '10dp'

            Label:
                text: 'Paradox v%s' % state._config.version
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
                    source: 'img/Telegram_alternative_logo.png'
                    width: height1 + dp(20)
                    size_hint_x: None


                ClickLabel:
                    text: '[color=#4AABFF][ref=https://telegram.me/spbelect_mobile]@spbelect_mobile[/ref][/color]'
                    on_ref_press: open_url(args[1])

            BoxLayout:
                height: height1 * 2
                size_hint_y: None

                Image:
                    source: 'img/fb_icon_325x325.png'
                    width: height1 + dp(20)
                    size_hint_x: None

                ClickLabel:
                    text: '[color=#4AABFF][ref=https://www.facebook.com/groups/npmobile/]npmobile[/ref][/color]'
                    on_ref_press: open_url(args[1])

            BoxLayout:
                height: height1 * 2
                size_hint_y: None

                Image:
                    source: 'img/vkontakte-256.png'
                    width: height1 + dp(20)
                    size_hint_x: None

                ClickLabel:
                    text: '[color=#4AABFF][ref=https://vk.com/spbelect_mobile]spbelect_mobile[/ref][/color]'
                    on_ref_press: open_url(args[1])


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
