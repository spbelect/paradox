from kivy.lang import Builder

from kivy.properties import StringProperty
from kivy.properties import ObjectProperty
from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup
from loguru import logger

from paradox.uix.button import Button

Builder.load_string('''
#:include constants.kv

#:import state app_state.state

<ChoicePickerModal>:
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
                    text: root.choicepicker.modal_header
                    color: white
                    background_color: lightgray
                VBox:
                    id: list


<ChoicePicker>:
    color: lightgray
    height: height1
    size_hint_y: None
    text_size: self.width, None
    #on_kv_post: self.choice = self.getchoice(self.value)
    
    #text: self.choice.short_text if self.choice else ''
    #value: self.choice.value if self.choice else None

<Choice>:
    color: black
    #width: self.parent.width if self.parent else '300dp'
    width: 0.9 * (self.parent.width if self.parent else 29)
    #width: 40
    size_hint: None, None
    #size: '300dp', height1 * 2
    #height: height1 * 1.5

    split_str: ' '
    #text_size: 300, 100
    text_size: self.width, None
    height: self.texture_size[1] + dp(10)

''')


class Choice(Button):
    short_text = StringProperty(None, allownone=True)
    value = ObjectProperty(None, allownone=True)
    #fff = 0

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"Choice <{self.short_text or self.text}>"

    #def __init__(self, *args, **kwargs):
        #super().__init__(*args, **kwargs)
        #if not self.short_text:
            #self.short_text = self.text
            
    # def on_color(self, *a):
    #     print(f"{self} {id(self)} oncolor {a}, {self.color=}")

    def on_parent(self, selff, parent):
        if parent is None and hasattr(self, 'instances'):
            #logger.debug(f'Widget parnet is None, remove {self}.')
            self._instances_weakset.remove(self)
        # if parent:
        #     logger.debug(f"{self.parent=} {self.text=} {self.short_text=} {self.value=}")
        # else:
        #     logger.debug(f"{self.text=} {self.short_text=} {self.value=}")

    #def on_size(self, *args, **kwargs):
        ##super(Choice, self).on_size(*args, **kwargs)
        #Choice.fff += 1
        #print Choice.fff


class ChoicePicker(Button):
    choice = ObjectProperty(None, allownone=True)
    modal_header = StringProperty()
    value = ObjectProperty(None, allownone=True)
    #input_value = ObjectProperty(None, allownone=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.modal = ChoicePickerModal(choicepicker=self)
        self.register_event_type('on_new_pick')

    def on_release(self):
        self.modal.open()

    def on_new_pick(self, *a):
        pass
        
    def on_choice(self, *a):
        # logger.debug(f'{a}')
        if self.choice:
            self.text = self.choice.short_text or self.choice.text
            self.value = self.choice.value
        else:
            self.text = ''
            self.value = None

    def add_widget(self, child):
        self.modal.ids.list.add_widget(child)
        # logger.error(f'{self.text=} {child=} {child.color=}')

    def remove_choice(self, value):
        for child in self.modal.ids.list.children[:]:
            if child.value == value:
                if self.choice == child:
                    self.choice = None
                self.modal.ids.list.remove_widget(child)
                break
            
    def clear(self):
        self.choice = None
        for child in self.modal.ids.list.children[:]:
            self.modal.ids.list.remove_widget(child)

    def choices(self):
        return self.modal.ids.list.children[:]
    
    def getchoice(self, value):
        for child in self.modal.ids.list.children[:]:
            if child.value == value:
                # logger.debug(f'{value=} found')
                return child
        # logger.debug(f'{value=} not found {len(self.modal.ids.list.children)}')

    def setchoice(self, value):
        self.choice = self.getchoice(value)
        

class ChoicePickerModal(ModalView):
    choicepicker = ObjectProperty()   # Parent ChoicePicker

    def on_touch_down(self, touch):
        if self.ids.scrollview.effect_y.velocity > 0:
            # The touch stops scrolling
            touch.ud['sv.stopped'] = True
        return super().on_touch_down(touch)
        #return res

    #def on_touch_move(self, touch):
        #res = super().on_touch_move(touch)
        #sv_ud = touch.ud.get(self.ids['scrollview']._get_uid())
        ##print sv_ud['mode'], sv_ud['user_stopped'] #, stopped, scrolled
        #sv = self.ids['scrollview']
        ##print sv.effect_y.scroll, sv.effect_y.velocity, sv.effect_y.displacement
        ##if sv.effect_y.displacement > sv.scroll_distance:
            ### The touch stops scrolling
            ##touch.ud['sv.stopped'] = True
        #return res

    def on_touch_up(self, touch):
        #res = super().on_touch_up(touch)
        #sv = self.ids['scrollview']
        scrolled = not touch.ud.get('sv.can_defocus', True)
        #scrolled = False  # FIXME
        if 'button' in touch.profile and touch.button.startswith('scroll'):
            scrolled = True
        stopped = touch.ud.get('sv.stopped', False)
        if (not stopped and not scrolled):
            touch.push()
            touch.apply_transform_2d(self.ids.scrollview.to_local)
            for child in self.ids.list.children:
                if child.collide_point(touch.x, touch.y):
                    self.choicepicker.choice = child
                    self.choicepicker.dispatch('on_new_pick', child.value)
                    self.dismiss()
                    return True
            touch.pop()
