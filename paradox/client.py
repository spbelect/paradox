import json
import trio
import asks

from app_state import state, on
from dateutil.parser import parse as dtparse
from django.db.models import Q
from lockorator.asyncio import lock_or_exit

from paradox import uix
from .models import Campaign, Coordinator, InputEvent


@on('state.region', 'state.country', 'state.uik', 'state.role')
@lock_or_exit('send_position')
async def send_position():
    await trio.sleep(10)
    while True:
        prev = (state.uik, state.region.id, state.country, state.role)
        try:
            response = await asks.post(f'{state.server}/position/', {
                'app_id': state.app_id,
                'uik': state.uik,
                'role': state.role,
                'region': state.region.id,
                'country': state.country,
            })
        except Exception as e:
            pass
        else:
            if response.status_code == 200:
                if prev == (state.uik, state.region.id, state.country, state.role):
                    # Пока ожидали http ответ, уик\регион не изменился
                    return
                #else:
                    ## Пока ожидали http ответ, уик\регион изменился, пошлем новые
                    #continue 
            #else:
                #uix.sidepanel.http_error(response)
        await trio.sleep(5)


async def event_send_loop():
    while True:
        tosend = Q(send_status__in=['pending', 'exception']) | Q(send_status__startswith='http_')
        #pending = InputEvent.objects.filter(tosend)
        for event in InputEvent.objects.filter(tosend).values():
            try:
                response = await asks.post('{state.server}/input_events/', {
                    'iid': event.input_id,
                    #'coordinators': [x.id]
                })
            except Exception as e:
                event.update(send_status='exception')
                uix.Input.instances.find(iid=iid).on_send_error(event)
                break
            if not response.status_code == 200:
                event.update(send_status=f'http_{response.status_code}')
                uix.Input.instances.find(iid=iid).on_send_error(event)
                break
            event.update(send_status='sent')
            uix.Input.instances.find(iid=iid).on_send_success(event)
        await trio.sleep(5)
        
        
async def recv_loop(url):
    while True:
        try:
            response = await asks.get('{state.server}{url}')
        except Exception as e:
            raise  # TODO
            await trio.sleep(5)
        else:
            return response
            

mock_campaigns = {
    'campaigns': {
        '8446': {
            'election': '6b26',
            'coordinator': '724',
            'fromtime': '2018.07.22T00:00',
            'totime': '2018.07.22T00:00',
            'channels': [
                {'type': 'readonly', 'uuid': '51', 'name': 'НП NEWS МО Дачное', 'icon': 'http://'},
                {'type': 'groupchat', 'uuid':'724', 'name': 'НП чат МО Дачное', 'icon': 'http://'},
            ],
            'external_channels': [{
                'type': 'tg', 'name': 'НП чат Кировский рн', 'link': 'https://t.me/mobile_kir',
            }],
            'phones': [{'name': 'НП Кировский', 'number': '88121111'}],
        },
    },
    'elections': {
        '6b26': {
            'name': 'Выборы Депутатов МО Дачное',
            'date': '2018.09.08', 
            'mokrug': '3467',
            'flags': ['otkrep', 'mestonah', 'dosrochka']
        },  
        'f674': {
            'name': 'Выборы президента'
        }},
    'coordinators': {'724':  {
        'name': 'Наблюдатели Петербурга',
        'external_channels': [{
            'type': 'tg', 
            'name': 'Общий чат СПб и ЛО', 
            'link': 'https://t.me/mobile_spb_lo',
            'region': '78',
        }],
        'phones': [{'name': 'НП Коллцентр', 'number': '88129535326'}],
        'channels': [
                {
                    'uuid': '7246',
                    'type': 'readonly',
                    'name': 'НП NEWS Спб',
                    'region': '78',
                    'icon': 'http://'
                },
                {
                    'uuid': '886',
                    'type': 'groupchat',
                    'name': 'НП чат Спб',
                    'region': '78',
                    'icon': 'http://'
                },
            ]
        }
    }
}
 
@uix.formlist.show_loader
#@uix.coordinators.show_loader
@lock_or_exit('update_campaigns')
async def update_campaigns():
    while True:
        region, country = state.region, state.country
        #data = await recv_loop(f'/region/{region}/campaigns/')
        #data = {
            #'coordinators': {'NP12345': {
                #'name': 'Наблюдатели петербурга',
                #'phones': ['555'],
                #'external_channels': ['http://t.me/spb_lo']
            #}},
            #'campaigns': {'EDG2019-26246':{
                #'election': '2019-mo-dachnoye-7272',
            #}},
            #'elections': {'2019-mo-dachnoye-7272':{
                #'region': 'ru_78',
                #'mokrug': 'mo-dachnoye',
                #'flags': 
            #}}
        #}
        data = mock_campaigns
        
        ##Channel.objects.filter(coordinator__in=data['coordinators']).update(actual=False)
                
        for id, coordinator in data['coordinators'].items():
            Coordinator.objects.update_or_create(id=id, defaults={
                'name': coordinator['name'],
                'phones': json.dumps(coordinator['phones']),
                'external_channels': json.dumps(coordinator['external_channels']),
            })
            #for channel in coordinator['channels']:
                #Channel.objects.update_or_create(id=channel['id'], {
                    #'name': channel['name'],
                    #'actual': True,
                    #'coordinator': id,
                #})
        
        for id, campaign in data['campaigns'].items():
            election = data['elections'].get(campaign['election'])
            Campaign.objects.update_or_create(id=id, defaults={
                'country': country,
                'region': election.get('region'), 
                'mokrug': election.get('mokrug'), 
                'fromtime': dtparse(campaign['fromtime']),
                'totime': dtparse(campaign['totime']),
                'coordinator_id': campaign['coordinator'],
                'elect_flags': ','.join(election['flags']),
                'phones': json.dumps(campaign['phones']),
                'external_channels': json.dumps(campaign['external_channels']),
            })
            #for channel in campaign['channels']:
                #Channel.objects.update_or_create(id=channel['id'], {
                    #'name': channel['name'],
                    #'actual': True,
                    #'campaign': id,
                    #'coordinator': campaign['coordinator']
                #})
        
        if (region, country) == (state.region, state.country):
            break  # Пока ожидали http ответ, регион не изменился, продолжим
        
        trio.sleep(5)
    
    campaigns = Campaign.objects.positional().current()
    #uix.coordinators.show(Coordinator.objects.filter(campaign__in=campaigns))
    
    #uix.FormListScreen.delete_campaign_forms()
    #for campaign in campaigns:  #.filter(coordinator__subscription='yes'):
        #uix.formlist.show_campaign_forms(campaign)
    
    #if campaigns.count() == 0:
        #uix.formlist.show_no_campaign_notice()


#async def on_subscribe(id):
    #Coordinator.objects.filter(id=id).update(subscription='subing')
    #subscribe(id)
    
    
#@uix.formlist.show_loader
#@lock_wait('coordinator_sub')   
#async def subscribe(id):
    #while True:
        #try:
            #response = await asks.post(f'{state.server}/coordinators/{id}/subscribe/')
        #except Exception as e:
            #uix.coordinators.subscribe_error(id)
        #else:
            #if response.status_code == 200:
                #break
            #uix.coordinators.subscribe_error(id)
        #trio.sleep(5)
    
    #coordinator = Coordinator.objects.get(id=id)
    #if not coordinator.subscription == 'subing':
        #return  # Пока ожидали http ответ, юзер отписался
    
    ##campaigns = 
    ##filter = Q(campaign__in=campaigns) | Q(campaign__isnull=True)
    ##Channel.objects.filter(filter, coordinator=id, actual=True)
    #coordinator.channels.filter(campaign__isnull=True, actual=True).update(joined=True)
    
    #for campaign in Campaign.objects.positional().filter(coordinator=id):
        #campaign.channels.filter(actual=True).update(joined=True)
        
        #formdata = await recv_loop(f'/campaigns/{campaign.id}/forms/')
        
        #for form in formdata:
            #for input in form['inputs']:
                #state.inputs[input['id']] = input
                    
        #if not state.forms.campaign[campaign.id] == formdata:
            #state.forms.campaign[campaign.id] = formdata
            #uix.formlist.show_campaign_forms(campaign)
        
    #Coordinator.objects.filter(id=id).update(subscription='yes')
    #uix.messages.show_channels(Channel.objects.filter(joined=True))
    #uix.coordinators.subscribe_success(id)
    
            
#async def on_unsubscribe(id):
    #Coordinator.objects.filter(id=id).update(subscription='unsubing')
    #unsubscribe(id)
    
    
#@uix.formlist.show_loader
#@lock_wait('coordinator_sub')
#async def unsubscribe(id):
    #while True:
        #try:
            #response = await asks.post(f'{state.server}/coordinators/{id}/unsubscribe/')
        #except Exception as e:
            #uix.coordinators.unsubscribe_error(id)
        #else:
            #if response.status_code == 200:
                #break
            #uix.coordinators.unsubscribe_error(id)
        #trio.sleep(5)
    
    #if not Coordinator.objects.get(id=id).subscription == 'unsubing':
        #return  # Пока ожидали http ответ, юзер подписался
    
    #for campaign in Campaign.objects.filter(coordinator=id):
        #uix.formlist.remove_campaign_forms(campaign.id)
    #Coordinator.objects.filter(id=id).update(subscription='no')
    
    
