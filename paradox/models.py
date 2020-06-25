
from datetime import datetime, timedelta
from uuid import uuid4

from django.db.models import (
    ForeignKey, UUIDField, DateTimeField, DateField, TextField, CharField, IntegerField,
    BooleanField, ManyToManyField, SET_NULL, CASCADE, PROTECT, Manager, QuerySet, Q)
from django.utils.timezone import now
from django import db

from app_state import state
import paradox


class Model(db.models.Model):
    class Meta:
        abstract = True

    def update(self, **kwargs):
        """
        Use this method to update and save model instance in single call:

        >>> user.update(email='user@example.com', last_name='Bob')

        is a shortcut for

        >>> user.email = 'user@example.com'
        >>> user.last_name = 'Bob'
        >>> user.save(update_fields=['email', 'last_name'])

        """
        #self2 = self.__class__.objects.get(pk=self.pk)
        for attr, val in kwargs.items():
            #setattr(self2, attr, val)
            setattr(self, attr, val)

        self.save(update_fields=kwargs)

def FK(model, related_name, *args, **kw):
    params = dict(
        on_delete=SET_NULL,
        related_name=related_name,
        null=True,
        blank=True
    )
    return ForeignKey(model, *args, **dict(params, **kw))


class Answer(Model):
    id = CharField(max_length=40, default=uuid4, primary_key=True)
    
    time_created = DateTimeField(default=now)
    
    # sent/pending/post_exception/post_http_{NNN}/patch_exception/patch_http_{NNN}
    send_status = CharField(max_length=40, default='pending')  
    
    time_sent = DateTimeField(null=True)
    time_updated = DateTimeField()
    revoked = BooleanField(default=False)
    refuse_person = TextField(null=True)  # Кто отказал принять жалобу
    
    question_id = CharField(max_length=40)  # UUID
    question_label = TextField()
    is_incident = BooleanField()
    role = CharField(max_length=15)
    country = CharField(max_length=2)
    region = CharField(max_length=6)
    uik = IntegerField()
    UIK_COMPLAINT_STATUS = [
        ('none', 'не подавалась'),
        ('refuse_to_accept', 'отказ принять жалобу'),
        ('refuse_to_resolve', 'отказ рассмотрения жалобы'),
        ('refuse_to_copy_reply', 'отказ выдать копию решения'),
        ('waiting_reply', 'ожидание решения комиссии'),
        ('got_unfair_reply', 'получено неудовлетворительное решение'),
        ('got_fair_reply', 'получено удовлетворительное решение'),
    ]
    TIK_COMPLAINT_STATUS = [
        ('none', 'не подавалась'),
        ('sending_to_moderator', 'отправляется модератору'),
        ('moderating', 'ожидает модерации'),
        ('denied', 'отклонено'),  # TODO - мы не получаем дальнейший статус от сервера.
        ('email_sent', 'email отправлен'),  # TODO - мы не получаем дальнейший статус от сервера.
    ]
    uik_complaint_status = CharField(max_length=30, choices=UIK_COMPLAINT_STATUS, default='none')
    tik_complaint_status = CharField(max_length=30, choices=TIK_COMPLAINT_STATUS, default='none')
    tik_complaint_text = TextField(null=True)
    
    @property
    def question(self):
        return state.questions.get(self.question_id, {})
    
    @property
    def value(self):
        if hasattr(self, 'integeranswer'):
            return self.integeranswer.rawvalue
        if hasattr(self, 'boolanswer'):
            return self.boolanswer.rawvalue
        
    @property
    def humanized_value(self):
        if hasattr(self, 'integeranswer'):
            return self.integeranswer.rawvalue
        if hasattr(self, 'boolanswer'):
            return 'Да' if self.boolanswer.rawvalue else 'Нет'
    
    def __eq__(self, other):
        # Default django model only checks if pk are equal. We also need to check if value and 
        # revoked fields are equal, so that QuizWidget.answer property change is dispatched when 
        # answer.value or answer.revoked is changed.
        return super().__eq__(other) and self.value == other.value and self.revoked == other.revoked
    
    def update(self, **kw):
        if kw.get('send_status') == 'sent' and self.tik_complaint_status == 'sending_to_moderator':
            kw['tik_complaint_status'] = 'moderating'
        super().update(**kw)
            
class IntegerAnswer(Answer):
    rawvalue = IntegerField(null=True)
    
class BoolAnswer(Answer):
    rawvalue = BooleanField(null=True)
    
    
#class Message(Model):
    #channel = FK(Channel)
    #sender = FK(User)
    #text = TextField()
    #readen = BooleanField(default=False)
    #time_created = DateTimeField()
    #time_local_received = DateTimeField()
    #send_status = CharField(max_length=20)  # 'sent', 'pending', 'exception', 'http_{NNN}'
    #inreply_to = FK('self')
    
    
#class Channel(Model):
    #id = CharField(max_length=40)  # UUID
    #name = TextField()
    #joined = Bool(default=False)
    #actual = Bool(default=True)
    #coordinator = FK(Organization, null=True)
    #campaign = FK(Campaign, null=True)
    #icon_url = TextField()
    #icon_local = TextField()
    
    #class Meta:
        #abstract=True
    
    
#class ReadonlyChanel(Channel):
    #pass
    
    
#class AnswerSupportChannel(Channel):
    #answer = FK(Answer)
    
    
class Organization(Model):
    id = CharField(primary_key=True, max_length=40)  # UUID
    name = TextField()
    contacts = TextField()  #json
    
    
class CampaignQuerySet(QuerySet):
    def positional(self):
        filter = Q(region__isnull=True)  # federal
        if state.region.id:
            filter |= Q(region=state.region.id, munokrug__isnull=True)  # regional
        if state.munokrug:
            filter |= Q(munokrug=state.munokrug.id)
        return self.filter(filter)

    def current(self):
        now = datetime.now().astimezone()
        #return self.filter(fromtime__lt=now, totime__gt=now)
    
        return self.filter(
            vote_date__gt = now,
            vote_date__lt = now + timedelta(days=60)
        )
    
    
class Campaign(Model):
    objects = CampaignQuerySet.as_manager()
    
    id = CharField(primary_key=True, max_length=40)  # UUID
    coordinator = FK(Organization, 'campaigns')
    #subscription = CharField() # yes/no/subing/unsubing
    #active = BooleanField()  # shortcut for filtering current timerange
    #fromtime = DateTimeField()
    #totime = DateTimeField()
    vote_date = DateField()
    country = CharField(max_length=2)
    region = CharField(max_length=6, null=True)
    munokrug = CharField(max_length=40, null=True)  # UUID Муниципльного округа
    election_name = TextField(null=True)
    contacts = TextField()  #json
    elect_flags = TextField()
    #channels = ManyToManyField(Channel)
    
#class User(Model):
    #name = TextField()
    #avatar
    
    

class AnswerUserComment(Model):
    answer = FK(Answer, 'comments')
    time_created = DateTimeField()
    text = TextField()
    send_status = CharField(max_length=20, default='pending') 
    
    class Meta:
        ordering = ('time_created',)
        
        
class AnswerImage(Model):
    
    #uuid = CharField(primary_key=True, default=uuid4, max_length=40)  # UUID
    time_sent = DateTimeField(null=True)
    time_updated = DateTimeField(default=now)
    
    deleted = BooleanField(default=False)
    
    answer = FK(Answer, 'images')
    TYPES = [
        ('uik_complaint', 'Подаваемые в УИК жалобы'),
        ('uik_reply', 'Ответы, решения от УИК'),
        ('tik_complaint', 'Подаваемые в ТИК жалобы'),
        ('tik_reply', 'Ответы, решения от ТИК'),
    ]
    type = CharField(max_length=20, choices=TYPES)
    md5 = CharField(max_length=32)
    filepath = TextField()
    send_status = CharField(max_length=40, default='pending') 
    time_created = DateTimeField(default=now)
    
    class Meta:
        ordering = ('time_created',)
        
    def save(self, *a, **kw):
        self.md5 = paradox.utils.md5_file(self.filepath)
        super().save(*a,**kw)
