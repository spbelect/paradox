from asyncio import Event
from kivy.lang import Builder

from kivy.properties import StringProperty
from kivy.properties import ObjectProperty
from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup
from loguru import logger

from button import Button

Builder.load_string('''
#:include constants.kv

#:import state app_state.state

<ConfirmModal>:
    background: ''
    #background_color: transparent

    text: ''
    yes: 'OK'
    no: 'Отмена'
    #header: ''
    hparent: getattr(self.parent, 'height', 10) * 0.9
    size_hint: 0.9, None
    #height: getattr(self.parent, 'height', 10) * 0.9
    height: 
        content.height if content.height < self.hparent else self.hparent
    #height:
        
    _anim_duration: 0
    _anim_alpha: 1
    #_window: app.root_window

    VBox:
        id: content
        orientation: 'vertical'
        height: message.height + buttons.height
        #padding: '12dp'
        ##cols: 1
        ##size_hint: None, None
        ##pos: root.pos
        ##size: root.size

        ScrollView:
            
            pos_hint: {'center_y': 0.5}
            id: scrollview
            scroll_distance: dp(30)
            size_hint_y: None
            height: message.height

            #VBox:
                #id: content
                #padding: 0

            Label:
                #background_color: teal
                id: message
                pos_hint: {'center_y': 0.5}
                text: root.text
                split_str: ' '
                text_size: self.width, None
                height: self.texture_size[1] + dp(10)
                
        BoxLayout:
            id: buttons
            spacing: dp(4)
            padding: dp(4)
            height: height1
            size_hint_y: None
            Button:
                background_color: lightgray
                color: black
                text: root.yes
                on_release:
                    root.answer = True
                    root.dismiss()
                
            Button:
                background_color: lightgray
                color: black
                text: root.no
                on_release:
                    root.answer = False
                    root.dismiss()
            
            
''')

class ConfirmModal(ModalView):
    text = StringProperty()
    yes = StringProperty()
    no = StringProperty()

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.answer = False
        self._closed = Event()
        
    def dismiss(self):
        self._closed.set()
        #logger.debug('dis')
        super().dismiss()
        
    async def wait(self):
        self.open()
        await self._closed.wait()
        return self.answer


async def yesno(text):
    modal = ConfirmModal(text=text, yes='Да', no='Нет')
    return await modal.wait()
