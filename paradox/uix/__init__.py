from .screens.screens import Screens

from .screens.position_screen import PositionScreen
from .screens.formlist_screen import FormListScreen
#from .screens.coordinators_screen import CoordinatorsScreen
from .screens.events_screen import EventsScreen



formlist = FormListScreen(name='formlist')
position = PositionScreen(name='position')

screeens = Screens()

from .sidepanel import SidePanel
sidepanel = SidePanel()

#from kivy.app import App

#position = None
#formlist = None
#side_panel = None

#async def init():
    ## awkward way to break circular deps
    #global position, formlist, side_panel
    #from .screens.position_screen import PositionScreen
    #from .screens.formlist_screen import FormListScreen
    #position = PositionScreen(name='position')
    #formlist = FormListScreen(name='formlist')
    
    #side_panel = App.root.ids['side_panel']

#App.nursery.start_soon(init)
##position = None
