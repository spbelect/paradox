from app_state import state
from asyncio import sleep
from kivy.tests.common import GraphicUnitTest, UnitTestTouch
from unittest import TestCase
from unittest.mock import patch, Mock, ANY
import pytest
import pytest_asyncio
import asyncio

from fixtures import app, mocked_api

#def x(self):
    ##import ipdb; ipdb.sset_trace()
    #self.test_released = True
    
#@pytest.mark.asyncio
#class XXTestCase(GraphicUnitTest):

    #async def test_render2(self):
        #from kivy.uix.button import Button

        ## with GraphicUnitTest.render() you basically do this:
        ## runTouchApp(Button()) + some setup before
        #button = Button()
        #self.render(button)

        ## wait_instance your Window instance safely
        #from kivy.base import EventLoop
        #EventLoop.ensure_window()
        #window = EventLoop.window

        #touch = UnitTestTouch(
            #*[s / 2.0 for s in window.size]
        #)

        ## bind something to test the touch with
        #button.bind(on_release=x)
        ##button.bind(
            ##on_release=lambda instance: setattr(
                ##instance, 'test_released', True
            ##)
        ##)

        ## then let's touch the Window's center
        #touch.touch_down()
        #touch.touch_up()
        #self.assertTrue(button.test_released)
        #await sleep(5000)
        
#class ZZMyTestCase(GraphicUnitTest):

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
                     
## matchall(x) returns True if x matches all attributes provided in kwargs
#matchall = lambda x: all((getattr(x, k) == v) for k, v in kwargs.items())
    
                     
async def wait_listitem(iterable, **kwargs): 
    """
    Usage:
    
    Wait for a child widget of mywidget, which has attribute called 
    'text' with value 'mytext', and then return it:
    
        child = await wait_listitem(mywidget.children, text='mytext')
        
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
    await app.wait_clock_frames(5)

    #import ipdb; ipdb.sset_trace()
    
    from paradox import uix
    #from paradox.uix.screens.position_screen import RegionChoice, RoleChoice
    #from paradox.uix.screens.home_screen import FormListItem
    from paradox.uix.quiz_widgets.base import QuizWidget
    from paradox.uix.confirm import ConfirmModal
    
    await sleep(3)
    
    #await app.click(uix.homescreen.ids.menu_button)
    
    
    #await app.click(uix.sidepanel.ids.region)
    ##print(uix.position.ids.region_choices)
    
    
    ## Экран позиции.
    ## Кликнуть на список регионов.
    #await app.click(uix.position.ids.regions)
    
    ## Кликнуть на "Лен область"
    #await app.click(await retry(uix.position.ids.regions.getchoice, 'ru_47'))
    
    ## Кликнуть "выбрать статус"
    #await app.click(uix.position.ids.roles)
    
    ## Кликнуть на "ПРГ"
    #await app.click(await retry(uix.position.ids.roles.getchoice, 'prg'))
    
    ## Кликнуть на "Номер УИК"
    #await app.click(uix.position.ids.uik)
    ## Ввести 1803
    #await app.text_input('1803')
        
    ## Кликнуть "Продолжить"
    #await app.click(uix.position.ids.next)
    
    
    ## Экран профиля.
    #await app.click(uix.userprofile.ids.first_name)
    #await app.text_input('name')
    #await app.click(uix.userprofile.ids.last_name)
    #await app.text_input('famil')
    #await app.click(uix.userprofile.ids.email)
    #await app.text_input('email@ya.ru')
    ##await app.text_input('emailya.ru')  # Невалидный email
    #await app.click(uix.userprofile.ids.phone)
    #await app.text_input('9061234567')
    ## Кликнуть "Продолжить"
    #await app.click(uix.userprofile.ids.next)
    
    state.update(
        profile=dict(email='a@ya.ru', first_name='2', last_name='3', phone='4', middle_name='5', telegram=''),
        region=state.regions['ru_47'],
        role='smi',
        uik='244'
    )
    # Подождать пока кампании будут получены с сервера.
    await sleep(4) 
    
    
    ### Главный экран.
    # Кликнуть на тематический раздел анкеты.
    await app.click(await wait_listitem(uix.homescreen.ids.topics.children, id='1'))
    
    
    ### Экран вопросов (тематический раздел анкеты).
    # Кликнуть на ответ "Нет".
    quizwidget = await wait_instance(QuizWidget, question__id='i1')
    await app.click(quizwidget.ids.no)
    
    # Кликнуть на "Обжаловать".
    await app.click(quizwidget.ids.complaint)
    
    
    ### Экран обжалования.
    # Кликнуть на "Статус жалобы".
    await app.click(uix.complaint.ids.uik_complaint_status)
    
    # Кликнуть на "Отказ принять".
    await app.click(uix.complaint.ids.uik_complaint_status.getchoice('refuse_to_accept'))
    #await app.click(await wait_instance(ComplaintStatusChoice, value='refuse_to_accept'))
    
    #fromscreen = uix.screenmgr.get_screen('form_1')
    #uix.complaint.ids.scrollview.scroll_to(uix.complaint.ids.tik_text_editor)
    
    #await app.click(quizwidget.complaint.ids.preview_tik_complaint)
    
    uix.complaint.ids.scrollview.scroll_to(uix.complaint.ids.tik_text_editor.ids.edit_button)
    await sleep(2)  # scroll animation
    
    await app.click(uix.complaint.ids.tik_text_editor.ids.edit_button)
    
    uix.complaint.ids.scrollview.scroll_to(uix.complaint.ids.tik_text_editor.ids.textinput)
    await sleep(2)  # scroll animation
    
    await app.click(uix.complaint.ids.tik_text_editor.ids.textinput)
    
    await app.text_input('lol')
    
    uix.complaint.ids.scrollview.scroll_to(uix.complaint.ids.tik_text_editor.ids.save)
    await sleep(1)  # scroll animation
    
    await app.click(uix.complaint.ids.tik_text_editor.ids.save)
    await sleep(2)  # scroll animation
    
    uix.complaint.ids.scrollview.scroll_to(uix.complaint.ids.send_tik_complaint)
    await sleep(2)  # scroll animation
    
    await app.click(uix.complaint.ids.send_tik_complaint)
    await sleep(2)  # scroll animation
    
    confirm = await wait_instance(ConfirmModal)
    await app.click(confirm.ids.yes)
    
    await sleep(2)  # next question
    
    confirm = await wait_instance(ConfirmModal)
    await app.click(confirm.ids.yes)
    
    
    await app.click(uix.complaint.ids.back)
    
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

