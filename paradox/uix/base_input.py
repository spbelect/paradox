from datetime import timedelta
from itertools import groupby
from asyncio import sleep

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
    #last_event = ObjectProperty(None, allownone=True)
    instances = InstanceManager()
    flags_match = BooleanProperty(True)
    
    def __init__(self, *args, **kwargs):
        self.complaint = None
        self.last_event = None
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
            self.flags_match = True
        else:
            #self.hide()
            self.flags_match = False
            
    async def set_past_events(self, events):
        #await sleep(0.02)
        if events:
            if self.last_event == list(events)[-1]:
                return
            self.last_event = list(events)[-1]
            if self.last_event.revoked:
                self.value = None
            else:
                self.value = self.last_event.get_value()
                
            if self.last_event.alarm and not self.last_event.revoked \
               and state.get('role') not in ('other', 'videonabl'):
                #self.form.load_finished = False
                #await sleep(3)
                if not self.complaint:
                    self.complaint = Complaint(input=self)
                    self.add_widget(self.complaint)
                logger.debug(f'Restoring complaint of past event, input: {self.json["input_id"]}. Event timestamp={self.last_event.time_created} value={self.last_event.get_value()}')
                await self.complaint.on_event(self.last_event)
                #self.form.load_finished = True
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
        
    async def on_input(self, value):
        if uix.position.show_errors():
            self.show_state(self.value)
            uix.screenmgr.push_screen('position')
            return False
        
        if uix.userprofile.userprofile_errors():
            self.show_state(self.value)
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
            msg = f'Отозвать предыдущее значение?'
            if self.json['input_type'] == 'NUMBER':
                msg += f' ({self.last_event.humanized_value()})'
            if not await uix.confirm.yesno(msg):
                self.show_state(self.last_event.get_value())
                return False
            
            event = InputEvent.objects.get(id=self.last_event.id)
            event.update(revoked=True, time_updated=now())
            uix.events_screen.add_event(event)
            logger.info(f'Revoke event input: {self.json["input_id"]}. New value: {value}')
            
        if value is not None:
            logger.info(f'New event input: {self.json["input_id"]}. New value: {value}')
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
            
        if event.alarm and not event.revoked \
           and state.get('role') not in ('other', 'videonabl'):
            #self.form.load_finished = False
            #await sleep(3)
            if not self.complaint:
                self.complaint = Complaint(input=self)
                self.add_widget(self.complaint)
            #print(4343)
            await self.complaint.on_event(event)
            await sleep(0.6)
            #self.form.load_finished = True
        elif self.complaint:
            self.remove_widget(self.complaint)
            self.complaint = None
        return True

    def __del__(self):
        print(f'del {self}')
        
    def show(self):
        self.height = 10
        self.size_hint_y = 1
        self.opacity = 1
        
    def hide(self):
        self.height = 0
        self.size_hint_y = None
        self.opacity = 0

    def show_state(self, value):
        pass
    
    def on_send_start(self, event):
        pass
    
    def on_send_success(self, event):
        #logger.debug(f'{self} {event} tik_complaint_status: {event.tik_complaint_status}')
        self.last_event = event

    def on_send_error(self, event):
        pass

    def on_send_fatal_error(self, event):
        pass

    def on_save_success(self, event):
        #logger.debug(f'{self} {event} tik_complaint_status: {event.tik_complaint_status}')
        self.last_event = event

    #def on_last_event(self, *a):
        #logger.debug(f'{self} {self.last_event} tik_complaint_status: {self.last_event.tik_complaint_status}')


async def restore_past_events():
    #for input in Input.instances.all():
        #await input.set_past_events(None)
    if not (state.get('uik') and state.get('region')):
        return
    filter = Q(uik=state.uik, region=state.region.id, time_created__gt=now()-timedelta(days=2))
    events = InputEvent.objects.filter(filter).order_by('input_id', 'time_created')
    logger.info(f'Restoring {events.count()} past events for {state.region.name} УИК {state.uik}')
    for iid, events in groupby(events, key=lambda x: x.input_id):
        for input in Input.instances.filter(input_id=iid):
            await input.set_past_events(list(events))
            await sleep(0.05)
            
