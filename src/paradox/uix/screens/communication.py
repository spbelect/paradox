# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.behaviors.button import ButtonBehavior


from paradox.uix.label import Label
from ..vbox import VBox


Builder.load_string('''
#:include constants.kv
#:import open_url paradox.utils.open_url
#:import call plyer.call

<CommunicationScreen>:
    ScrollView:
        VBox:
            padding: dp(8)


            Label:
                padding_x: dp(4)
                split_str: ' '
                text: 'Связь'
                text_size: self.width, None
                height: self.texture_size[1] + 10
                color: white
                background_color: teal

            Label:
                text: 'Пожалуйста установите приложение Telegram чтобы получать уведомления'
                text_size: self.width, None
                split_str: ' '
                color: lightgray
                font_size: sp(16)
                height: self.texture_size[1]


            BoxLayout:
                height: height1 * 2
                size_hint_y: None

                Image:
                    source: 'img/Telegram_alternative_logo.png'
                    width: height1 + dp(20)
                    size_hint_x: None

                Label:
                    id: tg_channel
                    text: 'Нет МО'
                    height: height1
                    size_hint_y: None
                    on_ref_press: open_url(args[1])
                    markup: True
                    color: black
                    text_size: self.width, None
                    halign: 'left'
                    pos_hint: {'center_y':.5}

            BoxLayout:
                height: height1 * 2
                size_hint_y: None

                Image:
                    source: 'img/Phone.png'
                    width: height1 + dp(20)
                    size_hint_x: None

                Label:
                    id: sos_phone
                    text: 'Нет МО'
                    height: height1
                    size_hint_y: None
                    on_ref_press: call.makecall(args[1])
                    markup: True
                    color: black
                    text_size: self.width, None
                    halign: 'left'
                    pos_hint: {'center_y':.5}

            BoxLayout:
                height: height1 * 2
                size_hint_y: None

                Image:
                    source: 'img/Telegram_alternative_logo.png'
                    width: height1 + dp(20)
                    size_hint_x: None

                Label:
                    text: 'Чат СПб и Лен.Обл.\\n[color=#4AABFF][ref=https://telegram.me/mobile_spb_lo]mobile_spb_lo[/ref][/color]'
                    height: height1
                    size_hint_y: None
                    on_ref_press: open_url(args[1])
                    markup: True
                    color: black
                    text_size: self.width, None
                    halign: 'left'
                    pos_hint: {'center_y':.5}


''')


class FormListItem(ButtonBehavior, Label):
    json = ObjectProperty()


class CommunicationScreen(Screen):
    def build(self, uik, region_sos_phone, region_tgchannel, mo_list):
        if region_tgchannel:
            self.ids['tg_channel'].text = 'Уведомления\n[color=#4AABFF][ref={tg}]{tg}[/ref][/color]'.format(tg=region_tgchannel)
        else:
            self.ids['tg_channel'].text = 'Уведомления: нет'
        if region_sos_phone:
            self.ids['sos_phone'].text = 'Колл-центр\n[color=#4AABFF][ref={sos}]{sos}[/ref][/color]'.format(sos=region_sos_phone)
        else:
            self.ids['sos_phone'].text = 'Колл-центр: нет'

        for mo in mo_list:
            if int(uik) in mo['uiks']:
                if mo.get('telegram_channel'):
                    self.ids['tg_channel'].text = 'Уведомления\n[color=#4AABFF][ref={telegram_channel}]{name}[/ref][/color]'.format(**mo)

                #sos_phone = mo.get('sos_phone')
                if mo.get('sos_phone'):
                    self.ids['sos_phone'].text = 'Колл-центр\n[color=#4AABFF][ref={sos_phone}]{sos_phone}[/ref][/color]'.format(**mo)

                break


screen = CommunicationScreen(name='communication')
