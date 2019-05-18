from uuid import uuid4
from os.path import basename

from kivy.lang import Builder

from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.properties import ObjectProperty
from kivy.uix.modalview import ModalView
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from plyer import filechooser

from button import Button
from paradox import utils
from paradox.uix.vbox import VBox
from paradox.uix.hbox import HBox

Builder.load_string('''
#:include constants.kv

#:import state app_state.state

<ImageButton>:
    size_hint_y: None
    height: dp(32)
    pos_hint: {'center_x': .5}
    Image:
        width: self.height
        size_hint_x: None
        source: root.image
        pos_hint: {'center_y': .5}
    Label:
        #background_color: teal
        size_hint_x: None
        text: root.label
        color: lightgray
        #text_size: self.width, None
        width: self.texture_size[0]
        #width: 200
        #halign: 'left'
        font_size: dp(16)

<ImageItem>:
    size_hint_y: None
    height: dp(32)
    pos_hint: {'center_x': .5}
   
    ImageButton:
        image: root.image
        label: root.label
        #on_click
    ImageButton:
        id: cross
        size: 10,10
        pos_hint: {'center_y': .5}
        image: 'img/x.png'

<ImageAddButton>:
    height: dp(18)


<ImagePicker>:
    padding: 0
    spacing: 0
    VBox:
        #visible: False
        id: images
    ImageAddButton:
        image: 'img/Antu_folder-camera.png'
        label: 'добавить фото'
        #image: 'img/plus_small.png'
    
''')



class ImageButton(ButtonBehavior, HBox):
    image = ObjectProperty(allownone=True)
    label = StringProperty(default='')

class ImagePicker(VBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.register_event_type('on_image_picked')

    def on_image_picked(self, filepath):
        self.add_image(filepath)
    
    def del_image(self, cross):
        self.ids.images.remove_widget(cross.parent)
        
    def add_image(self, filepath):
        i = ImageItem(
            image=filepath, 
            label=basename(filepath),
            #uuid=str(uuid or uuid4())
        )
        i.ids.cross.bind(on_release=self.del_image)
        self.ids.images.add_widget(i)
        return i
        

#class ImageListButton(ImageButton):
    #pass
    
class ImageAddButton(ImageButton):
    #def __init__(self, *a, **kw):
        #print(222222222)
    @utils.asynced
    async def on_release(self, *a):
        #TODO: thread
        filepath = filechooser.open_file()[0]
        #uuid=str(uuid4())
        self.parent.dispatch('on_image_picked', filepath)
        #self.parent.add_image(filepath)
        #print(filepath)


class ImageItem(HBox):
    #uuid = StringProperty()
    image = ObjectProperty()
    label = StringProperty()
    #value = ObjectProperty(None, allownone=True)
    #fff = 0

    #def on_click()
    #def on_size(self, *args, **kwargs):
        ##super(Choice, self).on_size(*args, **kwargs)
        #Choice.fff += 1
        #print Choice.fff

