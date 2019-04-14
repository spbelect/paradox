
from django.db.models import (
    ForeignKey, UUIDField, DateTimeField, TextField, CharField, IntegerField,
    BooleanField, ManyToManyField, SET_NULL, CASCADE, PROTECT, Manager)
from django.utils.timezone import now

from django import db


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
    #coordinators
    timestamp = DateTimeField()
    send_status = CharField(max_length=20)  # sent/pending/exception/http_{NNN}
    input_id = CharField(max_length=40)  # UUID
    input_label = TextField()
    value = TextField()
    alarm = BooleanField()
    country = IntegerField()
    region = IntegerField()
    uik = IntegerField()
    COMPLAINT_STATUS = [
        ('none', 'не подавалась'),
        ('refuse_to_accept', 'отказ принять жалобу'),
        ('refuse_to_resolve', 'отказ рассмотрения жалобы'),
        ('waiting_reply', 'ожидание решения комиссии'),
        ('got_unfair_reply', 'получено неудовлетворительное решение'),
        ('got_fair_reply', 'получено удовлетворительное решение'),
    ]
    complaint_status = CharField(max_length=20, choices=COMPLAINT_STATUS)
    
    
class Message(Model):
    channel = FK(Channel)
    sender = FK(User)
    text = TextField()
    readen = BooleanField(default=False)
    timestamp = DateTimeField()
    time_local_received = DateTimeField()
    send_status = CharField(max_length=20)  # 'sent', 'pending', 'exception', 'http_{NNN}'
    inreply_to = FK('self')
    
    
class Channel(Model):
    id = CharField(max_length=40)  # UUID
    name = TextField()
    joined = Bool(default=False)
    actual = Bool(default=True)
    coordinator = FK(Coordinator, null=True)
    campaign = FK(Campaign, null=True)
    icon_url = TextField()
    icon_local = TextField()
    
    class Meta:
        abstract=True
    
    
class ReadonlyChanel(Channel):
    pass
    
    
class InputEventSupportChannel(Channel):
    event = FK(InputEvent)
    
    
class Coordinator(Model):
    name = TextField()
    phones = TextField()  #json
    external_channels = TextField()  #json
    
    
class CampaignQuerySet(models.QuerySet):
    def positional(self):
        filter = Q(region__isnull=True)  # federal
        filter |= Q(region=state.region, mokrug__isnull=True)  # regional
        if state.mokrug:
            filter |= Q(mokrug=state.mokrug)
        return self.filter(filter)

    
class Campaign(Model):
    objects = CampaignQuerySet.as_manager()
    
    coordinator = FK(Coordinator)
    subscription = CharField() # yes no subing unsubing
    active = BooleanField()  # shortcut for filtering current timerange
    fromtime = DateTimeField()
    totime = DateTimeField()
    country = IntegerField()
    region = IntegerField()
    mokrug
    election
    phones = TextField()  #json
    external_channels = TextField()  #json
    elect_flags = TextField()
    #channels = ManyToManyField(Channel)
    
class User(Model):
    name = TextField()
    avatar
    
class InputEventImage(Model):
    event = FK(InputEvent)
    TYPES = [
        ('uik_complaint', 'Подаваемые в УИК жалобы'),
        ('uik_reply', 'Ответы, решения от УИК'),
        ('tik_complaint', 'Подаваемые в ТИК жалобы'),
        ('tik_reply', 'Ответы, решения от ТИК'),
    ]
    type = CharField(max_length=20, choices=TYPES)
    file = TextField()
    send_status = CharField(max_length=20)  # sent/pending/exception/http_{NNN}
