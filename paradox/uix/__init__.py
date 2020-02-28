from .screens.screen_manager import ScreenManager

from .screens.userprofile_screen import UserProfileScreen
from .screens.position_screen import PositionScreen
from .screens.formlist_screen import FormListScreen
from .screens.events_screen import EventsScreen
from .screens.coordinators_screen import CoordinatorsScreen
#from .screens.events_screen import EventsScreen
from .screens.tik_complaint_screen import TikComplaintScreen


coordinators = CoordinatorsScreen(name='coordinators')
tik_complaint = TikComplaintScreen(name='tik_complaint')
events_screen = EventsScreen(name='events')
formlist = FormListScreen(name='formlist')
position = PositionScreen(name='position')
userprofile = UserProfileScreen(name='userprofile')

screenmgr = ScreenManager()

from .sidepanel import SidePanel
sidepanel = SidePanel()

from .quiz_widgets.base import QuizWidget
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
