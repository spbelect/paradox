 
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.properties import ObjectProperty
from kivy.uix.widget import Widget

from button import Button
from paradox.uix.vbox import VBox

Builder.load_string('''
#:include constants.kv

<ImageButton>:
    size_hint_y: None
    size_hint_x: None
    height: dp(32)
    pos_hint: {'center_x': .5, 'center_y': .5}
    padding: 0
    image_size: None
    color: lightgray
    Image:
        #width: self.height
        size: root.image_size or (root.height, root.height)
        #size: dp(32), dp(32)
        size_hint_x: None
        #size_hint: None, None
        source: root.image
        pos_hint: {'center_y': .5}
    Label:
        #background_color: teal
        #size_hint_x: None
        size_hint_y: 1
        text: root.label
        color: self.parent.color
        text_size: self.width, self.height
        shorten: True
        #width: self.texture_size[0]
        #width: 200
        #halign: 'left'
        font_size: dp(16)

    
''')



class ImageButton(ButtonBehavior, BoxLayout):
    image = ObjectProperty(allownone=True)
    label = StringProperty(default='')
