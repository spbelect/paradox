
#from kivy.uix.camera import Camera
#from kivy.graphics.texture import Texture
#import cv2


#Builder.load_string('''
##:include constants.kv

##:import state app_state.state


##SmartCamera:
    ##id: camera
    ##resolution: (640, 480)
    ###resolution: (480, 640)
    ##play: True
    ##size: '100dp', '200dp'
       
##<SmartCamera>:
    ##canvas.before:
        ##PushMatrix
        ##Rotate:
            ##angle: root.rotate
            ##origin: self.center
    ##canvas.after:
        ##PopMatrix

        ##Color:
            ##rgba: 1,0,0,0.5
        ##Rectangle:
            ##pos: self.pos
            ##size: self.size
#''')

#class SmartCamera(Camera):
    #rotate = NumericProperty(0)

    #def __init__(self, *args, **kwargs):
        #super(SmartCamera, self).__init__(*args, **kwargs)
        #if platform != 'android':
            ##self.rotate = 90
            ##w, h = self.resolution
            ##if w > h:
                ##self.resolution = h, w
            ##self.rotate = 0
            #print self.size
            ##self.width, self.height


    ##def _camera_loaded(self, *largs):
        ##if platform != 'android':
            ##self.texture = Texture.create(size=self.resolution, colorfmt='rgb')
            ##self.texture_size = list(self.texture.size)
        ##else:
            ##super(CvCamera, self)._camera_loaded()

    ##def on_tex(self, *l):
        ###import ipdb; ipdb.set_trace()
        ##if platform != 'android':
            ##buf = self._camera.grab_frame()
            ###if not buf:
                ###return super(CvCamera, self).on_tex(*l)
            ##frame = self._camera.decode_frame(buf)
            ###buf = self.process_frame(frame)
            ##self.texture.blit_buffer(buf, colorfmt='rgb', bufferfmt=b'ubyte')
        ##super(CvCamera, self).on_tex(*l)

    #def process_frame(self, frame):
        ## Process frame with opencv
        #return cv2.flip(frame, 1).tostring()
 
