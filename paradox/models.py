   
class InputEvent(Model):
    coordinators
    timestamp
    send_status
    input_id
    input_label
    value
    alarm = BooleanField()
    country
    region
    uik
    
class Message(Model):
    channel = FK(Channel)
    sender = FK(User)
    text
    readen = Bool(default=False)
    timestamp
    time_local_received
    send_status
    inreply_to = FK('self')
    
class Channel(Model):
    id
    name
    joined = Bool(default=False)
    actual = Bool(default=True)
    coordinator = FK(Coordinator, null=True)
    campaign = FK(Campaign, null=True)
    icon_url
    icon_local
    
class ReadonlyChanel(Channel):
    
class InputEventSupportChannel(Channel):
    event = FK(InputEvent)
    
    
class Coordinator(Model):
    name
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
    active = Bool()
    fromtime = DateTimeField()
    totime = DateTimeField()
    country
    region
    mokrug
    election
    phones = TextField()  #json
    external_channels = TextField()  #json
    elect_flags = TextField()
    #channels = ManyToManyField(Channel)
    
class User(Model):
    name
    avatar
    
 
