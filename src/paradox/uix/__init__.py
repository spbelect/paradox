from . import label, button, textinput

from .screens.screen_manager import ScreenManager

screenmgr = ScreenManager()

from .side_panel import SidePanel
sidepanel = SidePanel()

from .quiz_widgets.base import QuizWidget
#from kivy.app import App

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
