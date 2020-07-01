from asyncio import sleep

from app_state import state, on
from lockorator.asyncio import lock_or_exit
from loguru import logger

from . import base


@on('state.profile')
@lock_or_exit()
async def post_userprofile():
    if not state.get('profile', None):
        return
    logger.debug('Sending profile.')
    fields = 'email last_name first_name phone'.split()
    await sleep(1)
    while True:
        logger.debug('Sending profile loop until success.')
        prev = tuple(state.profile.get(x, None) for x in fields)
        if not all(prev):
            logger.debug(f'Skip sending incomplete profile: {dict(zip(fields, prev))}')
            return
        
        try:
            response = await base.api_request('POST', f'userprofile/', {
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

 
