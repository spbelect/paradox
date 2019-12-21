from kivy.tests.common import GraphicUnitTest, UnitTestTouch
from unittest import TestCase
from unittest.mock import patch, Mock
import pytest
import pytest_asyncio
import asyncio
from asyncio import sleep

from fixtures import app 

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

        ## get your Window instance safely
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
        
#class ZZMyTestCase(GraphicUnitTest):

async def retry(fn, *args, **kw):
    for x in range(30):
        res = fn(*args, **kw)
        if res:
            return res
        await sleep(0.1)
    else:
        raise Exception(f'retry failed: {fn} {args!r} {kw!r}')
    
    
async def get(widget, **kwargs):
    for x in range(30):
        res = list(widget.instances.filter(**kwargs))
        if res:
            return res[0]
        await sleep(0.1)
    else:
        raise Exception(f'No such widget: {widget} {kwargs!r}')
    
#@pytest.mark.django_db
@pytest.mark.asyncio
async def test_render(app):

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

    from app_state import state
    state._raise_all = True
    
    from paradox import uix
    #from paradox.uix.screens.position_screen import RegionChoice, RoleChoice
    from paradox.uix.screens.formlist_screen import FormListItem
    from paradox.uix.quiz_widgets.base import QuizWidget
    from paradox.uix.complaint import ComplaintStatusChoice
    
    ##await sleep(10)
    ##await app.wait_clock_frames(500)
    await app.click(uix.formlist.ids.menu_button)
    
    await app.click(uix.sidepanel.ids.region)
    #print(uix.position.ids.region_choices)
    
    await app.click(uix.position.ids.regions)
    
    await app.click(await retry(uix.position.ids.regions.getchoice, 'ru_47'))
    
    await app.click(uix.position.ids.roles)
    await app.click(uix.position.ids.roles.getchoice('smi'))
    
    await app.click(uix.position.ids.uik)
    await app.text_input('1803')
        
    await app.click(uix.position.ids.next)
    
    await app.click(uix.userprofile.ids.first_name)
    await app.text_input('name')
    await app.click(uix.userprofile.ids.last_name)
    await app.text_input('famil')
    await app.click(uix.userprofile.ids.email)
    await app.text_input('email@ya.ru')
    #await app.text_input('emailya.ru')
    await app.click(uix.userprofile.ids.phone)
    await app.text_input('9061234567')
    await app.click(uix.userprofile.ids.next)
    
    state.update(
        profile=dict(email='a@ya.ru', first_name='2', last_name='3', phone='4', middle_name='5', telegram=''),
        region=state.regions['ru_47'],
        role='smi',
        uik='244'
    )
    
    await app.click(await get(FormListItem, id='1'))
    
    quizwidget = await get(QuizWidget, question_id='i1')
    await app.click(quizwidget.ids.no)
    
    
    #complaint = 
    await app.click(quizwidget.complaint.ids.uik_complaint_status)
    
    await app.click(await get(ComplaintStatusChoice, value='refuse_to_accept'))
    
    fromscreen = uix.screenmgr.get_screen('form_1')
    fromscreen.ids.scrollview.scroll_to(quizwidget.complaint.ids.preview_tik_complaint)
    await app.wait_clock_frames(50)  # scroll animation
    
    await app.click(quizwidget.complaint.ids.preview_tik_complaint)
    
    uix.tik_complaint.ids.scrollview.scroll_to(uix.tik_complaint.ids.edit_button)
    await app.wait_clock_frames(50)  # scroll animation
    
    await app.click(uix.tik_complaint.ids.edit_button)
    
    await app.click(uix.tik_complaint.ids.complaint_textinput)
    
    await app.text_input('lol')
    
    uix.tik_complaint.ids.scrollview.scroll_to(uix.tik_complaint.ids.save)
    await app.wait_clock_frames(50)  # scroll animation
    
    await app.click(uix.tik_complaint.ids.save)
    
    uix.tik_complaint.ids.scrollview.scroll_to(uix.tik_complaint.ids.send_button)
    await app.wait_clock_frames(50)  # scroll animation
    
    await app.click(uix.tik_complaint.ids.send_button)
    
    await app.wait_clock_frames(50) 
    
    await app.click(uix.tik_complaint.ids.back)
    
    
    asyncio.get_running_loop()._kivyrunning = False
    
    #print(11)
    #await app.wait_clock_frames(5000)
    #return
    #await asyncio.sleep(5)
    #self.render(app.root, 20)
    
    #from фынтсшщ import sleep
    #sleep(10)
    #self.assertTrue(button.test_released)

