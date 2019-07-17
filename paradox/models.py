
from datetime import datetime
from uuid import uuid4

from django.db.models import (
    ForeignKey, UUIDField, DateTimeField, TextField, CharField, IntegerField,
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
        >>> user.save()

        """
        for attr, val in kwargs.items():
            setattr(self, attr, val)

        self.save()

def FK(*args, **kw):
    params = dict(
        on_delete=SET_NULL,
        related_name='+',
        null=True,
        blank=True
    )
    return ForeignKey(*args, **dict(params, **kw))


class InputEvent(Model):
    id = CharField(max_length=40, default=uuid4, primary_key=True)
    
    time_created = DateTimeField(default=now)
    send_status = CharField(max_length=40, default='pending')  # sent/pending/exception/http_{NNN}
    time_sent = DateTimeField(null=True)
    time_updated = DateTimeField()
    revoked = BooleanField(default=False)
    
    input_id = CharField(max_length=40)  # UUID
    input_label = TextField()
    alarm = BooleanField()
    role = CharField(max_length=15)
    country = CharField(max_length=2)
    region = CharField(max_length=6)
    uik = IntegerField()
    COMPLAINT_STATUS = [
        ('none', 'не подавалась'),
        ('refuse_to_accept', 'отказ принять жалобу'),
        ('refuse_to_resolve', 'отказ рассмотрения жалобы'),
        ('waiting_reply', 'ожидание решения комиссии'),
        ('got_unfair_reply', 'получено неудовлетворительное решение'),
        ('got_fair_reply', 'получено удовлетворительное решение'),
    ]
    uik_complaint_status = CharField(max_length=20, choices=COMPLAINT_STATUS, default='none')
    tik_complaint_status = CharField(max_length=20, choices=COMPLAINT_STATUS, default='none')
    
    def get_value(self):
        if hasattr(self, 'integerinputevent'):
            return self.integerinputevent.value
        if hasattr(self, 'boolinputevent'):
            return self.boolinputevent.value
    
class IntegerInputEvent(InputEvent):
    value = IntegerField(null=True)
    
class BoolInputEvent(InputEvent):
    value = BooleanField(null=True)
    
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
    #coordinator = FK(Coordinator, null=True)
    #campaign = FK(Campaign, null=True)
    #icon_url = TextField()
    #icon_local = TextField()
    
    #class Meta:
        #abstract=True
    
    
#class ReadonlyChanel(Channel):
    #pass
    
    
#class InputEventSupportChannel(Channel):
    #event = FK(InputEvent)
    
    
class Coordinator(Model):
    id = CharField(primary_key=True, max_length=40)  # UUID
    name = TextField()
    phones = TextField()  #json
    external_channels = TextField()  #json
    
    
class CampaignQuerySet(QuerySet):
    def positional(self):
        filter = Q(region__isnull=True)  # federal
        if state.get('region'):
            filter |= Q(region=state.region.id, mokrug__isnull=True)  # regional
        if state.get('mokrug'):
            filter |= Q(mokrug=state.mokrug.id)
        return self.filter(filter)

    def current(self):
        now = datetime.now().astimezone()
        return self.filter(fromtime__lt=now, totime__gt=now)
    
    
class Campaign(Model):
    objects = CampaignQuerySet.as_manager()
    
    id = CharField(primary_key=True, max_length=40)  # UUID
    coordinator = FK(Coordinator)
    #subscription = CharField() # yes/no/subing/unsubing
    #active = BooleanField()  # shortcut for filtering current timerange
    fromtime = DateTimeField()
    totime = DateTimeField()
    country = CharField(max_length=2)
    region = CharField(max_length=6, null=True)
    mokrug = IntegerField(null=True) # Муниципльный округ
    #election
    phones = TextField()  #json
    external_channels = TextField()  #json
    elect_flags = TextField()
    #channels = ManyToManyField(Channel)
    
#class User(Model):
    #name = TextField()
    #avatar
    
    

class InputEventUserComment(Model):
    event = FK(InputEvent)
    time_created = DateTimeField()
    text = TextField()
    send_status = CharField(max_length=20, default='pending') 
    
    class Meta:
        ordering = ('time_created',)
        
        
class InputEventImage(Model):
    
    #uuid = CharField(primary_key=True, default=uuid4, max_length=40)  # UUID
    time_sent = DateTimeField(null=True)
    time_updated = DateTimeField(default=now)
    
    deleted = BooleanField(default=False)
    
    event = FK(InputEvent, related_name='images')
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
        
        from paradox import uix
        self.md5 = paradox.utils.md5_file(self.filepath)
        result = super().save(*a,**kw)
         #= uix.imagepicker.instances.filter(id=self.uuid)
        #if self.send_status == 'sent':
            
        return result
