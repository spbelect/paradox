from uuid import uuid4

from kivy.lang import Builder

from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.properties import ObjectProperty
from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup
from plyer import filechooser

from button import Button
from paradox import utils
from paradox.uix.vbox import VBox
from paradox.uix.hbox import HBox

Builder.load_string('''
#:include constants.kv

#:import state app_state.state

<ImagePickerModal>:
    background: ''
    #background_color: transparent

    size_hint: 0.9, None
    hparent: getattr(self.parent, 'height', 10) * 0.9
    height: 
        content.height if content.height < self.hparent else self.hparent
    #height:
        
    _anim_duration: 0
    _anim_alpha: 1
    #_window: app.root_window

    BoxLayout:
        #padding: '12dp'
        ##cols: 1
        ##size_hint: None, None
        ##pos: root.pos
        ##size: root.size

        ScrollView:
            id: scrollview
            scroll_distance: dp(30)

            VBox:
                id: content
                background_color: white
                padding: 0

                Label:
                    text: root.choices.modal_header
                    color: white
                    background_color: lightgray
                VBox:
                    id: list


#<Choice>:
    #color: black
    #background_color: white
    ##width: self.parent.width if self.parent else '300dp'
    #width: 0.9 * (self.parent.width if self.parent else 29)
    ##width: 40
    #size_hint: None, None
    ##size: '300dp', height1 * 2
    ##height: height1 * 1.5

    #split_str: ' '
    ##text_size: 300, 100
    #text_size: self.width, None
    #height: self.texture_size[1] + dp(10)



<ImageButton>:
    #size: height1, height1
    #size_hint: None, None
    height: dp(18)
    size_hint_y: None
    #background_color: lightgray
    AnchorLayout:
        size: self.parent.size
        pos: self.parent.pos
        HBox:
            anchor_x:'center'
            padding: 0
            #width: 
            Image:
                width: self.height
                size_hint_x: None
                source: root.image
            Label:
                #background_color: teal
                size_hint_x: None
                text: root.label
                color: lightgray
                #text_size: self.width, None
                width: self.texture_size[0] or 0
                #halign: 'left'
                font_size: dp(16)

#<ImageListButton>:

<ImageAddButton>:


<ImagePicker>:
    #height: dp(24)
    #size_hint_y: None
    ImageAddButton:
        image: 'img/Antu_folder-camera.png'
        label: 'добавить фото'
    #ImageAddButton:
        #image: 'img/plus_small.png'
    
''')



class ImageButton(Button):
    image = ObjectProperty(allownone=True)
    label = StringProperty(default='')

class ImagePicker(VBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.modal = ChoicesModal(choices=self)
        self.register_event_type('on_input')

    def on_input(self, filepath, uuid):
        pass
    
    def add_file(self, path):
        pass

class ImageListButton(ImageButton):
    pass
    
class ImageAddButton(ImageButton):
    #def __init__(self, *a, **kw):
        #print(222222222)
    @utils.asynced
    async def on_release(self, *a):
        filepath = filechooser.open_file()[0]
        self.parent.add_file(filepath)
        #print(filepath)


class Thumb(ImageButton):
    short_text = StringProperty(None, allownone=True)
    value = ObjectProperty(None, allownone=True)
    #fff = 0

    #def on_size(self, *args, **kwargs):
        ##super(Choice, self).on_size(*args, **kwargs)
        #Choice.fff += 1
        #print Choice.fff

