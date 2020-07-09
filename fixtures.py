import pytest
import gc
import weakref
import json
import time
import os.path
import asyncio
from datetime import date
from os.path import dirname
#from kivy.tests import async_sleep

from kivy.tests import UnitKivyApp
from kivy.tests.common import GraphicUnitTest, UnitTestTouch
from unittest.mock import Mock, AsyncMock, patch
from loguru import logger

import respx

from asyncio import sleep
#__all__ = ('kivy_app', )

# keep track of all the kivy app fixtures so that we can check that it
# properly dies
apps = []



@pytest.fixture()
async def mocked_api():
    #from paradox import config
    #if config.SERVER_ADDRESS.endswith('/'):
        #config.SERVER_ADDRESS = config.SERVER_ADDRESS[:-1]
        
    with respx.mock(base_url="http://127.0.0.1:8000/api/v3/", assert_all_mocked=True) as respx_mock:
        
        respx_mock.get("ru/questions/", alias="list_questions", content=[
            {'id': '1', 'name': 'ДО НАЧАЛА', 'questions': [
                {
                    'id': 'i1', 
                    'label': 'Вам предоставили', 
                    'type': 'YESNO',
                    "incident_conditions": { "answer_equal_to": False },
                }
            ]}
        ])
                
        respx_mock.get("ru/regions/", content={
            'ru_47': {'id': 'ru_47', 'name': 'Ленинградская обл', 'munokruga': [], 'tiks': [
                {'name': '№ 11', 'uik_ranges': [[1,9999]], 'email': 'tik001@ya.ru'}
            ]}
        })
            
        respx_mock.get("ru_47/elections/", content=[
            {
                'name': 'Выборы Депутатов МО Дачное',
                'date': date.today().strftime('%Y.%m.%d'), 
                'munokrug': '6ab3-d1c23',
                'flags': ['otkrep', 'mestonah', 'dosrochka'],
                'region': 'ru_78',
                'coordinators': [{
                    'org_id': '754',
                    'org_name': 'Наблюдатели Петербурга',
                    'contacts': [{'type': 'tg', 'name': 'НП общий чат', 'value': 'https://t.me/spbelect_mobile',},],
                    'campaign': {
                        'id': '8446',
                        'contacts': [
                            {'type': 'tg', 'name': 'НП чат Кировский рн', 'value': 'https://t.me/mobile_kir',},
                            {'type': 'ph', 'name': 'НП Кировский', 'value': '88121111'}
                        ],
                    },
                    }]
            },
            {
                'name': 'Выборы ЛО',
                'date': date.today().strftime('%Y.%m.%d'), 
                'flags': ['otkrep', ],
                'region': 'ru_47',
                'coordinators': [{
                    'org_id': '754',
                    'org_name': 'Наблюдатели Петербурга',
                    'contacts': [{'type': 'tg', 'name': 'НП общий чат', 'value': 'https://t.me/spbelect_mobile',},],
                    'campaign': {
                        'id': '1111',
                        'contacts': [
                            {'type': 'tg', 'name': 'НП чат ЛО', 'value': 'https://t.me/mobile_LO',},
                            {'type': 'ph', 'name': 'НП ЛО', 'value': '88127777'}
                        ],
                    },
                    }]
            },
        ])
                    
        respx_mock.post("position/", content=[])
        
        respx_mock.post("userprofile/", content=[])
        #respx_mock.post("quiz_answers/", content=[])
        respx_mock.post("answers/", content=[])
        
        yield respx_mock


@pytest.fixture()
async def app():
    
    from app_state import state
    state._raise_all = True
    
    from django.conf import settings
    import os
    from os.path import exists
    db = settings.DATABASES['default']['NAME']
    if exists(db):
        print(123123)
        os.remove(db)
    
    
    import main

    #from paradox import client
    #patch('paradox.client.client', Mock(request=AsyncMock(side_effect=request))).start()
    def rotate_server():
        from app_state import state
        state.server = 'http://127.0.0.1:8000/'
        state._server_ping_success.set()
        
    patch('paradox.client.rotate_server', AsyncMock(side_effect=rotate_server)).start()
    patch('app_state.State.autopersist', Mock()).start()
    gc.collect()
    #if apps:
        #last_app_weakref, last_request = apps.pop()
        #assert last_app_weakref() is None, \
            #'Memory leak: failed to release app for test ' + repr(last_request)

    #import ipdb; ipdb.sset_trace()
    from os import environ
    #environ['KIVY_USE_DEFAULTCONFIG'] = '1'

    # force window size + remove all inputs
    from kivy.config import Config
    #Config.set('graphics', 'width', '320')
    #Config.set('graphics', 'height', '240')
    
    # disable mouse and keyboard
    #for items in Config.items('input'):
        #Config.remove_option('input', items[0])

    from kivy.core.window import Window
    from kivy.context import Context
    from kivy.clock import ClockBase
    from kivy.factory import FactoryBase, Factory
    from kivy.app import App
    from kivy.lang.builder import BuilderBase, Builder
    from kivy.base import stopTouchApp
    from kivy import kivy_data_dir

    #context = Context(init=False)
    #context['Clock'] = ClockBase(async_lib='asyncio')
    #context['Factory'] = FactoryBase.create_from(Factory)
    #context['Builder'] = BuilderBase.create_from(Builder)
    #context.push()

    #Window.create_window()
    #Window.register()
    #Window.initialized = True
    #Window.canvas.clear()


    def aexc_handler(loop, context):
        throw(context['exception'])
        
    
    asyncio.get_running_loop()._kivyrunning = True
    
    def throw(err):
        try:
            asyncio.get_running_loop().stop()
            asyncio.get_running_loop()._kivyrunning = False
        except:
            pass
        #asyncio.get_running_loop().close()
        #global running
        #running = False
        raise err
    patch('paradox.exception_handler.common_exc_handler', throw).start()
    patch('paradox.exception_handler.send_debug_message', Mock()).start()
    
    ###patch('main.aexc_handler', aexc_handler).start()
    ###patch('main.state.autopersist', Mock(side_effect=Exception('err'))).start()
    ###patch('main.state.autopersist', Mock()).start()
    
    from main import ParadoxApp
    class App(UnitKivyApp, ParadoxApp):
        def __init__(self, **kwargs):
            #import ipdb; ipdb.sset_trace()
            ParadoxApp.__init__(self, **kwargs)
            
            ##def started_app(*largs):
                ##self.app_has_started = True
            #self.funbind('on_start')
        user_data_dir = dirname(__file__)
        
        async def wait_clock_frames(self, n, sleep_time=1 / 60.):
            from kivy.clock import Clock
            frames_start = Clock.frames
            while Clock.frames < frames_start + n:
                await sleep(sleep_time)
                    
        async def text_input(self, text):
            for char in text:
                async for x in self.do_keyboard_key(char):
                    pass
                
            await self.wait_clock_frames(20)
                
        async def click(self, widget):
            await sleep(0.1)
            for x in range(20):
                if getattr(widget, 'disabled', False) is False:
                    break
                await sleep(0.1)
            else:
                raise Exception(f'Widget {widget} is disabled')
                
            text = getattr(widget, 'text', '') or getattr(widget, 'hint_text', '')
            logger.debug(f'Click {widget} "{text}"')
            
            parent = widget.parent
            pos = widget.center
            #while parent and hasattr(parent, 'to_parent'):
                #pos = parent.to_parent(*pos)
                #print(pos, parent)
                #parent = parent.parent
                
            touch = UnitTestTouch(
                #window.height - 10, 10
                #*pos
                *widget.to_window(*widget.center)
            )

            # bind something to test the touch with
            #button.bind(
                #on_release=lambda instance: setattr(
                    #instance, 'test_released', True
                #)
            #)

            #if window and window.canvas:
                #window.canvas.ask_update()
                
            # then let's touch the Window's center
            touch.touch_down()
            #if window and window.canvas:
                #window.canvas.ask_update()
            touch.touch_up()
            await self.wait_clock_frames(30)
        
    #Window.create_window()
    #Window.register()
    #Window.initialized = True
    #Window.canvas.clear()

    app = App()
    #app = App()

    #import ipdb; ipdb.sset_trace()
    loop = asyncio.get_event_loop()
    loop.create_task(app.async_run())
    
    #from kivy.clock import Clock
    #Clock._max_fps = 0

    await app.wait_clock_frames(20)
    
    ts = time.perf_counter()
    while loop._kivyrunning and not app.app_has_started:
        await sleep(0.5)
        #print(1)
        #if time.perf_counter() - ts >= 10:
            #raise TimeoutError()

    await app.wait_clock_frames(5)
    

    #import ipdb; ipdb.sset_trace()
    yield app

    stopTouchApp()
    
    #ts = time.perf_counter()
    #while not app.app_has_stopped:
        #await async_sleep(.1)
        #if time.perf_counter() - ts >= 10:
            #raise TimeoutError()

    for child in Window.children[:]:
        Window.remove_widget(child)
    #context.pop()

    # release all the resources
    #del context
    #apps.append((weakref.ref(app), request))
    #del app
    patch.stopall()
    
    gc.collect()
