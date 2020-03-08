# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from app_state import state
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from loguru import logger

# It has to be imported first to register new Label and Button with Factory
#from .label import Label
#from .button import Button

from .navigationdrawer.navigationdrawer import NavigationDrawer
#from .screens.screens import screens
from paradox import uix


Builder.load_string('''
#:include constants.kv
#:import state app_state.state
##:import SidePanel paradox.uix.sidepanel.SidePanel

<MainWidget>:
    # NavigationDrawer settings
    touch_accept_width: dp(45)  # width to toggle navigation drawer
    side_panel_width: min(dp(450), 0.8*self.width)
    min_dist_to_open: 0.25
    min_dist_to_close: 0.1
    opening_transition: 'linear'
    closing_transition: 'linear'
    anim_time: 0.1

    #SidePanel:
        #id: side_panel

    #Screens:
        #id: screens

''')


class MainWidget(NavigationDrawer):
    def __init__(self, *a, **kw):
        ##kw['__no_builder'] = False
        super().__init__(*a, **kw)
        self.add_widget(uix.sidepanel)
        self.add_widget(uix.screenmgr)
        logger.debug(f'MainWidget created {self}')
        
        
    #async def init(self):
        #App.screens = App.root.ids['screens']   
