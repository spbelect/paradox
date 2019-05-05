import asyncio
import json
from asyncio import sleep, create_task
from itertools import chain
from urllib.parse import urljoin

#import asks
#import trio
from app_state import state, on
from dateutil.parser import parse as dtparse
from django.db.models import Q, F
from lockorator.asyncio import lock_or_exit
from loguru import logger
#from trio import sleep
import requests_async as requests

from paradox import uix
from .models import Campaign, Coordinator, InputEvent, InputEventImage, InputEventUserComment
from . import config
from . import utils


try:
    from get_server import get_server
except ImportError:
    def get_server():
        state.server = config.SERVER_ADDRESS


async def ping_loop():
    while True:
        try:
            return await requests.get(urljon(state.server, '/ping'), timeout=10)
        except requests.Timeout as e:
            pass
        except Exception as e:
            raise
        else:
            return
        await sleep(5)
    
@lock_or_exit()
async def check_server():
    logger.info('Checking server.')
    try:
        await asyncio.wait_for(ping_loop(), timeout=0.5*60)
    except asyncio.TimeoutError:
        logger.info('Server ping timeout.')
        get_server()
    except Exception as e:
        logger.info(e)
    else:
        logger.info('Server connection ok.')


async def api_request(method, url, data):
    try:
        #state.server = 'http://8.8.8.8'
        return await requests.request(method, urljoin(state.server, '/api/v1/', url), data=data, timeout=10)
    except requests.Timeout as e:
        logger.debug(repr(e))
        create_task(check_server())
        raise
    except Exception as e:
        #logger.exception(e)
        if getattr(e, 'args', None) and isinstance(e.args[0], OSError):
            if getattr(e.args[0], 'errno', None) == 101:
                raise
        logger.debug(repr(e))
        raise
        
        
@on('state.region', 'state.country', 'state.uik', 'state.role')
@lock_or_exit()
async def send_position():
    await sleep(1)
    while True:
        logger.debug('Sending position.')
        try:
            prev = (state.uik, state.region.id, state.country, state.role)
        except AttributeError:
            return
        try:
            response = await api_request('POST', f'/position/', {
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
                    logger.info('Position sent.')
                    return
                #else:
                    ## Пока ожидали http ответ, уик\регион изменился, пошлем новые
                    #continue 
            else:
                logger.info(repr(response))
                return
                #uix.sidepanel.http_error(response)
        await sleep(5)


async def event_image_send_loop():
    while True:
        tosend = InputEventImage.objects.filter(event__time_sent__isnull=False)\
                                        .exclude(send_status='sent')
        logger.info(f'{tosend.count()} images to send.')
        for image in tosend:
            #md5 = paradox.utils.md5_file(image.filepath)
            try:
                response = await api_request('POST', '/upload_request/', {
                    'filename': image.md5 + basename(image.filepath),
                    'md5': image.md5,
                    'content-type': 'image/jpeg'
                })
            except Exception as e:
                image.update(send_status='req_exception')
                continue
            if not response.status_code == 200:
                image.update(send_status=f'req_http_{response.status_code}')
                continue
            
            response = response.json()
            try:
                response = await requests.post(response['url'], data=response['fields'], 
                        files={'file': ('unused.jpeg', open(image.filepath, 'rb'))})
            except Exception as e:
                image.update(send_status='upload_exception')
                continue
            if not response.status_code == 200:
                image.update(send_status=f'upload_http_{response.status_code}')
                continue
            
            try:
                response = await api_request('POST', '/upload_finalize/', {
                    'event_id': image.event_id,
                    'type': image.type,
                    'timestamp': image.timestamp,
                    'filename': image.md5 + basename(image.filepath),
                })
            except Exception as e:
                image.update(send_status='fin_exception')
                continue
            if not response.status_code == 200:
                image.update(send_status=f'fin_http_{response.status_code}')
                continue
            
            image.update(send_status='sent')
            #print(res.content)
            #print('ok')
        await sleep(5)
            
async def event_send_loop():
    while True:
        tosend = Q(time_sent__isnull=True) | Q(time_sent__lt=F('time_updated'))
        tosend = InputEvent.objects.filter(tosend)
        logger.info(f'{tosend.count()} events to send.')
        for event in tosend:
            try:
                response = await api_request('POST', '/input_events/', {
                    'iid': event.input_id,
                })
            except Exception as e:
                event.update(send_status='exception')
                #print('err', event.input_id)
                for input in uix.Input.instances.filter(input_id=event.input_id):
                    input.on_send_error(event)
                continue
            if not response.status_code == 200:
                event.update(send_status=f'http_{response.status_code}')
                for input in uix.Input.instances.filter(input_id=event.input_id):
                    input.on_send_error(event)
                continue
            event.update(send_status='sent')
            for input in uix.Input.instances.filter(input_id=event.input_id).on_send_success(event):
                input.on_send_success(event)
        await sleep(5)
        
        
async def recv_loop(url):
    while True:
        try:
            response = await api_request('GET', url)
        except Exception as e:
            raise  # TODO
            await sleep(5)
        else:
            return response
            

mock_campaigns = {
    'campaigns': {
        '8446': {
            'election': '6b26',
            'coordinator': '724',
            'fromtime': '2018.07.22T00:00',
            'totime': '2019.12.22T00:00',
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
            'mokrug': 3467,
            'flags': ['otkrep', 'mestonah', 'dosrochka'],
            'region': 'ru_78'
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
@lock_or_exit()
@on('state.region')
async def update_campaigns():
    while True:
        region, country = state.get('region'), state.get('country')
        logger.info(f'region: {getattr(region, "name", None)}, country: {country}')
        if not region or not country:
            break
        #data = await recv_loop(f'/region/{region}/campaigns/')
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
        
        await sleep(5)
    
    create_task(update_elect_flags())
    #campaigns = Campaign.objects.positional().current()
    #uix.FormListScreen.delete_campaign_forms()
    #for campaign in campaigns:  #.filter(coordinator__subscription='yes'):
        #uix.formlist.show_campaign_forms(campaign)
    
    #if campaigns.count() == 0:
        #uix.formlist.show_no_campaign_notice()
        

    #uix.coordinators.show(Coordinator.objects.filter(campaign__in=campaigns))
    
@on('state.uik')
@lock_or_exit()
async def update_elect_flags():
    await sleep(5)
    campaigns = Campaign.objects.positional().current().filter(elect_flags__isnull=False)
    state.elect_flags = set(chain(*(x.elect_flags.split(',') for x in campaigns)))
    logger.debug(f'{campaigns.count()} active campaigns.')
    logger.debug(f'Election flags: {list(state.elect_flags)}')
    
    
    
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
    
    
