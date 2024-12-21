from app_state import state
from asyncio import sleep
from collections.abc import Iterable
from kivy.tests.common import GraphicUnitTest, UnitTestTouch
from unittest import TestCase, skip
from unittest.mock import patch, Mock, ANY
import pytest
import pytest_asyncio
import asyncio

from .fixtures import app, mocked_api


async def retry(fn, *args, **kw):
    for x in range(30):
        res = fn(*args, **kw)
        if res:
            return res
        await sleep(0.1)
    else:
        raise Exception(f'retry failed: {fn} {args!r} {kw!r}')
    
    
async def wait_instance(widget, **kwargs):
    for x in range(30):
        res = list(widget.instances.filter(**kwargs))
        if res:
            return res[0]
        await sleep(0.1)
    else:
        raise Exception(f'No such widget: {widget} {kwargs!r}')
    
    
#async def wait_result(callable, *args, **kwargs):
    #for x in range(30):
        #res = callable(*args, **kwargs)
        #if res:
            #return res
        #await sleep(0.1)
    #else:
        #raise Exception(f'No such widget: {callable}, *args, **kwargs')
    
#def props(**kw):
    #return 
                     
                     
async def wait_listitem(iterable: Iterable, **kwargs):
    """
    Wait for any item in the given iterable to have matching attributes provided
    in kwargs. Return first matching item or raise Exception on timeout.
    
    Example below waits for a child widget of mywidget, which has attribute called
    'text' with value 'mytext', and then return it:
    
    >> child = await wait_listitem(mywidget.children, text='mytext')
        
    """
    for x in range(30):
        for item in iterable:
            if all((getattr(item, k) == v) for k, v in kwargs.items()):
                return item
        await sleep(0.1)
    else:
        raise Exception(f'No such widget: {iterable} {kwargs!r}')       
                     
                     
#@pytest.mark.django_db
#async def lol(mocked_api, app):
# async def test_render(mocked_api):

@pytest.mark.asyncio
async def test_render(mocked_api, app):

    #from main import ParadoxApp

    # with GraphicUnitTest.render() you basically do this:
    # runTouchApp(Button()) + some setup before
    #app = ParadoxApp()
    #loop = asyncio.get_event_loop()
    #loop.create_task(app.async_run())

    #app.root = app.build()
    #runTouchApp()
    #self.render(app.root)

    # get your Window instance safely
    #from kivy.base import EventLoop
    #EventLoop.ensure_window()
    #window = EventLoop.window

    # await app.wait_clock_frames(5)
    await sleep(0.1)
    # import ipdb; ipdb.sset_trace()

    #import ipdb; ipdb.sset_trace()

    from paradox import uix
    #from paradox.uix.screens.position_screen import RegionChoice, RoleChoice
    #from paradox.uix.screens.home_screen import FormListItem
    from paradox.uix.quiz_widgets.base import QuizWidget
    from paradox.uix.confirm import ConfirmModal

    await sleep(0.1)

    #await app.click(uix.screens.home.home.ids.menu_button)


    #await app.click(uix.sidepanel.ids.region)
    ##print(uix.screens.position.position.ids.region_choices)


    ## Экран позиции.
    ## Кликнуть на список регионов.
    #await app.click(uix.screens.position.position.ids.regions)

    ## Кликнуть на "Лен область"
    #await app.click(await retry(uix.screens.position.position.ids.regions.getchoice, 'ru_47'))

    ## Кликнуть "выбрать статус"
    #await app.click(uix.screens.position.position.ids.roles)

    ## Кликнуть на "ПРГ"
    #await app.click(await retry(uix.screens.position.position.ids.roles.getchoice, 'prg'))

    ## Кликнуть на "Номер УИК"
    #await app.click(uix.screens.position.position.ids.uik)
    ## Ввести 1803
    #await app.text_input('1803')

    ## Кликнуть "Продолжить"
    #await app.click(uix.screens.position.position.ids.next)


    ## Экран профиля.
    #await app.click(uix.screens.userprofile.userprofile.ids.first_name)
    #await app.text_input('name')
    #await app.click(uix.screens.userprofile.userprofile.ids.last_name)
    #await app.text_input('famil')
    #await app.click(uix.screens.userprofile.userprofile.ids.email)
    #await app.text_input('email@ya.ru')
    ##await app.text_input('emailya.ru')  # Невалидный email
    #await app.click(uix.screens.userprofile.userprofile.ids.phone)
    #await app.text_input('9061234567')
    ## Кликнуть "Продолжить"
    #await app.click(uix.screens.userprofile.userprofile.ids.next)

    state.update(
        profile=dict(email='a@ya.ru', first_name='2', last_name='3', phone='4', middle_name='5', telegram=''),
        region=state.regions['ru_47'],
        role='smi',
        uik='244'
    )
    # Подождать пока кампании будут получены с сервера.
    await sleep(2)
    

    # await sleep(2000)
    ### Главный экран.
    # Кликнуть на тематический раздел анкеты.
    await app.click(await wait_listitem(uix.screens.home.home.ids.topics.children, id='1'))



    ### Экран вопросов (тематический раздел анкеты).
    # Кликнуть на ответ "Нет".
    quizwidget = await wait_instance(QuizWidget, question__id='i1')
    await app.click(quizwidget.ids.no)

    await sleep(1)
    # import ipdb; ipdb.sset_trace()
    # Кликнуть на "Обжаловать".
    await app.click(quizwidget.ids.complaint)
    await sleep(1.2)


    ### Экран обжалования.
    # Кликнуть на "Статус жалобы".
    await app.click(uix.screens.complaint.complaint.ids.uik_complaint_status)

    await sleep(0.2)
    # Кликнуть на "Отказ принять".
    await app.click(uix.screens.complaint.complaint.ids.uik_complaint_status.getchoice('refuse_to_accept'))
    #await app.click(await wait_instance(ComplaintStatusChoice, value='refuse_to_accept'))

    #fromscreen = uix.screenmgr.get_screen('form_1')
    #uix.screens.complaint.complaint.ids.scrollview.scroll_to(uix.screens.complaint.complaint.ids.tik_text_editor)

    # await sleep(0.1)
    # Click "Why complaint is needed"
    # await app.click(uix.screens.complaint.complaint.ids.handbook_why_complaint)

    #await app.click(quizwidget.complaint.ids.preview_tik_complaint)
    # import ipdb; ipdb.sset_trace()
    await sleep(0.2)
    uix.screens.complaint.complaint.ids.scrollview.scroll_to(uix.screens.complaint.complaint.ids.tik_text_editor.ids.edit_button)
    await sleep(2)  # scroll animation

    # Click "Edit complaint text"
    await app.click(uix.screens.complaint.complaint.ids.tik_text_editor.ids.edit_button)

    uix.screens.complaint.complaint.ids.scrollview.scroll_to(uix.screens.complaint.complaint.ids.tik_text_editor.ids.textinput)
    await sleep(2)  # scroll animation
    
    await app.click(uix.screens.complaint.complaint.ids.tik_text_editor.ids.textinput)
    
    await app.text_input('lol')
    
    uix.screens.complaint.complaint.ids.scrollview.scroll_to(uix.screens.complaint.complaint.ids.tik_text_editor.ids.save)
    await sleep(1)  # scroll animation
    
    await app.click(uix.screens.complaint.complaint.ids.tik_text_editor.ids.save)
    await sleep(2)  # scroll animation
    
    uix.screens.complaint.complaint.ids.scrollview.scroll_to(uix.screens.complaint.complaint.ids.send_tik_complaint)
    await sleep(2)  # scroll animation
    
    await app.click(uix.screens.complaint.complaint.ids.send_tik_complaint)
    await sleep(2)  # scroll animation
    
    confirm = await wait_instance(ConfirmModal)
    await app.click(confirm.ids.yes)
    
    await sleep(2)  # next question
    
    confirm = await wait_instance(ConfirmModal)
    await app.click(confirm.ids.yes)
    
    
    await app.click(uix.screens.complaint.complaint.ids.back)
    
    await sleep(3)  # next question
    
    from paradox.models import Answer
    
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



@skip
def test_respx():
    pass
    # import httpx
    # import respx
    # with respx.mock(
    #     # base_url="http://127.0.0.1:8000/api/v3/",
    #     assert_all_mocked=True,
    #     assert_all_called=False
    #       ) as respx_mock:
    #
    #     # print('mock ru/questions/')
    #     respx_mock.get("http://127.0.0.1:8000/api/v3/ru/questions/").respond(json=[])
    #     # # respx_mock.get("http://127.0.0.1:8000/api/v3/ru/questions/").mock(side_effect=httpx.ConnectError)
    #
    #     # import ipdb; ipdb.sset_trace()
    #     httpxclient = httpx.AsyncClient()
    #     result = await httpxclient.get('http://127.0.0.1:8000/api/v3/ru/questions/')
    #     print("AAAAAA")
    #     return
