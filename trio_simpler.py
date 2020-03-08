#'''Example shows the recommended way of how to run Kivy with a trio
#event loop as just another async coroutine.
#'''
#import asks
#import os
#import sys
#import trio


#os.environ['KIVY_EVENTLOOP'] = 'trio'
#asks.init('trio')

#from kivy.app import App
#from kivy.lang.builder import Builder
#from kivy.uix.button import Button
#from kivy.resources import resource_add_path
    
#if getattr(sys, 'frozen', False):
    ## we are running in a PyInstaller windows bundle
    #bundle_dir = sys._MEIPASS
    #logging.info(bundle_dir)
#else:
    ## we are running in a normal Python environment
    #bundle_dir = os.path.dirname(os.path.abspath(__file__))

#kv = '''
#BoxLayout:
    #orientation: 'vertical'
    ##MyButton:
        ##id: btn
        ##text: 'Press me'
    ##Label:
        ##id: label
#'''

#class MyButton(Button):
    #async def on_release(self):
        #""" Download file reporting progress """
        #self.disabled = True
        #url = 'https://apod.nasa.gov/apod/image/1705/Arp273Main_HubblePestana_3079.jpg'
        #downloaded = 0
        #response = await asks.get(url, stream=True)
        #async for chunk in response.body:
            #downloaded += len(chunk)
            #App.root.ids.label.text = "got %s of %s" % (downloaded, response.headers['content-length'])
        #self.disabled = False
            

#class MyApp(App):
    #async def async_run(self):
        #resource_add_path(bundle_dir + '/paradox/uix/')
        #from paradox.uix.true_none_false import TrueNoneFalse
        #App.root = self.root = Builder.load_string(kv)
        #App.root.add_widget(TrueNoneFalse(json={
            #"help_text": "ст. 30, п. 1\n1. На всех заседаниях комиссии, ",
            #"input_type": "YESNO",
            #"extra_tag": None,
            #"question_id": "5275ae82-e2c1-4351-a52c-caf7922bd728",
            #"label": "В помещении остались только члены УИК и лица, зарегистрированные в реестре"
        #}))
        #await super().async_run()


#if __name__ == '__main__':
    #trio.run(MyApp().async_run)
 
