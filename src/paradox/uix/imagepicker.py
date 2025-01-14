from asyncio import sleep
from uuid import uuid4
from os.path import basename, exists
from shutil import move
from pathlib import Path

from app_state import state
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty
from kivy.properties import ObjectProperty
from kivy.uix.modalview import ModalView
from kivy.uix.scatter import Scatter
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.utils import platform
from loguru import logger
from plyer import filechooser

import paradox
from paradox.uix.button import Button
from paradox import utils
from paradox import gallery
from paradox import camera
from paradox import exception_handler
from paradox.uix.vbox import VBox
from paradox.uix.hbox import HBox
from paradox.uix.imagebutton import ImageButton


Builder.load_string('''
#:include constants.kv

#:import state app_state.state

<ActionModal>:
    height: dp(200)
    background: ''
    size_hint: 0.9, None
    
    VBox:
        spacing: dp(20)
        height: dp(200)
        ImageButton:
            size_hint_y: 1
        
            #background_color: white
            height: dp(70)
            id: take_photo
            image: 'img/Antu_folder-camera.png'
            label: 'Камера'
            width: dp(200)
            color: black
            #image: 'img/plus_small.png'
        ImageButton:
            size_hint_y: 1
            height: dp(70)
            #background_color: white
            color: black
            id: pick_file
            image: 'img/HAMBURGER_MENU-1282.png'
            label: 'Выбрать файл'
            width: dp(200)
            #image: 'img/plus_small.png'

<ImageModal>:
    #ScrollView:
    #Scatter:
    BoxLayout:
        orientation: 'vertical'
        #Button:
            #on_release: root.dismiss()
        ImageScatter:
            id: scat
            #size: self.parent.size
            #pos: self.parent.pos
            do_rotation: False
            auto_bring_to_front: False
            scale: 1.0
            Image:
                id: img
        #Label:
            #text: str(scat.size)
            #size_hint_y: None
            #height: height1
        #Label:
            #text: str(scat.scale)
            #size_hint_y: None
            #height: height1
        Button:
            #pos_hint: {'bottom': 0}
            background_color: transparent
            #background_color: teal
            size_hint_y: None
            height: height1
            #width: root.width
            color: white
            text: '< назад'
            outline_width: dp(1)
            on_release: root.dismiss()
            
<ImageItem>:
    size_hint: None, None
    #size_hint_y: None
    height: dp(32)
    width: dp(300)
    #pos_hint: {'center_x': .5}
    pos_hint: {'center_x': .5, 'center_y': .5}
    spacing: dp(8)
   
    Button:
        #image: root.image
        text: root.label
        size_hint_x: 1
        height: dp(32)
        color: lightgray
        text_size: self.width, self.height
        shorten: True
        #width: self.texture_size[0]
        #width: 200
        #halign: 'left'
        font_size: dp(16)
        #width: dp(190)
        on_release: root.on_release()
        #on_click
    ImageButton:
        id: cross
        size: dp(32),dp(32)
        image_size: dp(20), dp(20)
        pos_hint: {'center_y': .5}
        image: 'img/x.png'
        

#<ImageAddButton>:


<ImagePicker>:
    padding: 0
    spacing: 0
    VBox:
        #visible: False
        id: images
        width: dp(300)
        pos_hint: {'center_x': .5}
    ImageAddButton:
        size_hint_y: 1
        image: 'img/Antu_folder-camera40.png'
        label: 'добавить фото'
        width: dp(200)
        font_size: font1
        height: self.font_size
        image_size: dp(20), dp(20)
        #image: 'img/plus_small.png'
    #Button:
        #on_release: root.gg()
        #text: 'ggg'
        #width: dp(200)
        #pos_hint: {'center_x': .5}
        #color: black
    
''')



class ImagePicker(VBox):
    compress_quality = NumericProperty(None, allownone=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.register_event_type('on_image_picked')

    def compress(self, filepath):
        if self.compress_quality:
            from PIL import Image
            img = Image.open(filepath)
            #fill_color = ''  # your background
            #image = Image.open(file_path)
            if not img.mode == 'RGB':
                #background = Image.new(image.mode[:-1], image.size)
                #background.paste(image, image.split()[-1])
                #image = background
                img = img.convert('RGB')
            f = Path(filepath)
            filepath = f.with_name(f'{f.stem}_x.jpg')
            
            img.save(str(filepath), optimize=True, quality=self.compress_quality)
        return str(filepath)
 
    def on_image_picked(self, filepath):
        filepath = self.compress(filepath)
        self.add_image(filepath)
    
    def on_cross_clik(self, cross):
        self.ids.images.remove_widget(cross.parent)
        
    def del_images(self):
        for item in self.ids.images.children[:]:
            self.ids.images.remove_widget(item)
        
    def add_image(self, filepath):
        i = ImageItem(
            image=filepath, 
            label=basename(filepath),
            #uuid=str(uuid or uuid4())
        )
        i.ids.cross.bind(on_release=self.on_cross_clik)
        self.ids.images.add_widget(i)
        return i
    
#class ImageListButton(ImageButton):
    #pass
    
class ImageAddButton(ImageButton):
    #def __init__(self, *a, **kw):
        #print(222222222)
        
    #@utils.asynced
    def on_release(self, *a):
        self.modal = ActionModal()
        self.modal.ids.pick_file.bind(on_release=self.pick_file)
        self.modal.ids.take_photo.bind(on_release=self.take_photo)
        self.modal.open()
        
    @utils.asynced
    async def pick_file(self, *a):
        if platform == 'android':
            self.modal.dismiss()
            if not await utils.ask_permissions('WRITE_EXTERNAL_STORAGE', 'READ_EXTERNAL_STORAGE'):
                return
            paradox.gallery.user_select_image(self.on_file_picked)
        else:
            filepath = filechooser.open_file()
            if filepath:
                self.parent.dispatch('on_image_picked', filepath[0])
                
        
    def on_file_picked(self, file):
        
        paradox.exception_handler.send_debug_message(f'on_file_picked {file}')
        if file:
            if file.startswith('file://'):
                file = file[7:]
            elif file.startswith('content:') or file.startswith('media:'):
                raise Exception(f"Can't handle {file}")
            self.parent.dispatch('on_image_picked', file)
            
            logger.debug(f'111, {file}')
            
    @utils.asynced
    async def take_photo(self, *a):
        self.modal.dismiss()
        #TODO: thread
        if platform == 'android':
            #filename = uuid4()
            if not await utils.ask_permissions('WRITE_EXTERNAL_STORAGE', 'READ_EXTERNAL_STORAGE'):
                return
            from jnius import autoclass
            env = autoclass('android.os.Environment')
            dir = env.getExternalStoragePublicDirectory(env.DIRECTORY_DCIM).getPath()
            fpath = f'{dir}/{uuid4()}.jpg'
            logger.debug(fpath)
            paradox.camera.take_picture(fpath, on_complete=self.on_photo_taken)
        else:
            filepath = filechooser.open_file()
            if filepath:
                self.parent.dispatch('on_image_picked', filepath[0])

    #@utils.asynced
    def on_photo_taken(self, file):
        paradox.exception_handler.send_debug_message(f'on_photo_taken {file}')
        #move(filename, state.user_data_dir + '/')
        logger.debug(f'aaa {file}')
        #await sleep(0.5)
        
        if file.startswith('file://'):
            file = file[7:]
        elif file.startswith('content:') or file.startswith('media:'):
            raise Exception(f"Can't handle {file}")
        #for x in range(10):
            
        if exists(file):
            Clock.schedule_once(lambda dt: self.parent.dispatch('on_image_picked', file), 0.5)
        else:
            raise Exception(f'File {file} does not exist.')
        #self.parent.dispatch('on_image_picked', filename) #join(state.user_data_dir, filename))


class ActionModal(ModalView):
    pass

class ImageModal(ButtonBehavior, ModalView):
    image = StringProperty()
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        Clock.schedule_once(lambda dt: setattr(self.ids.img, 'source', self.image), 0.1)
        
        #self.ids.img.source = self.image
    
class ImageItem(BoxLayout):
    #uuid = StringProperty()
    image = StringProperty()
    label = StringProperty()
    #value = ObjectProperty(None, allownone=True)
    #fff = 0

    def on_release(self):
        self.modal = ImageModal(image=self.image)
        self.modal.open()

    #def on_click()
    #def on_size(self, *args, **kwargs):
        ##super(Choice, self).on_size(*args, **kwargs)
        #Choice.fff += 1
        #print Choice.fff

class ImageScatter(ScatterLayout):
    def on_touch_down(self, touch):
        #x, y = touch.x, touch.y
        #self.prev_x = touch.x
        #self.prev_y = touch.y
        #print(3)
        if touch.is_mouse_scrolling:
            #print(11)
            if touch.button == 'scrolldown':
                #print('down')
                ## zoom in
                if self.scale < 10:
                    self.scale = self.scale * 1.1

            elif touch.button == 'scrollup':
                #print('up')## zoom out
                if self.scale > 1:
                    self.scale = self.scale * 0.8
        return super().on_touch_down(touch)
