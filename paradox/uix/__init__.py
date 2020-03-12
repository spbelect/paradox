from .screens.screen_manager import ScreenManager

from .screens.userprofile_screen import UserProfileScreen
from .screens.position_screen import PositionScreen
from .screens.home_screen import HomeScreen
from .screens.events_screen import EventsScreen
from .screens.coordinators_screen import CoordinatorsScreen
#from .screens.tik_complaint_screen import TikComplaintScreen
from .screens.complaint_screen import ComplaintScreen


coordinators = CoordinatorsScreen(name='coordinators')
#tik_complaint = TikComplaintScreen(name='tik_complaint')
complaint = ComplaintScreen(name='complaint')
events_screen = EventsScreen(name='events')
homescreen = HomeScreen(name='home')
position = PositionScreen(name='position')
userprofile = UserProfileScreen(name='userprofile')

screenmgr = ScreenManager()

from .sidepanel import SidePanel
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
