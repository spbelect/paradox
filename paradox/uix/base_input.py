from kivy.properties import StringProperty, BooleanProperty, ObjectProperty, Property
from kivy.clock import Clock
#from scheduler import schedule
from getinstance import InstanceManager
from kivy.uix.widget import Widget

class Input(Widget):
    json = ObjectProperty()
    form = ObjectProperty()
    #value = ObjectProperty(None, allownone=True)
    instances = InstanceManager()

    def __init__(self, *args, **kwargs):
        print(1, args, kwargs)
        super(Input, self).__init__(*args, **kwargs)
        print(2, args, kwargs)
        #self.json = kwargs.get('json')
        self.input_id = self.json['input_id']
        #bind()
        #print self.input_id

    def on_send_start(self, event):
        pass
    
    def on_send_success(self, event):
        pass

    def on_send_error(self, event, request, error_data):
        pass

    def on_send_fatal_error(self, event, request, error_data):
        pass

    def on_save_success(self, event):
        pass

    def add_past_event(self, event):
        pass

    def reset(self):
        pass

    def on_input(self, value):
        if uix.PositionScreen.show_errors():
            App.screens.push_screen('position')
            return
        
        if uix.UserProfileScreen.userprofile_errors():
            App.screens.push_screen('userprofile')
            return

        event = InputEvent.objects.create(
            input_id=self.input_id,
            input_label=self.json['input_label'],
            value=value,
            country=state.country,
            region=state.region.id,
            uik=state.uik,
        )
        
        #campaigns = Campaign.objects.positional().filter(active=True, subscription='yes')
        #event.coordinators = [x.coordinator.id for x in campaigns]

        for input in Input.instances.find(iid=self.input_id):
            input.on_save_success(event)
        uix.EventsScreen.add_event(event)

