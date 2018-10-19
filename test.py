from kivy.tests.common import GraphicUnitTest, UnitTestTouch
from unittest import TestCase


def x(self):
    #import ipdb; ipdb.sset_trace()
    self.test_released = True
    
class XXTestCase(GraphicUnitTest):

    def test_render(self):
        from kivy.uix.button import Button

        # with GraphicUnitTest.render() you basically do this:
        # runTouchApp(Button()) + some setup before
        button = Button()
        self.render(button)

        # get your Window instance safely
        from kivy.base import EventLoop
        EventLoop.ensure_window()
        window = EventLoop.window

        touch = UnitTestTouch(
            *[s / 2.0 for s in window.size]
        )

        # bind something to test the touch with
        button.bind(on_release=x)
        #button.bind(
            #on_release=lambda instance: setattr(
                #instance, 'test_released', True
            #)
        #)

        # then let's touch the Window's center
        touch.touch_down()
        touch.touch_up()
        self.assertTrue(button.test_released)
        
class ZZMyTestCase(GraphicUnitTest):

    def test_render(self):
        from main import ParadoxApp

        # with GraphicUnitTest.render() you basically do this:
        # runTouchApp(Button()) + some setup before
        app = ParadoxApp()
        app.root = app.build()
        #runTouchApp()
        self.render(app.root)

        # get your Window instance safely
        from kivy.base import EventLoop
        EventLoop.ensure_window()
        window = EventLoop.window

        from paradox.uix.screens.formlist_screen import FormListScreen
        
        mb = FormListScreen.objects.get().ids['menu_button']
        
        #import ipdb; ipdb.sset_trace()
        #touch = UnitTestTouch(
            #*[s / 2.0 for s in window.size]
        #)
        touch = UnitTestTouch(
            #window.height - 10, 10
            *mb.to_window(*mb.center)
        )

        # bind something to test the touch with
        #button.bind(
            #on_release=lambda instance: setattr(
                #instance, 'test_released', True
            #)
        #)

        # then let's touch the Window's center
        touch.touch_down()
        touch.touch_up()
        
        self.render(app.root, 20)
        
        from time import sleep
        sleep(10)
        #self.assertTrue(button.test_released)
 
