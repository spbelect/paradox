from asyncio import create_task, sleep
from loguru import logger
from app_state import state

from os.path import join
from random import randint
import asyncio
import django
from django import conf
from django.core import management

from paradox import uix
from paradox import client


mock_regions = {
    'ru_47': {
        'id': 'ru_47',
        'name': 'Лен. обл.',
        'tiks': [
            {
                'id': '68b7a-2533d-8dd43',
                'uik_ranges': [[21,800]],
                'name': 'Tik kingiseppskogo rayona',
                'email': 'tik-kingiseppskogo@lo.ru',
                'phone': '72727',
                'address': 'street 35'
            },
        ],
        'munokruga': [],
    },
    'ru_78': {
        'id': 'ru_78',
        'name': 'Spb',
        'tiks': [
            {
                'id': 'f8e424-235b-77a8a',
                'uik_ranges': [[21,800]],
                'name': 'Tik 7',
                'email': 'tik7@x.ru',
                'phone': '6463',
                'address': 'ulitsa 77'
            },
        ],
        'munokruga': [
            {
                'id': '6ab3-d1c23',
                'uik_ranges': [[1,100], [4010, 4055]],
                'name': 'Муниципальный округ Дачное',
                'ikmo_email': 'MOlol@x.ru',
                'ikmo_phone': '78796',
                'ikmo_address': 'leninsky 53'
            },
        ],
    }
}

mock_quiz_topics = [{
    "id": "14bf4a0a-30f4-4ed2-9bcb-9a16a65033d7",
    "elections": None,
    "name": "НАЧАЛО ПОДСЧЕТА",
    "questions": [
      {
        "id": "ecc1deb3-5fe7-48b3-a07c-839993e4563b",
        "label": "Неиспользованные бюллетени убраны в сейф или лежат на видном месте.",
        "fz67_text": "ст.456 п.2 Неиспользованные бюллетени бла бла бла\n",
        "type": "YESNO",   # тип да\нет
        "incident_conditions": { "answer_equal_to": False },
        "example_uik_complaint": "жалоба: бла бла"
      },
      {
        "id": "b87436e0-e7f2-4453-b364-a952c0c7842d",
        "label": "Число проголосаваших досрочно",
        "fz67_text": "ст.123 п.9 Число проголосаваших досрочно бла бла бла\n",
        "type": "NUMBER",  # тип число
        "incident_conditions": { "answer_greater_than": 100 },
        "visible_if": {
            "elect_flags": ["dosrochka"],  # показать только если есть активная кампания с досрочкой
        },
        "example_uik_complaint": "жалоба: бла бла"
      },
      {
        "id": "77532eb3-5fe7-48b3-a07c-cd9b35773709",
        "label": "Все досрочные бюллетени считаются отдельно.",
        "type": "YESNO",
        # Считать ответ инцидетом если все заданные условия соблюдены
        "incident_conditions": { "answer_equal_to": False },
        # Показывать этот вопрос в анкете если:
        # - текущие выборы имеют заданные флаги
        # И
        # - даны разрешающие ответы на ограничивающие вопросы
        "visible_if": {
            "elect_flags": ["dosrochka"],  # показать только если есть активная кампания с досрочкой
            "limiting_questions": {
                # Возможные значения:
                # all: [] - все условия в списке должны быть соблюдены
                # any: [] - хотя бы одно условие в списке соблюдено
                "all": [
                    # Возможные условия:
                    # answer_equal_to, answer_greater_than, answer_less_than
                    {
                        "question_id": "ecc1deb3-5fe7-48b3-a07c-839993e4563b", 
                        "answer_equal_to": False
                    },
                    {
                        "question_id": "b87436e0-e7f2-4453-b364-a952c0c7842d", 
                        "answer_greater_than": 100,
                        "answer_less_than": 1000
                    }
                ]
            },
        },
        "example_uik_complaint": "жалоба: бла бла",
        "fz67_text": "ст. 778 ... \n",
      },
    ],
  },
]
      
      
@uix.homescreen.show_loader
async def main(app):
    logger.info(f"Using db {django.conf.settings.DATABASES['default']}")
    
    await sleep(0.2)
    logger.info('Start migration.')
    django.core.management.call_command('migrate')
    logger.info('Finished migration.')
    await sleep(0.1)
    
    
    # Initialize application state
    state._server_ping_success = asyncio.Event()
    state._server_ping_success.set()  # Assume success on app start.
    
    statefile = join(app.user_data_dir, 'state.db.shelve')
    logger.info(f'Reading state from {statefile}')
    state.autopersist(statefile)
    if 'country' not in state:
        logger.info('Creating default state.')
    
    state.setdefault('app_id', randint(10 ** 19, 10 ** 20 - 1))
    state.setdefault('profile', {})    
    state.setdefault('country', 'ru')
    state.setdefault('superior_ik', 'TIK')
    state.setdefault('tik', None)
    state.setdefault('regions', {})
    
    # Dict of questions by id { question.id: {"label": "", "type": "", ...}, ... }
    state.setdefault('questions', {})
    
    # Dict of lists of quiz_topics by country. Topics list for each country is ordered.
    state.setdefault('quiz_topics', {'ru': [], 'ua': [], 'kz': [], 'by': []})
    
    logger.info(f'Server: {state.server}')
    if not state.server:
        await client.rotate_server()
    
    await sleep(0.2)
    
    
    asyncio.create_task(client.check_new_version_loop())
    
    uix.homescreen.build_topics()
    uix.events_screen.restore_past_events()
    logger.info('Restored past events.')
    
    
    logger.info('Updating questions.')
    
    #quiz_topics = mock_quiz_topics
    quiz_topics = (await client.recv_loop(f'{state.country}/questions/')).json()
    #logger.info(quiz_topics)
    #quiz_topics = {'ru': json.load(open('forms_general.json'))}
    
    if quiz_topics:
        logger.info(f'Got {len(quiz_topics)} quiz topics for country "{state.country}"')
    else:
        logger.error('Received empty quiz topics for country "{state.country}"')
        
    # Update state.questions - build dict by id for all questions of all received quiz_topics.
    for topic in quiz_topics:
        try:
            state.questions.update({q['id']: q for q in topic['questions']})
        except Exception as e:
            logger.error(repr(e))
            uix.float_message.show('Ошибка при обновлении анкет')
            uix.homescreen.ids.messages.add_widget(Label(
                text='Ошибка при обновлении анкет. Возможно вы используете старую версию программы.'    
            ))
            paradox.exception_handler.send_debug_message(e)
            return
            
    # Build each question dependants list - i.e. list of questions that may be
    # hidden or displayed depending on the answer to the current question.
    # This is the reverse of `limiting_questions` list, used in uix.quiz_widgets.base
    for dependant_question in state.questions.values():
        rules = dependant_question.get('visible_if', {}).get('limiting_questions', {})
        for rule in (rules.get('any') or rules.get('all') or []):
            # Parent (limiting_question).
            parent = state.questions.get(rule.question_id, {})
            # Add this dependant_question to the `dependants` list of its parent.
            parent.setdefault('dependants', []).append(dependant_question['id'])
        
    # Update topics for current country.
    if not state.quiz_topics.get(state.country) == quiz_topics:
        state.quiz_topics[state.country] = quiz_topics
        uix.homescreen.build_topics()
    
    #regions = mock_regions
    regions = (await client.recv_loop(f'{state.country}/regions/')).json()
    ###regions = {f'ru_{x["id"]}': dict(x, id=f'ru_{x["id"]}') for x in json.load(open('regions.json'))}
        
    #logger.debug(regions)
    state.regions.update(regions)
    logger.info('Regions updated.')
    if state.region.id:
        if not state.region == state.regions.get(state.region.id):
            logger.debug(f'Setting region to {state.region.id}')
            state.region = state.regions.get(state.region.id)
    
    uix.events_screen.restore_past_events()
    logger.info('Restored past events (fin).')
    
    asyncio.create_task(client.answer_send_loop())
    asyncio.create_task(client.answer_image_send_loop())
    app.app_has_started = True
    logger.info('Startup finished.')
 
