# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from functools import wraps

from app_state import state, on
from getinstance import InstanceManager
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.behaviors.button import ButtonBehavior
from loguru import logger

from label import Label
from ..vbox import VBox


Builder.load_string('''
#:include constants.kv
#:import state app_state.state

<HomeScreen>:
    BoxLayout:
        orientation: 'vertical'
        
        ScrollView:
            VBox:
                padding: 0, dp(10)
                spacing: dp(8)

                Label:
                    text: 'Анкеты'
                    height: dp(20)
                    text_size: self.size
                    font_size: sp(18)
                    color: lightgray
                    
                    Label:
                        text: "Анкеты обновляются..."
                        id: topics_loader
                        pos: self.parent.pos
                        font_size: sp(18)
                        size: self.parent.size
                        background_color: wheat4
    
                VBox:
                    id: messages
                VBox:
                    id: topics
                    padding: 0

                Widget:  # spacer
                    height: dp(60)
                    size_hint: 1, None

        BoxLayout:
            height: height1
            size_hint: 1, None

            Button:
                background_normal: 'img/HAMBURGER_MENU-1282.png'
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
                #text_size: 100, 300
                size_hint: None, None
                width: dp(150)
                height: height1
                #background_color: (4,4,0,1)
                background_normal: ''
                color: lightgray
                pos_hint: {'center_y':.5}
                #font_size: sp(30)

            Widget:  # horizontal spacer


<QuizTopicButton>:
    halign: 'left'
    split_str: ' '
    text_size: self.width, None
    height: self.texture_size[1]
    size_hint_y: None
    #width: 300
    text: self.json['name']


''')


class QuizTopicButton(ButtonBehavior, Label):
    """
    Кнопка открывающая экран тематического раздела анкеты.
    """
    json = ObjectProperty()
    id = StringProperty()


class HomeScreen(Screen):
    def build_topics(self):
        # Remove all current TopicItems
        for item in self.ids.topics.children[:]:
            self.ids.topics.remove_widget(item)
            
        logger.debug(f'Rebuilding {len(state.quiz_topics[state.country])} quiz topics.')
        
        for topic in state.quiz_topics[state.country]:
            if not topic['name'] or not topic['id']:
                logger.error(topic)
                continue
            self.ids.topics.add_widget(QuizTopicButton(
                json = topic, id = str(topic['id']),
                on_release = lambda button: self.manager.show_quiztopic(button.json)
            ))
            

    def show_loader(self, f):
        @wraps(f)
        async def wrapped(*a, **kw):
            self.ids.topics_loader.height = dp(20)
            self.ids.topics_loader.opacity = 1
            try:
                return await f(*a, **kw)
            finally:
                #logger.debug('hide loader')
                self.ids.topics_loader.height = 0
                self.ids.topics_loader.opacity = 0
        return wrapped


    #def show_campaign_forms(self):
        #pass
