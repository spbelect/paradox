from asyncio import sleep
from itertools import chain, cycle
from os.path import basename

from app_state import state, on
from django.db.models import Q, F
from loguru import logger

from . import base
from paradox.models import AnswerImage
from paradox import uix


async def _patch_image_meta(image):
    """
    Пользователь изменил метаданные сделанной фотографии. Отправить метаданные на сервер.
    Флаг "удален" - пока что единственный полезный мета-параметр который нужно послать на сервер.
    """
    try:
        response = await base.api_request('PATCH', f'answers/{image.answer_id}/images/{image.md5}', {
            #'type': image.type,
            #'time_created': image.time_created,
            'deleted': image.deleted,
            #'filename': image.md5 + basename(image.filepath),
        })
    except Exception as e:
        image.update(send_status='patch_exception')
        if getattr(state, '_raise_all', None):
            raise e
        return
    if not response.status_code == 200:
        image.update(send_status=f'patch_http_{response.status_code}')
        return
    
    image.update(send_status='sent', time_sent=now())


async def answer_image_send_loop():
    """
    Бесконечный цикл. Запускается в main.
    TODO: перенести в бэкграунд-сервис на android.
    """
    while True:
        # Фото к еще не отправленным ответам. (будут отправлены только после отправки ответов)
        waiting_answer = AnswerImage.objects.filter(answer__time_sent__isnull=True).count()
        
        # Фото которые пользователь обновил после того как они были отправлены. (напр. удалил)
        topatch = AnswerImage.objects.filter(
            Q(time_sent__isnull=False) & Q(time_sent__lt=F('time_updated'))
        )
        
        # Новые фото к уже отправленным ответам.
        topost = AnswerImage.objects.exclude(deleted=True).filter(
            Q(time_sent__isnull=True) & Q(answer__time_sent__isnull=False)
        )
        
        if topost.count() or topatch.count() or waiting_answer:
            logger.info(
                f'{topost.count()} images to post now. {topatch.count()} images to patch.'
                f' {waiting_answer} waiting for answer to be sent first.'
            )
        else:
            logger.debug('0 images to post or patch.')

        throttle_delay = base.get_throttle_delay()
        
        for image in topatch:
            await _patch_image_meta(image)
            await sleep(throttle_delay)
            
        for image in topost:
            await sleep(throttle_delay)
            try:
                response = await base.api_request('POST', 'upload_slot/', {
                    'filename': image.md5 + basename(image.filepath),
                    'md5': image.md5,
                    'content_type': 'image/jpeg'
                })
            except Exception as e:
                logger.error(repr(e))
                image.update(send_status='req_exception')
                if getattr(state, '_raise_all', None):
                    raise e   # For testing
                continue
            if not response.status_code == 200:
                logger.error(repr(response))
                image.update(send_status=f'req_http_{response.status_code}')
                continue
            
            s3params = response.json()
            try:
                response = await base.httpxclient.post(
                    s3params['url'], data=s3params['fields'], 
                    files={'file': open(image.filepath, 'rb')},
                    timeout=3*60
                )
            except Exception as e:
                logger.error(repr(e))
                image.update(send_status='upload_exception')
                if getattr(state, '_raise_all', None):
                    raise e   # For testing
                continue
            if not response.status_code in (200, 201, 204):
                logger.error(repr(response))
                logger.error(response.text)
                image.update(send_status=f'upload_http_{response.status_code}')
                continue
            
            try:
                response = await base.api_request('POST', f'answers/{image.answer_id}/images/', {
                    'type': image.type,
                    'timestamp': image.time_created.isoformat(),
                    'deleted': image.deleted,
                    'filename': image.md5 + basename(image.filepath),
                })
            except Exception as e:
                logger.error(repr(e))
                image.update(send_status='post_exception')
                if getattr(state, '_raise_all', None):
                    raise e   # For testing
                continue
            if response.status_code == 404:
                try:
                    logger.info(f'{response!r} {response.json()}')
                except:
                    logger.info(repr(response))
                    image.update(send_status=f'post_http_404')
                    continue
                else:
                    err = response.json()
                    if isinstance(err, dict) and err.get('status') == 'no such answer':
                        #   На сервере нет такого ответа - возможно на сервере удалили ответ 
                        # после того как юзер его отправил.
                        #   Скорее всего это неисправимая ошибка, так что помечаем как 
                        # успешно отправленную, чтобы больше не пытаться.
                        image.update(send_status='sent', time_sent=now())
                        continue
            if not response.status_code == 200:
                logger.error(repr(response))
                image.update(send_status=f'post_http_{response.status_code}')
                continue
            
            image.update(send_status='sent', time_sent=now())
            #print(res.content)
            #print('ok')
        await sleep(10)
            
