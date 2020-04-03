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
from paradox.uix import float_message
from paradox.uix import confirm
#from paradox.uix.complaint import Complaint


class QuizWidget(Widget):
    question = ObjectProperty()
    form = ObjectProperty()
    value = ObjectProperty(None, allownone=True)
    answer = ObjectProperty(None, allownone=True)
    instances = InstanceManager()
    flags_match = BooleanProperty(True)
    conditions_ok = BooleanProperty(True)
    complaint_visible = BooleanProperty(False)
    status_text = StringProperty('')
    
    
    def __init__(self, *args, **kwargs):
        #self.complaint = None
        #self.answer = None
        #import ipdb; ipdb.sset_trace()
        super().__init__(*args, **kwargs)
        #logger.debug(f'QuizWidget.__init__: question = {self.question}')
        self.check_visibility()

    async def set_past_answers(self, answers):
        #await sleep(0.02)
        if not answers:
            self.answer = None
            return
        
        if self.answer == list(answers)[-1]:
            return
        
        self.answer = list(answers)[-1]
        
        
    def show_help(self):
        uix.screenmgr.show_handbook(self.question.label, self.question.fz67_text)
        
    async def add_new_answer(self, value):
        #if self.question.id in state._pending_save_questions:
            ## Prevent adding new values until saved in db
            #uix.float_message.show('Предыдущий ответ еще не сохранен!')
            #return False
        
        if uix.position.show_errors():
            uix.screenmgr.push_screen('position')
            return False
        
        if uix.userprofile.userprofile_errors():
            uix.screenmgr.push_screen('userprofile')
            return False

        if self.question.type == 'YESNO':
            AnswerType = BoolAnswer
        elif self.question.type == 'NUMBER':
            AnswerType = IntegerAnswer
            value = int(value) if value else None
                
        #if self.answer and value == self.answer.value:
            #return False
        
        ## Prevent adding new values until saved in db
        #state._pending_save_questions.add(self.question.id)
            
        sibling_widgets = QuizWidget.instances.filter(question__id=self.question.id)
        sibling_widgets.status_text = 'сохраняется'
        
        try:
            if self.answer and not self.answer.revoked:
                msg = f'Отозвать предыдущее значение?'
                if self.question.type == 'NUMBER':
                    msg += f' ({self.answer.value})'
                if not await uix.confirm.yesno(msg):
                    return False
                
                answer = Answer.objects.get(id=self.answer.id)
                answer.update(revoked=True, time_updated=now())
                uix.events_screen.add_event(answer)
                logger.info(f'Revoke answer input: {self.question.id}. New value: {value}')
                
            if self.question.type == 'YESNO' and value is None:
                # None отзывает предыдущее значение, не добавляя новое.
                sibling_widgets.answer = answer
                return True
            
            logger.info(f'New answer input: {self.question.id}. New value: {value}')
            
            # Проверим является ли ответ инцидентом.
            is_incident = False
            for condition, badvalue in self.question.incident_conditions.items():
                if condition == 'answer_equal_to':
                    is_incident = bool(value == badvalue)
                elif condition == 'answer_greater_than':
                    is_incident = bool(int(value) > int(badvalue))
                elif condition == 'answer_less_than':
                    is_incident = bool(int(value) < int(badvalue))
                
            answer = AnswerType.objects.create(
                question_id=self.question.id,
                question_label=self.question.label,
                rawvalue=value,
                #region='ru_78',
                #uik=55,
                is_incident=is_incident,
                region=state.region.id,
                uik=state.uik,
                role=state.role,
                time_updated=now()
            )
            
            uix.events_screen.add_event(answer)
            
            #campaigns = Campaign.objects.positional().filter(active=True, subscription='yes')
            #answer.organizations = [x.organization.id for x in campaigns]
            
            sibling_widgets.answer = answer
        #except Exception as e:
            ##uix.float_message.show('Ошибка при сохранении ответа! (ошибка отправлена разработчикам)')
            #self.show_cur_state()
            #raise e
        finally:
            sibling_widgets.status_text = 'отправляется'
            
            ## Enable previously disabled quizwidgets of same question
            #state._pending_save_questions.difference_update({self.question.id})
        
        return True


    def on_answer(self, *a):
        self.show_cur_state()
        
        self.revise_complaint_visibility()
            
        logger.debug(f"Update dependants of {self.question.label}.")
        for id in self.question.get('dependants', []):
            QuizWidget.instances.filter(question__id=id).check_visibility()
        
        
    @on('state.role')
    def revise_complaint_visibility(self):
        if self.answer.is_incident and not self.answer.revoked \
           and state.get('role') not in ('other', 'videonabl'):
            self.complaint_visible = True
        else:
            self.complaint_visible = False
        logger.debug(f'complaint_visible = {self.complaint_visible}')
                
                
    def check_limiting_questions(self):
        """
        Проверить условия для отображения этого виджета (вопроса).
        Формат {'all': [{}, {}, ...]} или {'any': [{}, {}, ...]}.
        """
        conditions = self.question.get('visible_if', {}).get('limiting_questions')
        if not conditions:
            return True
        
        logger.debug(f'checking {self.question.label} {conditions}')
        if conditions.get('all'):
            if all(self.check_condition(**x) for x in conditions.all):
                return True
        elif conditions.get('any'):
            if any(self.check_condition(**x) for x in conditions.any):
                return True
        return False
            
            
    def check_condition(self, question_id, **rules):
        """
        Проверить значение последнего ответа на заданный вопрос на соответствие заданным критериям.
        question_id - id вопроса, значение ответа на который проверяется.
        rules - критерии для проверки значения.
        rules['answer_equal_to'] - значение value которое должно точно совпадать с текущим.
        rules['answer_greater_than'] - Проверить что value больше чем заданное.
        rules['answer_less_than'] - Проверить что value меньше чем заданное.
        Вернуть False если хотя бы один критерий не выполнен или ответа нет в базе.
        """
        answer = Answer.objects.filter(question_id=question_id).order_by('time_created').last()
        #import ipdb; ipdb.sset_trace()
        #logger.debug(f'{answer}')
        if not answer:
            return False
        value = None if answer.revoked else answer.value
        
        if 'answer_equal_to' in rules:
            return rules['answer_equal_to'] == value
        if 'answer_greater_than' in rules:
            if value <= rules['answer_greater_than']:
                return False
        if 'answer_less_than' in rules:
            if value >= rules['answer_less_than']:
                return False
        return True
            
            
    @on('state.elect_flags')
    def check_visibility(self, *a):
        self.visible = bool(self.check_election_flags() and self.check_limiting_questions())
            
            
    def check_election_flags(self):
        #print(state.get('elect_flags', set()), self.question.get('elect_flags'))
        flags = self.question.get('visible_if', {}).get('elect_flags')
        if not flags:
            return True
        if set(flags) & state.get('elect_flags', set()):
            return True
        self.flags_match = False
            
            
    #def __del__(self):
        #print(f'del {self}')
        
    #def show(self):
        #self.height = 10
        #self.size_hint_y = 1
        #self.opacity = 1
        
    #def hide(self):
        #self.height = 0
        #self.size_hint_y = None
        #self.opacity = 0

    def show_cur_state(self):
        """ Показать текущий ответ в инпуте """
        raise NotImplementedError("show_cur_state must be implemented in QuizWidget subclass")
    
    def on_send_start(self, answer):
        pass
    
    def on_send_success(self, answer):
        if self.answer.id == answer.id:
            self.status_text = ''   # Отправлен последний (текущий) ответ.
        else:
            self.status_text = 'отправляется'   # Еще не все ответы отправлены.

    def on_send_error(self, answer):
        self.status_text = 'отправляется (error)'

    def on_send_fatal_error(self, answer):
        self.status_text = 'отправляется (error)'

    #def on_save_success(self, answer):
        ##logger.debug(f'{self} {answer} tik_complaint_status: {answer.tik_complaint_status}')
        #self.answer = answer


async def restore_past_answers():
    #for quizwidget in QuizWidget.instances.all():
        #await quizwidget.set_past_answers(None)
    if not (state.get('uik') and state.get('region')):
        return
    filter = Q(uik=state.uik, region=state.region.id, time_created__gt=now()-timedelta(days=2))
    answers = list(Answer.objects.filter(filter).order_by('question_id'))
    logger.info(f'Restoring {len(answers)} past answers for {state.region.name} УИК {state.uik}')
    for question, answers in groupby(answers, key=lambda x: x.question_id):
        e = sorted(answers, key=lambda x: x.time_created)
        for quizwidget in QuizWidget.instances.filter(question__id=question):
            await quizwidget.set_past_answers(e)
            await sleep(0.05)
            
