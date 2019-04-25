from datetime import timedelta
from itertools import groupby

from app_state import state, on
from django.db.models import Q
from django.utils.timezone import now
from getinstance import InstanceManager
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty, Property
from kivy.clock import Clock
from kivy.uix.widget import Widget

from paradox.models import InputEvent, BoolInputEvent, IntegerInputEvent
from paradox import uix


class Input(Widget):
    json = ObjectProperty()
    form = ObjectProperty()
    value = ObjectProperty(None, allownone=True)
    instances = InstanceManager()
    
    def __init__(self, *args, **kwargs):
        super(Input, self).__init__(*args, **kwargs)
        self.input_id = self.json['input_id']
        self.apply_flags()

    @on('state.elect_flags')
    def apply_flags(self):
        flags = self.json.get('elect_flags')
        if not flags:
            return
        if set(flags) & state.get('elect_flags', set()):
            #self.show()
            self.disabled = False
        else:
            #self.hide()
            self.disabled = True
            
    def set_past_events(self, events):
        if events:
            self.value = list(events)[-1].get_value()
        else:
            self.value = None
        self.show_dependants()

    def show_dependants(self):
        for dep in self.json.get('dependants', []):
            if dep.get('value') == self.value:
                for input in Input.instances.filter(input_id=dep['iid']):
                    input.show()
                continue
            if dep.get('range') and (dep['range'][0] <= self.value <= dep['range'][1]):
                for input in Input.instances.filter(input_id=dep['iid']):
                    input.show()
                continue
            for input in Input.instances.filter(input_id=dep['iid']):
                input.hide()
                

    def on_input(self, value):
        #if uix.position.show_errors():
            #uix.screeens.push_screen('position')
            #return
        
        #if uix.userprofile.userprofile_errors():
            #uix.screeens.push_screen('userprofile')
            #return

        if self.json['input_type'] == 'MULTI_BOOL':
            InputEventt = BoolInputEvent
        elif self.json['input_type'] == 'NUMBER':
            InputEventt = IntegerInputEvent
            value = int(value) if value else None
            
        alarm = False
        if 'alarm_value' in self.json:
            alarm = bool(value == self.json['alarm_value'])
            
        event = InputEventt.objects.create(
            input_id=self.input_id,
            input_label=self.json['label'],
            value=value,
            #country=state.country,
            #region='ru_78',
            #uik=55,
            alarm=alarm,
            country=state.country,
            region=state.region.id,
            uik=state.uik,
        )
        
        #campaigns = Campaign.objects.positional().filter(active=True, subscription='yes')
        #event.coordinators = [x.coordinator.id for x in campaigns]

        for input in Input.instances.filter(input_id=self.input_id):
            input.on_save_success(event)
        uix.events_screen.add_event(event)

    def show(self):
        self.height = 10
        self.size_hint_y = 1
        self.opacity = 1
        
    def hide(self):
        self.height = 0
        self.size_hint_y = None
        self.opacity = 0

    def on_send_start(self, event):
        pass
    
    def on_send_success(self, event):
        pass

    def on_send_error(self, event):
        pass

    def on_send_fatal_error(self, event):
        pass

    def on_save_success(self, event):
        pass


@on('state.uik', 'state.region')
def restore_past_events():
    for input in Input.instances.all():
        input.set_past_events(None)
    if not (state.get('uik') and state.get('region')):
        return
    filter = Q(uik=state.uik, region=state.region.id, timestamp__gt=now()-timedelta(days=1))
    events = InputEvent.objects.filter(filter).order_by('input_id', 'timestamp')
    for iid, events in groupby(events, key=lambda x: x.input_id):
        for input in Input.instances.filter(input_id=iid):
            input.set_past_events(list(events))
            
