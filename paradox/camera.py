#from .gallery import resolve
#from paradox import client
from loguru import logger

RESULT_CANCELED = 0;
RESULT_OK = -1;
        
def take_picture(filepath, on_complete):
    from jnius import autoclass
    from jnius import cast
    from android import activity
    from paradox import client
    
    
    Intent = autoclass('android.content.Intent')
    PythonActivity = autoclass('org.renpy.android.PythonActivity')
    currentActivity = cast('android.app.Activity', PythonActivity.mActivity)
    MediaStore = autoclass('android.provider.MediaStore')
    FileProvider = autoclass('android.support.v4.content.FileProvider')
    Uri = autoclass('android.net.Uri')
    File = autoclass('java.io.File')

    def on_activity_result(requestCode, resultCode, intent):
        if requestCode != 0x123:
            client.send_debug(f'got {requestCode}')
            return
        
        activity.unbind(on_activity_result=on_activity_result)
        
        if resultCode == RESULT_CANCELED:
            return
        
        if resultCode != RESULT_OK:
            # This may just go into the void...
            raise NotImplementedError(f'Unknown result_code "{resultCode}"')
        
        on_complete(filepath)
    
    activity.unbind(on_activity_result=on_activity_result)
    activity.bind(on_activity_result=on_activity_result)
    intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
    file = File('file://' + filepath)
    #print(file)
    #uri = Uri.parse('file://' + filepath)
    photoURI = FileProvider.getUriForFile(
        currentActivity, "org.spbelect.paradox2.fileprovider", file
    );
    logger.debug(photoURI)
    #parcelable = cast('android.os.Parcelable', uri)
    intent.putExtra(MediaStore.EXTRA_OUTPUT, cast('java.lang.String', photoURI))
    currentActivity.startActivityForResult(intent, 0x123)


 
