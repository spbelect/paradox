from kivy.lang import Builder

from kivy.properties import StringProperty
from kivy.properties import ObjectProperty
from kivy.properties import BooleanProperty
from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup
from loguru import logger

from paradox.uix.vbox import VBox
from paradox.uix.button import Button

Builder.load_string('''
#:include constants.kv

#:import state app_state.state


<FrozenEditor>:
    padding: 0
        
    VBox:
        visible: root.frozen
        padding: 0
        spacing: dp(10)
        
        # Readonly text preview
        Label:
            font_size: sp(18)
            split_str: ' '
            text_size: self.width, None
            height: self.texture_size[1]
            markup: True
            halign: 'left'
            text: root.text or ''
            disabled_color: lightgray
            color: black

        Button:
            id: edit_button
            text: 'Редактировать текст'
            on_release: root.frozen = False
            color: teal
            disabled_color: lightgray  # Some kivy bug requires to set this explicitly
            
        
    VBox:
        #id: editable_block
        visible: not root.frozen
        padding: 0
        spacing: dp(10)
        
        # Editable text
        TextInput:
            id: textinput
            text: root.text or ''
            color: black
            multiline: True
            #height: root.height * 0.6
            
            height: self.minimum_height
            size_hint_y: None
        
        Button:
            id: save
            color: teal
            text: 'Сохранить'
            on_release: root.on_save_cilck()
                        

''')




class FrozenEditor(VBox):
    text = StringProperty(None, allownone=True)
    frozen = BooleanProperty(True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.register_event_type('on_save')

    def on_save_cilck(self):
        self.frozen = True
        self.text = self.ids.textinput.text
        self.dispatch('on_save', self.text)

    def on_save(self, *a):
        pass  # Default handler. Should be overriden.
        
