from kivy.properties import StringProperty, BooleanProperty, ObjectProperty, Property
from kivy.clock import Clock
#from scheduler import schedule
from ..objects_manager import objects_manager


@objects_manager
class Input(object):
    json = ObjectProperty()
    form = ObjectProperty()
    #value = ObjectProperty(None, allownone=True)

    def __init__(self, *args, **kwargs):
        super(Input, self).__init__(*args, **kwargs)
        self.input_id = self.json['input_id']
        #print self.input_id

    def on_send_success(self, event):
        pass

    def on_send_error(self, event, request, error_data):
        pass

    def on_send_fatal_error(self, event, request, error_data):
        pass

    def on_save_success(self, eid, timestamp, value):
        pass

    def add_past_event(self, event):
        pass

    def reset(self):
        pass
