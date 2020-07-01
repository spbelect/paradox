from asyncio import sleep
from itertools import chain, cycle

from app_state import state, on
from django.db.models import Q, F
from loguru import logger

from . import base
from paradox.models import Answer
from paradox import uix

            
async def _patch_answer(answer):
    """ Return True on success """
    try:
        response = await base.api_request('PATCH', f'answers/{answer.id}/', {
            'revoked': answer.revoked,
            'uik_complaint_status': answer.get_uik_complaint_status_display(),
            'tik_complaint_text': answer.tik_complaint_text ,
            'tik_complaint_status': answer.get_tik_complaint_status_display(),
        })
    except Exception as e:
        answer.update(send_status='patch_exception')
        if getattr(state, '_raise_all', None):
            raise e   # For testing
        return False
    if response.status_code == 404:
        try:
            logger.info(f'{response!r} {response.json()}')
        except:
            logger.info(repr(response))
            answer.update(send_status=f'post_http_404')
            return False
        else:
            err = response.json()
            if isinstance(err, dict) and err.get('status') == 'no such answer':
                #   На сервере нет такого ответа - возможно на сервере удалили ответ 
                # после того как юзер его отправил.
                #   Скорее всего это неисправимая ошибка, так что помечаем ответ как 
                # успешно отправленный, чтобы больше не пытаться.
                answer.update(send_status='sent', time_sent=now())
                return True
            else:
                answer.update(send_status=f'post_http_404')
                return False
    elif not response.status_code == 200:
        try:
            logger.info(f'{response!r} {response.json()}')
        except:
            logger.info(repr(response))
            
        answer.update(send_status=f'patch_http_{response.status_code}')
        return False
    
    # Статус 200, успешно отпрвлен.
    answer.update(send_status='sent', time_sent=now())
    return True


async def answer_send_loop():
    """
    Бесконечный цикл. Запускается в main.
    """
    while True:
        # Ответы которые пользователь обновил после того как они были отправлены. 
        # (напр. статус жалобы)
        topatch = Answer.objects.filter(time_sent__isnull=False, time_sent__lt=F('time_updated'))
        
        # Еще не отправленные ответы.
        topost = Answer.objects.filter(time_sent__isnull=True)
        
        logger.info(f'{topost.count()} answers to post. {topatch.count()} answers to patch.')
        
        throttle_delay = base.get_throttle_delay()
            
        for answer in chain(topost, topatch):
            quizwidgets = uix.QuizWidget.instances.filter(question__id=answer.question_id)
            quizwidgets.on_send_start(answer)
            await sleep(throttle_delay)
            
        for answer in topatch:
            quizwidgets = uix.QuizWidget.instances.filter(question__id=answer.question_id)
            if await _patch_answer(answer):
                quizwidgets.on_send_success(answer)
            else:
                quizwidgets.on_send_error(answer)
            await sleep(throttle_delay)
            
        for answer in topost:
            quizwidgets = uix.QuizWidget.instances.filter(question__id=answer.question_id)
            try:
                response = await base.api_request('POST', 'answers/', {
                    'id': answer.id,
                    'question_id': answer.question_id,
                    'value': answer.value,
                    'uik_complaint_status': answer.get_uik_complaint_status_display(),
                    'tik_complaint_status': answer.get_tik_complaint_status_display(),
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
                    raise e   # For testing
                await sleep(throttle_delay)
                continue
            
            if response.status_code == 404:
                try:
                    logger.info(f'{response!r} {response.json()}')
                except:
                    logger.info(repr(response))
                    answer.update(send_status=f'post_http_404')
                    quizwidgets.on_send_error(answer)
                else:
                    err = response.json()
                    if isinstance(err, dict) and err.get('status') == 'no such question':
                        #   На сервере нет такого вопроса - вероятно на сервере удалили 
                        # старый вопрос. В идеале на сервере вопросы удаляться совсем не 
                        # должны, а только исключаться из анкеты. Но пока идет активная
                        # разработка, и бывает что вопросы удаляются.
                        #   Скорее всего это неисправимая ошибка, так что помечаем ответ как 
                        # успешно отправленный, чтобы больше не пытаться.
                        answer.update(send_status='sent', time_sent=now())
                        quizwidgets.on_send_success(answer)
                    else:
                        answer.update(send_status=f'post_http_404')
                        quizwidgets.on_send_error(answer)
                        
            elif not response.status_code == 201:
                logger.info(repr(response))
                answer.update(send_status=f'post_http_{response.status_code}')
                quizwidgets.on_send_error(answer)
            else:
                logger.debug(f'{answer.question.id} {answer.question.label} sent successfully.')
                answer.update(send_status='sent', time_sent=now())
                quizwidgets.on_send_success(answer)
                #quizwidgets.on_send_error(answer)
            await sleep(throttle_delay)
        await sleep(5)
        
        
