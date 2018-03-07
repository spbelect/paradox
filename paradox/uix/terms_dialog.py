# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.uix.modalview import ModalView
from kivy.lang import Builder

from ..scheduler import schedule

Builder.load_string('''

<TermsDialog>:
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
        BoxLayout:
            orientation: 'horizontal'
            height: height1
            size_hint_y: None
            Button:
                text: 'принять'
                on_release: root.accept()
                color: black
                background_color: lightgray
            Button:
                text: 'отклонить'
                on_release: root.dismiss()
                color: black
                background_color: lightgray

''')


text = '''
Некоторые вводимые вами данные могут попадать под закон о защите персональных
данных.
Мы не публикуем и не передаем ваши контактные данные третьим лицам без вашего согласия.
Но по закону нам требуется ваше разрешение на хранение, обработку, и передачу данных.

Чтобы отправлять данные в колл-центр мы проим вас принять пользовательское соглашение.

[b]ПОЛЬЗОВАТЕЛЬСКОЕ СОГЛАШЕНИЕ[/b]

Нажимая "Принять", вы как пользователь принимаете с условия данного соглашения.

Оператором вводимых пользователем данных является Общественная Организация «Наблюдатели Петербурга»
(«Наблюдатели Санкт­-Петербурга и Северо-­Западного региона»). Оператор организует передачу, хранение и
обработку всех вводимых пользователем данных, включая персональные данные. Эти данные могут быть
переданы для непосредственной обработки или хранения третьим лицам. Пользователь предоставляет оператору право
использовать полученные данные в сответствии с данным соглашением, законом "О Персональных Данных" и другими
действующими в Российской Федерации нормативными актами.

'''


class TermsDialog(ModalView):
    def __init__(self, *args, **kwargs):
        super(TermsDialog, self).__init__(*args, **kwargs)
        self.ids['txt'].text = text
        self.open()

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

    def accept(self):
        self.dismiss()
        schedule('core.terms_accepted')

    def _handle_keyboard(self, window, key, *largs):
        if key == 27 and self.auto_dismiss:
            self.dismiss()
            return False


def show_terms_dialog():
    TermsDialog()


# MOVE TO core
def terms_accepted():
    App.app_store[b'terms_accepted'] = True
    App.app_store.sync()
    if userprofile_errors():
        App.screens.push_screen('userprofile')
    else:
        timestamp = datetime.utcnow().isoformat()
        net.queue_send_userprofile(dict(App.app_store[b'profile'], timestamp=timestamp))

        if App.screens.get_screen('position').show_errors():
            App.screens.push_screen('position')
        else:
            net.queue_send_position(dict(App.app_store[b'position'], timestamp=timestamp))
