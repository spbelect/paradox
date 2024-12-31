from asyncio import sleep

from app_state import state, on
from lockorator.asyncio import lock_or_exit
from loguru import logger

from . import base


@on('state.region', 'state.country', 'state.uik', 'state.role')
@lock_or_exit()
async def post_position():
    await sleep(1)
    while True:
        logger.debug('Sending position loop until success.')
        
        prev = (state.uik, state.region.id, state.country, state.role)
        if not all(prev):
            logger.info(f'Skip sending incomplete position {prev}')
            return
        
        try:
            response = await base.api_request('POST', f'position/', {
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

