# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from app_state import state 
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.behaviors.button import ButtonBehavior



from ...objects_manager import objects_manager
from ..label import Label
from ..vbox import VBox


Builder.load_string('''
#:include constants.kv

<SmartCamera>:
    canvas.before:
        PushMatrix
        Rotate:
            angle: root.rotate
            origin: self.center
    canvas.after:
        PopMatrix

        Color:
            rgba: 1,0,0,0.5
        Rectangle:
            pos: self.pos
            size: self.size

<FormListScreen>:

    BoxLayout:
        orientation: 'vertical'
        ScrollView:
            VBox:
                #Camera:
                #SmartCamera:
                    #id: camera
                    #resolution: (640, 480)
                    ##resolution: (480, 640)
                    #play: True
                    #size: '100dp', '200dp'


                VBox:
                    padding: 0, dp(10)

                    Label:
                        height: dp(20)
                        text_size: self.size
                        text: 'Анкеты'
                        font_size: sp(18)
                        color: lightgray

                    VBox:
                        id: general_forms
                        padding: 0

                    Widget:  # spacer
                        height: dp(60)
                        size_hint: 1, None

                VBox:
                    padding: 0, dp(10)

                    background_color: lightgray

                    Label:
                        height: dp(20)
                        text_size: self.size
                        text: 'Итоговые протоколы'
                        font_size: sp(18)
                        color: white
                        background_color: lightgray

                    VBox:
                        id: federal_forms
                        background_color: lightgray
                    VBox:
                        id: regional_forms
                        background_color: lightgray
                    VBox:
                        id: local_forms
                        background_color: lightgray

        #Widget:  # spacer

        BoxLayout:
            height: height1
            size_hint: 1, None
            #spacing: dp(2)
            #padding: dp(2)

            Button:
                background_normal: 'HAMBURGER_MENU-1282.png'
                size: height1, height1
                #size_hint_x: None
                size_hint: None, None
                pos_hint: {'center_y': .5}
                on_release: app.root.toggle_state()
                #background_color: lightgray

            Button:
                id: menu_button
                text: 'Меню'
                on_release: app.root.toggle_state()
                halign: 'left'
                text_size: self.size
                size_hint: None, None
                width: dp(150)
                height: height1
                background_color: white
                color: lightgray
                pos_hint: {'center_y':.5}


            Widget:  # horizontal spacer

<FormListItem>:
    halign: 'left'
    split_str: ' '
    text_size: self.width, None
    height: self.texture_size[1]
    width: 300
    text: self.json['name']


''')

#from kivy.uix.camera import Camera
#from kivy.graphics.texture import Texture
#import cv2


#class SmartCamera(Camera):
    #rotate = NumericProperty(0)

    #def __init__(self, *args, **kwargs):
        #super(SmartCamera, self).__init__(*args, **kwargs)
        #if platform != 'android':
            ##self.rotate = 90
            ##w, h = self.resolution
            ##if w > h:
                ##self.resolution = h, w
            ##self.rotate = 0
            #print self.size
            ##self.width, self.height


    ##def _camera_loaded(self, *largs):
        ##if platform != 'android':
            ##self.texture = Texture.create(size=self.resolution, colorfmt='rgb')
            ##self.texture_size = list(self.texture.size)
        ##else:
            ##super(CvCamera, self)._camera_loaded()

    ##def on_tex(self, *l):
        ###import ipdb; ipdb.set_trace()
        ##if platform != 'android':
            ##buf = self._camera.grab_frame()
            ###if not buf:
                ###return super(CvCamera, self).on_tex(*l)
            ##frame = self._camera.decode_frame(buf)
            ###buf = self.process_frame(frame)
            ##self.texture.blit_buffer(buf, colorfmt='rgb', bufferfmt=b'ubyte')
        ##super(CvCamera, self).on_tex(*l)

    #def process_frame(self, frame):
        ## Process frame with opencv
        #return cv2.flip(frame, 1).tostring()


class FormListItem(ButtonBehavior, Label):
    json = ObjectProperty()
    
    #def on_release(self, *a):
        #self.

@objects_manager
class FormListScreen(Screen):
    def build_general(self):
        for item in self.ids['general_forms'].children[:]:
            self.ids['general_forms'].remove_widget(item)
        for form in state.forms.general[state.country]:
            item = FormListItem(json=form)
            item.bind(on_release=self.on_release)
            self.ids['general_forms'].add_widget(item)

    def on_release(self, item):
        self.manager.show_form(item.json)

    @staticmethod
    def show_loader(f):
        async def wrapped(*a, **kw):
            self = App.screens.get_screen('formlist')
            self.ids['forms_loader'].show()
            try:
                return await f(*a, **kw)
            finally:
                self.ids['forms_loader'].hide()
        return wrapped
