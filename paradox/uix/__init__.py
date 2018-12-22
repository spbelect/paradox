
from kivy.app import App

position = None
formlist = None
side_panel = None

async def init():
    # awkward way to break circular deps
    global position, formlist, side_panel
    from .screens.position_screen import PositionScreen
    from .screens.formlist_screen import FormListScreen
    position = PositionScreen(name='position')
    formlist = FormListScreen(name='formlist')
    
    side_panel = App.root.ids['side_panel']

App.nursery.start_soon(init)
#position = None
