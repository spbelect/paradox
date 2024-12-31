import os
from app_state import state
from asyncio import sleep
from kivy.tests.common import GraphicUnitTest, UnitTestTouch
from unittest import TestCase, skip
from unittest.mock import patch, Mock, ANY
import pytest
import pytest_asyncio
import asyncio

from .fixtures import app, mocked_api
from .base import wait_instance, wait_listitem


@pytest.mark.asyncio
async def test_complaint(mocked_api, app):
    from paradox import uix
    from paradox.uix.quiz_widgets.base import QuizWidget
    from paradox.uix.confirm import ConfirmModal

    await sleep(0.01)

    state.update(
        profile=dict(email='a@ya.ru', first_name='2', last_name='3', phone='4', middle_name='5', telegram=''),
        region=state.regions['ru_47'],
        role='smi',
        uik='244'
    )
    # Подождать пока кампании будут получены с сервера.
    await sleep(2)

    ### Главный экран.
    # Кликнуть на тематический раздел анкеты.
    await app.click(await wait_listitem(uix.screens.home.screen.ids.topics.children, id='1'))

    ### Экран вопросов (тематический раздел анкеты).
    # Кликнуть на ответ "Нет".
    quizwidget = await wait_instance(QuizWidget, question__id='i1')
    await app.click(quizwidget.ids.no)

    await sleep(1)
    # import ipdb; ipdb.sset_trace()
    # Кликнуть на "Обжаловать".
    await app.click(quizwidget.ids.complaint)
    await sleep(1.2)

    screen = uix.screens.complaint.screen.ids
    ### Экран обжалования.
    # Кликнуть на "Статус жалобы".
    await app.click(screen.uik_complaint_status)

    await sleep(0.2)
    # Кликнуть на "Отказ принять".
    await app.click(screen.uik_complaint_status.getchoice('refuse_to_accept'))
    #await app.click(await wait_instance(ComplaintStatusChoice, value='refuse_to_accept'))

    #fromscreen = uix.screenmgr.get_screen('form_1')
    #uix.screens.complaint.complaint.ids.scrollview.scroll_to(uix.screens.complaint.complaint.ids.tik_text_editor)

    # await sleep(0.1)
    # Click "Why complaint is needed"
    # await app.click(uix.screens.complaint.complaint.ids.handbook_why_complaint)

    #await app.click(quizwidget.complaint.ids.preview_tik_complaint)
    # import ipdb; ipdb.sset_trace()
    await sleep(0.2)
    screen.scrollview.scroll_to(screen.tik_text_editor.ids.edit_button)
    await sleep(2)  # scroll animation

    # Click "Edit complaint text"
    await app.click(screen.tik_text_editor.ids.edit_button)

    screen.scrollview.scroll_to(screen.tik_text_editor.ids.textinput)
    await sleep(2)  # scroll animation
    
    await app.click(screen.tik_text_editor.ids.textinput)
    
    await app.text_input('lol')
    
    screen.scrollview.scroll_to(screen.tik_text_editor.ids.save)
    await sleep(1)  # scroll animation
    
    await app.click(screen.tik_text_editor.ids.save)
    await sleep(2)  # scroll animation
    
    screen.scrollview.scroll_to(screen.send_tik_complaint)
    await sleep(2)  # scroll animation
    
    await app.click(screen.send_tik_complaint)
    await sleep(2)  # scroll animation
    
    confirm = await wait_instance(ConfirmModal)
    await app.click(confirm.ids.yes)
    
    await sleep(2)  # next question
    
    confirm = await wait_instance(ConfirmModal)
    await app.click(confirm.ids.yes)
    
    
    await app.click(screen.back)
    
    await sleep(3)  # next question
    
    from paradox.models import Answer
    
    # THEN one Answer should be stored in database
    # Answer should have tik and uik complait status
    assert list(Answer.objects.values()) == [{
        'country': '',
        'id': ANY,
        'is_incident': True,
        'question_id': 'i1',
        'question_label': 'Вам предоставили',
        'refuse_person': None,
        'region': 'ru_47',
        'revoked': False,
        'role': 'smi',
        'send_status': 'post_http_200',
        'tik_complaint_status': 'sending_to_moderator',
        'tik_complaint_text': ANY,
        'time_created': ANY,
        'time_sent': None,
        'time_updated': ANY,
        'uik': 244,
        'uik_complaint_status': 'refuse_to_accept'

    }]
    
    # AND tik_complaint_text should contain user input
    assert 'lol' in Answer.objects.first().tik_complaint_text
    
    asyncio.get_running_loop()._kivyrunning = False
    
    #print(11)
    #await app.wait_clock_frames(5000)
    #return
    #await asyncio.sleep(5)
    #self.render(app.root, 20)
    
    #from фынтсшщ import sleep
    #sleep(10)
    #self.assertTrue(button.test_released)
