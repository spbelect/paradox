from datetime import timedelta
from itertools import groupby

from app_state import state, on
from django.db.models import Q
from django.utils.timezone import now
from getinstance import InstanceManager
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty, Property
from kivy.clock import Clock
from kivy.uix.widget import Widget
from loguru import logger

from paradox.models import InputEvent, BoolInputEvent, IntegerInputEvent, InputEventImage
from paradox import uix
from paradox import utils
from paradox.uix import confirm
from paradox.uix.complaint import Complaint


class Input(Widget):
    json = ObjectProperty()
    form = ObjectProperty()
    value = ObjectProperty(None, allownone=True)
    last_event = ObjectProperty(None, allownone=True)
    instances = InstanceManager()
    
    def __init__(self, *args, **kwargs):
        self.complaint = None
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
            self.last_event = list(events)[-1]
            if self.last_event.revoked:
                self.value = None
            else:
                self.value = self.last_event.get_value()
                
            if self.last_event.alarm and not self.last_event.revoked:
                if not self.complaint:
                    self.complaint = Complaint(input=self)
                    self.add_widget(self.complaint)
                self.complaint.on_event(self.last_event)
            elif self.complaint:
                self.remove_widget(self.complaint)
                self.complaint = None
        else:
            self.value = None
            if self.complaint:
                self.remove_widget(self.complaint)
                self.complaint = None
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
                
    def show_help(self):
        uix.screenmgr.show_handbook(self.json['label'], self.json['fz67_text'])
        
    @utils.asynced
    async def on_input(self, value):
        if uix.position.show_errors():
            uix.screenmgr.push_screen('position')
            return False
        
        if uix.userprofile.userprofile_errors():
            uix.screenmgr.push_screen('userprofile')
            return False

        if self.json['input_type'] == 'MULTI_BOOL':
            InputEventt = BoolInputEvent
        elif self.json['input_type'] == 'NUMBER':
            InputEventt = IntegerInputEvent
            value = int(value) if value else None
                
        if value == self.value:
            return False
        
        if self.value is not None:
            if not await uix.confirm.yesno('Отозвать предыдущее значение?'):
                self.set_state(self.last_event.get_value())
                return False
            
            event = InputEvent.objects.get(id=self.last_event.id)
            event.update(revoked=True, time_updated=now())
            uix.events_screen.add_event(event)
            logger.info('revoke event')
            
        if value is not None:
            logger.info('new event')
            alarm = False
            if self.json.get('alarm', None):
                #print(self.json['alarm'])
                if 'eq' in self.json['alarm']:
                    alarm = bool(value == self.json['alarm'].get('eq'))
                elif 'gt' in self.json['alarm']:
                    alarm = bool(int(value) > self.json['alarm'].get('gt'))
                
            event = InputEventt.objects.create(
                input_id=self.input_id,
                input_label=self.json['label'],
                value=value,
                #region='ru_78',
                #uik=55,
                alarm=alarm,
                region=state.region.id,
                uik=state.uik,
                role=state.role,
                time_updated=now()
            )
            
            uix.events_screen.add_event(event)
        
        #campaigns = Campaign.objects.positional().filter(active=True, subscription='yes')
        #event.coordinators = [x.coordinator.id for x in campaigns]
        
        self.value = value

        for input in Input.instances.filter(input_id=self.input_id):
            input.on_save_success(event)
            
        if event.alarm and not event.revoked:
            if not self.complaint:
                self.complaint = Complaint(input=self)
                self.add_widget(self.complaint)
            self.complaint.on_event(event)
        elif self.complaint:
            self.remove_widget(self.complaint)
            self.complaint = None
        return True

    def show(self):
        self.height = 10
        self.size_hint_y = 1
        self.opacity = 1
        
    def hide(self):
        self.height = 0
        self.size_hint_y = None
        self.opacity = 0

    def set_state(self, value):
        pass
    
    def on_send_start(self, event):
        pass
    
    def on_send_success(self, event):
        pass

    def on_send_error(self, event):
        pass

    def on_send_fatal_error(self, event):
        pass

    def on_save_success(self, event):
        self.last_event = event


@on('state.uik', 'state.region')
def restore_past_events():
    for input in Input.instances.all():
        input.set_past_events(None)
    if not (state.get('uik') and state.get('region')):
        return
    filter = Q(uik=state.uik, region=state.region.id, time_created__gt=now()-timedelta(days=1))
    events = InputEvent.objects.filter(filter).order_by('input_id', 'time_created')
    for iid, events in groupby(events, key=lambda x: x.input_id):
        for input in Input.instances.filter(input_id=iid):
            input.set_past_events(list(events))
            
