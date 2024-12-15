import asyncio
import json
from os.path import join, basename
from asyncio import sleep, create_task
from datetime import datetime
from itertools import chain, cycle
from urllib.parse import urljoin

from app_state import state, on
from dateutil.parser import parse as dtparse
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q, F
from django.utils.timezone import now
from lockorator.asyncio import lock_or_exit
from loguru import logger
#from trio import sleep
import httpx
import httpcore

from paradox import uix
from paradox.uix import newversion_dialog
from paradox.models import Campaign  #, Organization, Answer, AnswerImage, AnswerUserComment
from paradox import config
import paradox
#from paradox import utils

#class on:
    #def __init__(*a):
        #pass
    
    #def __call__(self, f):
        #return f


httpxclient = httpx.AsyncClient()


try:
    from .rotate_server_task import rotate_server
except ImportError:
    @lock_or_exit()
    async def rotate_server():
        """
        Заглушка. Сервер не изменяет, только сбрасывает флаг _server_ping_success.
        """
        logger.info(f'Setting state.server to {paradox.config.SERVER_ADDRESS=}')
        if not state.server == paradox.config.SERVER_ADDRESS:
            state.server = paradox.config.SERVER_ADDRESS
        state._server_ping_success.clear()
        await sleep(10)
        create_task(reconnect())
        return



#async def server_ping_success():
    #if not state._server_ping_success:
        #state._server_ping_success = asyncio.Event()
        #state._server_ping_success.set()  # Assume success on app start.
    #return await state._server_ping_success.wait()
    
    
async def _ping_loop():
    """ Бесконечный цикл. Запускается и останавливается в reconnect() """
    state._server_ping_success.clear()
    while True:
        try:
            return await httpxclient.get(state.server, timeout=15)
        except httpcore.TimeoutException as e:
            pass
        except httpcore.NetworkError as e:
            # Сеть недоступна.
            logger.debug(repr(e))
        # except httpx.ConnectError as e:
        #     # Failed to establish a connection.
        #     logger.debug(repr(e))
        except Exception as e:
            # Not a network error, assume server issue. Raise it to force server rotation.
            raise
        else:
            state._server_ping_success.set()
            return
        await sleep(5)
    
    
@lock_or_exit()
async def reconnect():
    """
    Запустить _ping_loop(), если не отвечает за 3 минуты, остановить _ping_loop(),
    и изменить state.server на следующий.
    """
    while not state.server:
        # state.server должен быть иницализирован в main.on_start()
        await sleep(5)
    
    logger.info('Checking server.')
    try:
        await asyncio.wait_for(_ping_loop(), timeout=3*60)
    except asyncio.TimeoutError:
        logger.info('Server ping timeout.')
        await rotate_server()
    except Exception as e:
        logger.warning(e)
        await rotate_server()
    else:
        logger.info('Server connection ok.')
        state._server_ping_success.set()


async def api_request(method, url, data=None, timeout=15):
    while not state.server:
        # state.server должен быть иницализирован в main.on_start()
        logger.debug('Waiting for state initialization')
        await sleep(5)
    
    await state._server_ping_success.wait()
    
    url = urljoin(state.server, urljoin('/api/v3/', url))
    logger.debug(f'{method} {url}')
    try:
        #state.server = 'http://8.8.8.8'
        return await httpxclient.request(
            method, url, timeout=timeout,
            json=dict(data, app_id=state.app_id) if data else None
        )
    except httpcore.TimeoutException as e:
        logger.debug(repr(e))
        create_task(reconnect())
        raise
    except Exception as e:
        create_task(reconnect())
        
        if getattr(e, 'args', None) and isinstance(e.args[0], OSError):
            if getattr(e.args[0], 'errno', None) == 101:
                raise
        logger.debug(repr(e))
        raise
        
       
       
async def check_new_version_loop():
    while True:
        try:
            response = await httpxclient.get(config.CHANGELOG_URL, timeout=25)
        except:
            await sleep(2)
            continue
        if response.status_code != 200:
            await sleep(2)
            continue
        
        changelog = response.content.decode('utf8').strip()
        vstring = 'Версия %s' % config.version[0:3]
        if vstring in changelog:
            try:
                before, after = changelog.split(vstring)
        
                new = '\n'.join(before.split('\n')[4:]).strip()  # skip first 4 lines of the file
                if new:
                    uix.newversion_dialog.show_new_version_dialog(new)
            except Exception as e:
                logger.error(repr(e))
            
        await sleep(10*60)

 
def get_throttle_delay():
    vote_dates = Campaign.objects.positional().current().values_list('vote_date', flat=True)
    if now().date() in list(vote_dates):
        return 5    # В день голосования
    else:
        return 0.1  # В любой другой день
        
        
async def recv_loop(url):
    while True:
        try:
            response = await api_request('GET', url)
        except httpx.RequestError as e:
            logger.error(f'{e!r} {e.request}')
        except Exception as e:
            if getattr(state, '_raise_all', None):
                raise e
            else:
                logger.error(repr(e))
                await sleep(5)
        else:
            if response.status_code == 200:
                return response
            logger.info(repr(response))
            await sleep(5)
            


