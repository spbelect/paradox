import asyncio
import json
from os.path import join, basename
from asyncio import sleep, create_task
from datetime import datetime
from itertools import chain
from urllib.parse import urljoin

#import asks
#import trio
from app_state import state, on
from dateutil.parser import parse as dtparse
from django.db.models import Q, F
from django.utils.timezone import now
from lockorator.asyncio import lock_or_exit
from loguru import logger
#from trio import sleep
import requests_async as requests
import http3

from paradox import uix
from .models import Campaign, Coordinator, InputEvent, InputEventImage, InputEventUserComment
from . import config
from . import utils


client = http3.AsyncClient()

state.server = config.SERVER_ADDRESS
try:
    from get_server import get_server
except ImportError:
    @lock_or_exit()
    async def get_server():
        state.server = config.SERVER_ADDRESS
        #import ipdb; ipdb.sset_trace()
        #logger.debug(state.server)



def send_debug(msg):
    from requests import post
    from os.path import join
    try:
        server = state.get('server', config.SERVER_ADDRESS)
        post(join(server, 'api/v2/errors/'), json={
            'app_id': state.get('app_id', '666'),
            #'hash': md5(_traceback.encode('utf-8')).hexdigest(),
            'timestamp': datetime.utcnow().isoformat(),
            'msg': msg
        })
    except:
        pass
    
async def ping_loop():
    while True:
        try:
            return await client.get(state.server, timeout=10)
        except http3.Timeout as e:
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
        await get_server()
    except Exception as e:
        logger.info(e)
        await get_server()
    else:
        logger.info('Server connection ok.')


async def api_request(method, url, data=None):
    while True:
        if 'server' in state:
            break
        await get_server()
        await sleep(5)
        
    #import ipdb; ipdb.sset_trace()
    url = urljoin(state.server, join('/api/v2', url))
    logger.debug(url)
    try:
        #state.server = 'http://8.8.8.8'
        return await client.request(
            method, url, timeout=10,
            json=dict(data, app_id=state.app_id) if data else None
        )
    except http3.Timeout as e:
        logger.debug(repr(e))
        create_task(check_server())
        raise
    except Exception as e:
        create_task(check_server())
        
        #import ipdb; ipdb.sset_trace()
        #raise
        #logger.exception(e)
        if getattr(e, 'args', None) and isinstance(e.args[0], OSError):
            if getattr(e.args[0], 'errno', None) == 101:
                raise
        logger.debug(repr(e))
        raise
        
        
@on('state.region', 'state.country', 'state.uik', 'state.role')
@lock_or_exit()
async def send_userprofile():
    logger.debug('Sending profile.')
    fields = 'email last_name first_name phone telegram'.split()
    await sleep(1)
    while True:
        logger.debug('Sending profile loop.')
        prev = tuple(state.profile.get(x, None) for x in fields)
        if not all(prev):
            await sleep(10)
            continue
        
        try:
            response = await api_request('POST', f'userprofile/', {
                'first_name': state.profile.first_name,
                'last_name': state.profile.last_name,
                'middle_name ': state.profile.get('middle_name', None),
                'email': state.profile.email,
                'phone': state.profile.phone,
                'telegram': state.profile.telegram,
            })
        except Exception as e:
            logger.info(f'{repr(e)}')
        else:
            if response.status_code == 200:
                if prev == tuple(state.profile.get(x, None) for x in fields):
                    # Пока ожидали http ответ, профиль не изменился
                    logger.info('Profile sent.')
                    return
                else:
                    # Пока ожидали http ответ, профиль изменился, пошлем новые
                    logger.info('Profile changed, will send again.') 
            else:
                logger.info(repr(response))
                return
                #uix.sidepanel.http_error(response)
        await sleep(50)


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
            response = await api_request('POST', f'position/', {
                'uik': state.uik,
                'region': state.region.id,
                'country': state.country,
                'role': state.role,
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
        await sleep(50)


async def _put_image(image):
    try:
        response = await api_request('PUT', f'input_events/{image.event_id}/images/{image.md5}', {
            #'type': image.type,
            #'time_created': image.time_created,
            'deleted': image.deleted,
            #'filename': image.md5 + basename(image.filepath),
        })
    except Exception as e:
        image.update(send_status='put_exception')
        return
    if not response.status_code == 200:
        image.update(send_status=f'put_http_{response.status_code}')
        return
    
    image.update(send_status='sent', time_sent=now())


async def event_image_send_loop():
    while True:
        waiting = InputEventImage.objects.filter(event__time_sent__isnull=True).count()
        
        topost = Q(time_sent__isnull=True) & Q(event__time_sent__isnull=False)
        topost = InputEventImage.objects.filter(topost).exclude(deleted=True)
        
        toput = Q(time_sent__isnull=False) & Q(time_sent__lt=F('time_updated'))
        toput = InputEventImage.objects.filter(toput)
        
        logger.info(f'{topost.count()} images to create. {toput.count()} images to update. {waiting} waiting.')
        
        #logger.debug(list(topost.values_list('filepath')))
        for image in toput:
            await sleep(0.2)
            await _put_image(image)
            
        for image in topost:
            await sleep(0.2)
            try:
                response = await api_request('POST', 'upload_request/', {
                    'filename': image.md5 + basename(image.filepath),
                    'md5': image.md5,
                    'content-type': 'image/jpeg'
                })
            except Exception as e:
                logger.error(repr(e))
                image.update(send_status='req_exception')
                continue
            if not response.status_code == 200:
                logger.error(repr(response))
                image.update(send_status=f'req_http_{response.status_code}')
                continue
            
            s3params = response.json()
            try:
                response = await client.post(
                    s3params['url'], data=s3params['fields'], 
                    files={'file': open(image.filepath, 'rb')}
                )
            except Exception as e:
                logger.error(repr(e))
                image.update(send_status='upload_exception')
                continue
            if not response.status_code in (200, 201, 204):
                logger.error(repr(response))
                logger.error(response.text)
                image.update(send_status=f'upload_http_{response.status_code}')
                continue
            
            try:
                response = await api_request('POST', f'input_events/{image.event_id}/images/', {
                    'type': image.type,
                    'timestamp': image.time_created.isoformat(),
                    'deleted': image.deleted,
                    'filename': image.md5 + basename(image.filepath),
                })
            except Exception as e:
                logger.error(repr(e))
                image.update(send_status='post_exception')
                continue
            if not response.status_code == 200:
                logger.error(repr(response))
                image.update(send_status=f'post_http_{response.status_code}')
                continue
            
            image.update(send_status='sent', time_sent=now())
            #print(res.content)
            #print('ok')
        await sleep(10)
            
            
async def _put_event(event):
    try:
        response = await api_request('PUT', f'input_events/{event.id}/', {
            'revoked': event.revoked,
            'uik_complaint_status': event.uik_complaint_status,
            'tik_complaint_status': event.tik_complaint_status,
        })
    except Exception as e:
        event.update(send_status='put_exception')
        return
    if response.status_code == 404:
        # No such input
        logger.info(f'404, {response.json()}')
        event.update(send_status='sent', time_sent=now())
        return
    elif not response.status_code == 200:
        event.update(send_status=f'put_http_{response.status_code}')
        return
    
    event.update(send_status='sent', time_sent=now())


async def event_send_loop():
    while True:
        toput = InputEvent.objects.filter(time_sent__isnull=False, time_sent__lt=F('time_updated'))
        topost = InputEvent.objects.filter(time_sent__isnull=True)
        logger.info(f'{topost.count()} events to post. {toput.count()} events to put.')
        
        for event in chain(topost, toput):
            uix_inputs = uix.Input.instances.filter(input_id=event.input_id)
            uix_inputs.on_send_start(event)
            await sleep(0.1)
            
        for event in toput:
            await sleep(0.2)
            uix_inputs = uix.Input.instances.filter(input_id=event.input_id)
            await _put_event(event)
            uix_inputs.on_send_success(event)
            
        for event in topost:
            uix_inputs = uix.Input.instances.filter(input_id=event.input_id)
            try:
                response = await api_request('POST', 'input_events/', {
                    'id': event.id,
                    'input_id': event.input_id,
                    'value': event.get_value(),
                    'uik_complaint_status': event.uik_complaint_status,
                    'tik_complaint_status': event.tik_complaint_status,
                    'region': event.region,
                    'uik': event.uik,
                    'role': event.role,
                    'alarm': event.alarm,
                    'revoked': event.revoked,
                    'timestamp': event.time_created.isoformat(),
                })
            except Exception as e:
                logger.error(repr(e))
                event.update(send_status='post_exception')
                uix_inputs.on_send_error(event)
                continue
            if response.status_code == 404:
                # No such input
                logger.info(f'404, {response.json()}')
                event.update(send_status='sent', time_sent=now())
                uix_inputs.on_send_success(event)
                continue
            if not response.status_code == 201:
                logger.info(repr(response))
                event.update(send_status=f'post_http_{response.status_code}')
                uix_inputs.on_send_error(event)
                continue
            event.update(send_status='sent', time_sent=now())
            uix_inputs.on_send_success(event)
            await sleep(0.1)
        await sleep(10)
        
mock_campaigns = {
    'campaigns': {
        '8446': {
            'elections': '6b26',
            'coordinator': '724',
            'fromtime': '2018.07.22T00:00',
            'totime': '2019.12.22T00:00',
            #'channels': [
                #{'type': 'readonly', 'uuid': '51', 'name': 'НП NEWS МО Дачное', 'icon': 'http://'},
                #{'type': 'groupchat', 'uuid':'724', 'name': 'НП чат МО Дачное', 'icon': 'http://'},
            #],
            'external_channels': [{
                'type': 'tg', 'name': 'НП чат Кировский рн', 'url': 'https://t.me/mobile_kir',
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
            'url': 'https://t.me/mobile_spb_lo',
            'region': '78',
        }],
        'phones': [{'name': 'НП Коллцентр lasrjaosjrh lwjg alwj', 'number': '88129535326'}],
        #'channels': [
                #{
                    #'uuid': '7246',
                    #'type': 'readonly',
                    #'name': 'НП NEWS Спб',
                    #'region': '78',
                    #'icon': 'http://'
                #},
                #{
                    #'uuid': '886',
                    #'type': 'groupchat',
                    #'name': 'НП чат Спб',
                    #'region': '78',
                    #'icon': 'http://'
                #},
            #]
        }
    }
}
 
@uix.formlist.show_loader
@uix.coordinators.show_loader
@lock_or_exit()
@on('state.region')
async def update_campaigns():
    await sleep(2)
    while True:
        region, country = state.get('region'), state.get('country')
        logger.info(f'Updating campaigns. Region: {getattr(region, "name", None)}, country: {country}')
        if not region or not country:
            break
        data = (await recv_loop(f'regions/{region.id}/campaigns/')).json()
        #data = mock_campaigns
        
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
            election = data['elections'].get(campaign['elections'])
            logger.debug(election)
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
    campaigns = Campaign.objects.positional().current()
    logger.debug(campaigns.values())
    #uix.FormListScreen.delete_campaign_forms()
    #for campaign in campaigns:  #.filter(coordinator__subscription='yes'):
        #uix.formlist.show_campaign_forms(campaign)
    
    #if campaigns.count() == 0:
        #uix.formlist.show_no_campaign_notice()
        
    uix.coordinators.show(Coordinator.objects.filter(campaigns__in=campaigns))
    #uix.coordinators.show(Coordinator.objects.all())
    logger.debug('Update campaigns finished')
    
    
@on('state.uik')
@lock_or_exit()
async def update_elect_flags():
    await sleep(0.5)
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
    
    

        
async def recv_loop(url):
    while True:
        try:
            response = await api_request('GET', url)
        except Exception as e:
            logger.error(repr(e))
            await sleep(5)
        else:
            if response.status_code == 200:
                return response
            logger.info(repr(response))
            await sleep(5)
            
