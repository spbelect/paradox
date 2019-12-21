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

from paradox.models import Answer, BoolAnswer, IntegerAnswer, AnswerImage
from paradox import uix
from paradox import utils
from paradox.uix import confirm
from paradox.uix.complaint import Complaint


class QuizWidget(Widget):
    json = ObjectProperty()
    form = ObjectProperty()
    value = ObjectProperty(None, allownone=True)
    answer = ObjectProperty(None, allownone=True)
    instances = InstanceManager()
    flags_match = BooleanProperty(True)
    
    def __init__(self, *args, **kwargs):
        self.complaint = None
        #self.answer = None
        super().__init__(*args, **kwargs)
        self.question_id = self.json['question_id']
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
            
    async def set_past_answers(self, answers):
        #await sleep(0.02)
        if not answers:
            self.value = None
            if self.complaint:
                self.remove_widget(self.complaint)
                self.complaint = None
            self.show_dependants()
            return
        
        if self.answer == list(answers)[-1]:
            return
        self.answer = list(answers)[-1]
        if self.answer.revoked:
            self.value = None
        else:
            self.value = self.answer.value()
            
        if self.answer.alarm and not self.answer.revoked \
            and state.get('role') not in ('other', 'videonabl'):
            #self.form.load_finished = False
            #await sleep(3)
            if not self.complaint:
                self.complaint = Complaint(quizwidget=self)
                self.add_widget(self.complaint)
            #logger.debug(f'Restoring complaint of past answer, quizwidget: {self.json["question_id"]}. Event timestamp={self.answer.time_created} value={self.answer.value()}')
            await self.complaint.on_event(self.answer)
            #self.form.load_finished = True
        elif self.complaint:
            self.remove_widget(self.complaint)
            self.complaint = None
            
        self.revise_dependants()
        
    def revise_complaint(self):

    def revise_dependants(self):
        if self.json.get('dependants'):
            logger.debug(f"{self.json['label']}, {self.json['dependants']}")
        for dep in self.json.get('dependants', []):
            if dep.get('value') == self.value:
                for quizwidget in QuizWidget.instances.filter(question_id=dep['iid']):
                    #quizwidget.show()
                    #quizwidget.disabled = False
                    quizwidget.visible = True
                continue
            if dep.get('range') and (dep['range'][0] <= self.value <= dep['range'][1]):
                for quizwidget in QuizWidget.instances.filter(question_id=dep['iid']):
                    #quizwidget.show()
                    #quizwidget.disabled = False
                    quizwidget.visible = True
                continue
            for quizwidget in QuizWidget.instances.filter(question_id=dep['iid']):
                #quizwidget.disabled = True
                quizwidget.visible = False
                #quizwidget.hide()
                
    def show_help(self):
        uix.screenmgr.show_handbook(self.json['label'], self.json['fz67_text'])
        
    async def new_answer(self, value):
        if uix.position.show_errors():
            self.show_state(self.value)
            uix.screenmgr.push_screen('position')
            return False
        
        if uix.userprofile.userprofile_errors():
            self.show_state(self.value)
            uix.screenmgr.push_screen('userprofile')
            return False

        if self.json['input_type'] == 'MULTI_BOOL':
            AnswerType = BoolAnswer
        elif self.json['input_type'] == 'NUMBER':
            AnswerType = IntegerAnswer
            value = int(value) if value else None
                
        if value == self.value:
            return False
        
        if self.value is not None:
            msg = f'Отозвать предыдущее значение?'
            if self.json['input_type'] == 'NUMBER':
                msg += f' ({self.answer.value()})'
            if not await uix.confirm.yesno(msg):
                self.show_state(self.answer.value())
                return False
            
            answer = Answer.objects.get(id=self.answer.id)
            answer.update(revoked=True, time_updated=now())
            uix.events_screen.add_event(answer)
            logger.info(f'Revoke answer input: {self.json["question_id"]}. New value: {value}')
            
        if value is not None:
            logger.info(f'New answer input: {self.json["question_id"]}. New value: {value}')
            alarm = False
            if self.json.get('alarm', None):
                #print(self.json['alarm'])
                if 'eq' in self.json['alarm']:
                    alarm = bool(value == self.json['alarm'].get('eq'))
                elif 'gt' in self.json['alarm']:
                    alarm = bool(int(value) > self.json['alarm'].get('gt'))
                
            #if alarm:
                #logger.info(f'alarm!')
                
            answer = AnswerType.objects.create(
                question_id=self.question_id,
                question_label=self.json['label'],
                value=value,
                #region='ru_78',
                #uik=55,
                alarm=alarm,
                region=state.region.id,
                uik=state.uik,
                role=state.role,
                time_updated=now()
            )
            
            uix.events_screen.add_event(answer)
        
        #campaigns = Campaign.objects.positional().filter(active=True, subscription='yes')
        #answer.coordinators = [x.coordinator.id for x in campaigns]
        
        self.value = value

        for quizwidget in QuizWidget.instances.filter(question_id=self.question_id):
            quizwidget.on_save_success(answer)
            
        if answer.alarm and not answer.revoked \
           and state.get('role') not in ('other', 'videonabl'):
            #self.form.load_finished = False
            #await sleep(3)
            #print(self.complaint)
            if not self.complaint:
                #logger.info(f'complaint!')
                self.complaint = Complaint(quizwidget=self)
                self.add_widget(self.complaint)
            #print(4343)
            await self.complaint.on_event(answer)
            await sleep(0.6)
            #self.form.load_finished = True
        elif self.complaint:
            self.remove_widget(self.complaint)
            self.complaint = None
        self.revise_dependants()
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
    
    def on_send_start(self, answer):
        pass
    
    def on_send_success(self, answer):
        #logger.debug(f'{self} {answer} tik_complaint_status: {answer.tik_complaint_status}')
        self.answer = event

    def on_send_error(self, answer):
        pass

    def on_send_fatal_error(self, answer):
        pass

    def on_save_success(self, answer):
        #logger.debug(f'{self} {answer} tik_complaint_status: {answer.tik_complaint_status}')
        self.answer = event

    #def on_answer(self, *a):
        #logger.debug(f'{self} {self.answer} tik_complaint_status: {self.answer.tik_complaint_status}')


async def restore_past_answers():
    #for quizwidget in QuizWidget.instances.all():
        #await quizwidget.set_past_answers(None)
    if not (state.get('uik') and state.get('region')):
        return
    filter = Q(uik=state.uik, region=state.region.id, time_created__gt=now()-timedelta(days=2))
    answers = list(Answer.objects.filter(filter).order_by('question_id'))
    logger.info(f'Restoring {len(answers)} past answers for {state.region.name} УИК {state.uik}')
    for iid, answers in groupby(answers, key=lambda x: x.question_id):
        e = sorted(answers, key=lambda x: x.time_created)
        for quizwidget in QuizWidget.instances.filter(question_id=iid):
            await quizwidget.set_past_answers(e)
            await sleep(0.05)
            
