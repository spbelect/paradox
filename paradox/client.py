import asyncio
import json
from os.path import join, basename
from asyncio import sleep, create_task
from datetime import datetime
from itertools import chain, cycle
from urllib.parse import urljoin

#import asks
#import trio
from app_state import state, on
from dateutil.parser import parse as dtparse
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q, F
from django.utils.timezone import now
from lockorator.asyncio import lock_or_exit
from loguru import logger
#from trio import sleep
import httpx

from paradox import uix
from paradox.uix import newversion_dialog
from .models import Campaign, Coordinator, Answer, AnswerImage, AnswerUserComment
from . import config
from . import utils

#class on:
    #def __init__(*a):
        #pass
    
    #def __call__(self, f):
        #return f


client = httpx.AsyncClient()

state.server = config.SERVER_ADDRESS
SERVER_GISTS = cycle(config.SERVER_GISTS) if config.SERVER_GISTS else None

try:
    from get_server import get_server
except ImportError:
    @lock_or_exit()
    async def get_server():
        if not SERVER_GISTS:
            state.server = config.SERVER_ADDRESS
            state._server_ping_success.clear()
            create_task(check_servers())
            return
        
        for gist in SERVER_GISTS:
            try:
                response = await client.get(gist, timeout=25)
            except:
                await sleep(2)
                continue
            if response.status_code != 200:
                await sleep(2)
                continue
            state.server = response.text.strip()
            #logger.debug(state.server)
            state._server_ping_success.clear()
            create_task(check_servers())
            return
            
        #import ipdb; ipdb.sset_trace()


async def check_new_version_loop():
    while True:
        try:
            response = await client.get(config.CHANGELOG_URL, timeout=25)
        except:
            await sleep(2)
            continue
        if response.status_code != 200:
            await sleep(2)
            continue
        #import ipdb; ipdb.sset_trace()
        
        changelog = response.content.decode('utf8').strip()
        vstring = 'Версия %s' % config.version[0:3]
        #import ipdb; ipdb.sset_trace()
        if vstring in changelog:
            try:
                before, after = changelog.split(vstring)
        
                new = '\n'.join(before.split('\n')[4:]).strip()  # skip first 4 lines of the file
                if new:
                    uix.newversion_dialog.show_new_version_dialog(new)
            except Exception as e:
                logger.error(repr(e))
            
        await sleep(10*60)


def send_debug(msg):
    return
    from requests import post
    from os.path import join
    try:
        server = state.get('server', config.SERVER_ADDRESS)
        post(join(server, 'api/v2/errors/'), timeout=15, json={
            'app_id': state.get('app_id', '666'),
            #'hash': md5(_traceback.encode('utf-8')).hexdigest(),
            'timestamp': datetime.utcnow().isoformat(),
            'msg': msg
        })
    except:
        pass
    

async def server_ping_success():
    if not state._server_ping_success:
        state._server_ping_success = asyncio.Event()
        state._server_ping_success.set()  # Assume success on app start.
    return await state._server_ping_success.wait()
    
    
async def ping_loop():
    """ Бесконечный цикл. Запускается и останавливается в check_servers() """
    state._server_ping_success.clear()
    while True:
        try:
            return await client.get(state.server, timeout=15)
        except httpx.Timeout as e:
            pass
        except ConnectionRefusedError as e:
            # Сеть недоступна.
            logger.debug(repr(e))
        except Exception as e:
            raise
        else:
            state._server_ping_success.set()
            return
        await sleep(5)
    
@lock_or_exit()
async def check_servers():
    """
    Запустить ping_loop(), если не отвечает за 3 минуты, остановить ping_loop(),
    и изменить state.server на следующий.
    """
    while not state.server:
        # state.server должен быть иницализирован в main.on_start()
        await sleep(5)
    
    logger.info('Checking server.')
    try:
        await asyncio.wait_for(ping_loop(), timeout=3*60)
    except asyncio.TimeoutError:
        logger.info('Server ping timeout.')
        await get_server()
    except Exception as e:
        logger.info(e)
        await get_server()
    else:
        logger.info('Server connection ok.')


async def api_request(method, url, data=None, timeout=15):
    while not state.server:
        # state.server должен быть иницализирован в main.on_start()
        await sleep(5)
    
    await server_ping_success()
        
    url = urljoin(state.server, urljoin('/api/v2', url))
    logger.debug(f'{method} {url}')
    try:
        #state.server = 'http://8.8.8.8'
        return await client.request(
            method, url, timeout=timeout,
            json=dict(data, app_id=state.app_id) if data else None
        )
    except httpx.Timeout as e:
        logger.debug(repr(e))
        create_task(check_servers())
        raise
    except Exception as e:
        create_task(check_servers())
        
        #import ipdb; ipdb.sset_trace()
        #raise
        #logger.exception(e)
        if getattr(e, 'args', None) and isinstance(e.args[0], OSError):
            if getattr(e.args[0], 'errno', None) == 101:
                raise
        logger.debug(repr(e))
        raise
        
        
@on('state.profile')
@lock_or_exit()
async def send_userprofile():
    if not state.get('profile', None):
        return
    logger.debug('Sending profile.')
    fields = 'email last_name first_name phone'.split()
    await sleep(1)
    while True:
        logger.debug('Sending profile loop.')
        prev = tuple(state.profile.get(x, None) for x in fields)
        if not all(prev):
            logger.debug(f'Waiting for full profile: {dict(zip(fields, prev))}')
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
            
            if getattr(state, '_raise_all', None):
                raise e
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
        logger.debug('Sending position loop.')
        try:
            prev = (state.uik, state.region.id, state.country, state.role)
        except AttributeError as e:
            logger.debug(repr(e))
            return
        try:
            response = await api_request('POST', f'position/', {
                'uik': state.uik,
                'region': state.region.id,
                'country': state.country,
                'role': state.role,
            })
        except Exception as e:
            if getattr(state, '_raise_all', None):
                raise e
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


def get_throttle_delay():
    vote_dates = Campaign.objects.positional().current().values_list('vote_date', flat=True)
    if now().date() in list(vote_dates):
        return 5
    else:
        return 0.1
        
        
async def _put_image(image):
    try:
        response = await api_request('PUT', f'quiz_answers/{image.answer_id}/images/{image.md5}', {
            #'type': image.type,
            #'time_created': image.time_created,
            'deleted': image.deleted,
            #'filename': image.md5 + basename(image.filepath),
        })
    except Exception as e:
        image.update(send_status='put_exception')
        if getattr(state, '_raise_all', None):
            raise e
        return
    if not response.status_code == 200:
        image.update(send_status=f'put_http_{response.status_code}')
        return
    
    image.update(send_status='sent', time_sent=now())


async def answer_image_send_loop():
    while True:
        waiting_answer = AnswerImage.objects.filter(answer__time_sent__isnull=True).count()
        
        topost = Q(time_sent__isnull=True) & Q(answer__time_sent__isnull=False)
        topost = AnswerImage.objects.filter(topost).exclude(deleted=True)
        
        toput = Q(time_sent__isnull=False) & Q(time_sent__lt=F('time_updated'))
        toput = AnswerImage.objects.filter(toput)
        
        logger.info(
            f'{topost.count()} images to post now. {toput.count()} images to put.'
            f' {waiting_answer} waiting for answer to be sent first.'
        )
        
        throttle_delay = get_throttle_delay()
        
        for image in toput:
            await _put_image(image)
            await sleep(throttle_delay)
            
        for image in topost:
            await sleep(throttle_delay)
            try:
                response = await api_request('POST', 'upload_request/', {
                    'filename': image.md5 + basename(image.filepath),
                    'md5': image.md5,
                    'content-type': 'image/jpeg'
                })
            except Exception as e:
                logger.error(repr(e))
                image.update(send_status='req_exception')
                if getattr(state, '_raise_all', None):
                    raise e
                continue
            if not response.status_code == 200:
                logger.error(repr(response))
                image.update(send_status=f'req_http_{response.status_code}')
                continue
            
            s3params = response.json()
            try:
                response = await client.post(
                    s3params['url'], data=s3params['fields'], 
                    files={'file': open(image.filepath, 'rb')},
                    timeout=3*60
                )
            except Exception as e:
                logger.error(repr(e))
                image.update(send_status='upload_exception')
                if getattr(state, '_raise_all', None):
                    raise e
                continue
            if not response.status_code in (200, 201, 204):
                logger.error(repr(response))
                logger.error(response.text)
                image.update(send_status=f'upload_http_{response.status_code}')
                continue
            
            try:
                response = await api_request('POST', f'quiz_answers/{image.answer_id}/images/', {
                    'type': image.type,
                    'timestamp': image.time_created.isoformat(),
                    'deleted': image.deleted,
                    'filename': image.md5 + basename(image.filepath),
                })
            except Exception as e:
                logger.error(repr(e))
                image.update(send_status='post_exception')
                if getattr(state, '_raise_all', None):
                    raise e
                continue
            if not response.status_code == 200:
                logger.error(repr(response))
                image.update(send_status=f'post_http_{response.status_code}')
                continue
            
            image.update(send_status='sent', time_sent=now())
            #print(res.content)
            #print('ok')
        await sleep(10)
            
            
async def _put_answer(answer):
    """ Return True on success """
    try:
        response = await api_request('PUT', f'quiz_answers/{answer.id}/', {
            'revoked': answer.revoked,
            'uik_complaint_status': answer.uik_complaint_status,
            'tik_complaint_status': answer.tik_complaint_status,
            'tik_complaint_text': answer.tik_complaint_text,
        })
    except Exception as e:
        answer.update(send_status='put_exception')
        if getattr(state, '_raise_all', None):
            raise e
        return False
    if response.status_code == 404:
        # На сервере нет такого вопроса или ответа.
        #  Если нет такого вопроса - вероятно на сервере удалили старый вопрос. В идеале на сервере 
        # вопросы удаляться совсем не должны, а только исключаться из анкеты. Но пока идет активная
        # разработка, и бывает что вопросы удаляются.
        #  Если нет такого ответа - возможно на сервере удалили ответы после того как юзер его 
        # отправил.
        #  Скорее всего это неисправимые ошибки на сервере, так что помечаем ответ как успешно
        # отправленный, чтобы больше не пытаться.
        logger.info(f'404, {response!r} {response.json()}')
        answer.update(send_status='sent', time_sent=now())
        return True
    elif not response.status_code == 200:
        try:
            logger.info(f'{response!r} {response.json()}')
        except:
            logger.info(repr(response))
        answer.update(send_status=f'put_http_{response.status_code}')
        return
    
    extra = {}
    if answer.tik_complaint_status == 'request_pending':
        extra = {'tik_complaint_status': 'request_sent'}
    answer.update(send_status='sent', time_sent=now(), **extra)


async def answer_send_loop():
    while True:
        # Ответы которые пользователь обновил после того как они были отправлены. (напр. статус жалобы)
        toput = Answer.objects.filter(time_sent__isnull=False, time_sent__lt=F('time_updated'))
        # Еще не отправленные ответы.
        topost = Answer.objects.filter(time_sent__isnull=True)
        
        logger.info(f'{topost.count()} answers to post. {toput.count()} answers to put.')
        
        throttle_delay = get_throttle_delay()
            
        for answer in chain(topost, toput):
            quizwidgets = uix.QuizWidget.instances.filter(question__id=answer.question_id)
            quizwidgets.on_send_start(answer)
            await sleep(throttle_delay)
            
        for answer in toput:
            quizwidgets = uix.QuizWidget.instances.filter(question__id=answer.question_id)
            if await _put_answer(answer):
                quizwidgets.on_send_success(answer)
            else:
                quizwidgets.on_send_error(answer)
            await sleep(throttle_delay)
            
        for answer in topost:
            quizwidgets = uix.QuizWidget.instances.filter(question__id=answer.question_id)
            try:
                response = await api_request('POST', 'quiz_answers/', {
                    'id': answer.id,
                    'question_id': answer.question_id,
                    'value': answer.value,
                    'uik_complaint_status': answer.uik_complaint_status,
                    'tik_complaint_status': answer.tik_complaint_status,
                    'tik_complaint_text': answer.tik_complaint_text,
                    'region': answer.region,
                    'uik': answer.uik,
                    'role': answer.role,
                    'is_incident': answer.is_incident,
                    'revoked': answer.revoked,
                    'timestamp': answer.time_created.isoformat(),
                })
            except Exception as e:
                logger.error(repr(e))
                answer.update(send_status='post_exception')
                quizwidgets.on_send_error(answer)
                #print(state.get('_raise_all'))
                if getattr(state, '_raise_all', None):
                    raise e
                await sleep(throttle_delay)
                continue
            
            if response.status_code == 404:
                # No such question
                logger.info(f'404, {response.json()}')
                answer.update(send_status='sent', time_sent=now())
                quizwidgets.on_send_success(answer)
            elif not response.status_code == 201:
                logger.info(repr(response))
                answer.update(send_status=f'post_http_{response.status_code}')
                quizwidgets.on_send_error(answer)
            else:
                answer.update(send_status='sent', time_sent=now())
                quizwidgets.on_send_success(answer)
            await sleep(throttle_delay)
        await sleep(10)
        
        
mock_campaigns = {
    'campaigns': {
        '8446': {
            'election': '6b26',
            'coordinator': '724',
            'fromtime': '2018.07.22T00:00',
            'totime': '2059.12.22T00:00',
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
            'munokrug': '6ab3-d1c23',
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
 
@on('state.region')
@lock_or_exit()
@uix.formlist.show_loader
@uix.coordinators.show_loader
async def update_campaigns():
    await sleep(2)
    while True:
        region, country = state.get('region'), state.get('country')
        logger.info(f'Updating campaigns. Region: {getattr(region, "name", None)}, country: {country}')
        if not region or not country:
            break
        #data = (await recv_loop(f'{country}/regions/{region.id}/campaigns/')).json()
        data = mock_campaigns
        
        #logger.debug(data)
        ##Channel.objects.filter(coordinator__in=data['coordinators']).update(actual=False)
                
        for id, coordinator in data['coordinators'].items():
            Coordinator.objects.update_or_create(id=id, defaults={
                'name': coordinator['name'],
                'phones': json.dumps(coordinator['phones'], ensure_ascii=False),
                'external_channels': json.dumps(coordinator['external_channels'], ensure_ascii=False),
            })
            #for channel in coordinator['channels']:
                #Channel.objects.update_or_create(id=channel['id'], {
                    #'name': channel['name'],
                    #'actual': True,
                    #'coordinator': id,
                #})
        
        for id, campaign in data['campaigns'].items():
            election = data['elections'].get(campaign['election'])
            #logger.debug(election)
            Campaign.objects.update_or_create(id=id, defaults={
                'country': country,
                'election_name': election.get('name'),
                'region': election.get('region'), 
                'munokrug': election.get('munokrug'), 
                'fromtime': dtparse(campaign['fromtime']),
                'totime': dtparse(campaign['totime']),
                'vote_date': dtparse(election['date']),
                'coordinator_id': campaign['coordinator'],
                'elect_flags': ','.join(election['flags']),
                'phones': json.dumps(campaign['phones'], ensure_ascii=False),
                'external_channels': json.dumps(campaign['external_channels'], ensure_ascii=False),
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
    logger.debug('Active election observers campaigns in current region: {}'.format(
        json.dumps(list(campaigns.values()), ensure_ascii=False, indent=2, cls=DjangoJSONEncoder)
    ))
    if campaigns.filter(munokrug__isnull=True).exists():
        state.superior_ik = 'TIK'
    else:
        state.superior_ik = 'IKMO'
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
                #state.questions[input['id']] = input
                    
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
            if getattr(state, '_raise_all', None):
                raise e
            await sleep(5)
        else:
            if response.status_code == 200:
                return response
            logger.info(repr(response))
            await sleep(5)
            
