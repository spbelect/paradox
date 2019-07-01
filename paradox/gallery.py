#from plyer.facades import Gallery
#import jnius
#from android import activity
#from android import autoclass
#import threading
#from time import sleep

#Intent = autoclass('android.content.Intent')
#PythonActivity = autoclass('org.renpy.android.PythonActivity')
#Uri = autoclass('android.net.Uri')

#CompressFormat = autoclass('android.graphics.Bitmap$CompressFormat')
#BitmapFactory = autoclass('android.graphics.BitmapFactory')
#FileInputStream = autoclass('java.io.FileInputStream')
#FileOutputStream = autoclass('java.io.FileOutputStream')
#BufferedOutputStream = autoclass('java.io.BufferedOutputStream')
#ContentResolver = PythonActivity.mActivity.getContentResolver()
#Version = autoclass('android.os.Build$VERSION')


class AndroidGallery():

    def _choose_image(self, on_complete, filename=None):
        assert(on_complete is not None)
        self.on_complete = on_complete
        self.filename = filename

        activity.unbind(on_activity_result=self.on_activity_result)
        activity.bind(on_activity_result=self.on_activity_result)
        intent = Intent(Intent.ACTION_PICK)
        intent.setType("image/jpeg")
        intent.putExtra(Intent.EXTRA_ALLOW_MULTIPLE, True)
        #intent.putExtra(Intent.EXTRA_LOCAL_ONLY, True)
        #intent.putExtra(Intent.CATEGORY_OPENABLE, True)
        PythonActivity.mActivity.startActivityForResult(
            Intent.createChooser(intent, autoclass(
                'java.lang.String')("Select Picture")), 0x100)

    def on_activity_result(self, requestCode, resultCode, intent):
        activity.unbind(on_activity_result=self.on_activity_result)

        if requestCode != 0x100:
            return

        if resultCode != -1:
            self.on_complete([], True)
            return

        uri = []
        data = intent.getClipData()
        if not data:
            return
        for x in range(data.getItemCount()):
            item = data.getItemAt(x)
            urI = item.getUri()
            uri.append(urI)

        PythonActivity.toastError("Loading {} image/s".format(len(uri)))
        print('calling get path form uri ', uri)
        th = threading.Thread(target=self._get_path_from_URI, args=[uri])
        th.start()

    def _get_path_from_URI(self, uris):
        # return a list of all the uris converted to their paths
        ret = []
        for count, uri in enumerate(uris):
            scheme = uri.getScheme()
            if scheme == 'content':
                PythonActivity.toastError('Loading file {}'.format(count + 1))
                try:
                    cursor = ContentResolver.query(
                            uri, None, None, None, None)
                    if cursor.moveToFirst():
                        index = cursor.getColumnIndexOrThrow('_data')
                        uri = Uri.parse(cursor.getString(index))
                        pth = uri.getPath()
                        if pth:
                            ret.append(pth)
                except Exception as e:
                    print('ScramPhoto: {}'.format(e))
                    parcelFileDescriptor = ContentResolver.openFileDescriptor(uri, 'r')
                    file_nm, ext = self.filename.rsplit('.')
                    filename = file_nm[:-1] + str(int(file_nm[-1]) + 1) + '.' + ext
                    self.filename = filename
                    output = BufferedOutputStream(FileOutputStream(filename))
                    bitmap = BitmapFactory.decodeFileDescriptor(parcelFileDescriptor.getFileDescriptor())
                    bitmap.compress(CompressFormat.JPEG, 100, output)
                    ret.append(filename)
                    continue
            elif scheme != 'file':
                continue
        self.on_complete(ret, False)
        #jnius.detach()
        sleep(2000000)





from kivy.logger import Logger
from kivy.clock import Clock

def user_select_image(callback):
    """Open Gallery Activity and call callback with absolute image filepath of image user selected.
    None if user canceled.
    """


    from jnius import autoclass
    from jnius import cast

    # python-for-android provides this
    from android import activity

    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Intent = autoclass('android.content.Intent')
    Uri = autoclass('android.net.Uri')

    # Value of MediaStore.Images.Media.DATA
    MediaStore_Images_Media_DATA = "_data"

    # Custom request codes
    RESULT_LOAD_IMAGE = 1

    Activity = autoclass('android.app.Activity')
    # Activity is only used to get these codes. Could just hardcode them.
        # /** Standard activity result: operation canceled. */
        # public static final int RESULT_CANCELED    = 0;
        # /** Standard activity result: operation succeeded. */
        # public static final int RESULT_OK           = -1;
        # /** Start of user-defined activity results. */
        # Not sure what this means
        # public static final int RESULT_FIRST_USER   = 1;



    # PythonActivity.mActivity is the instance of the current Activity
    # BUT, startActivity is a method from the Activity class, not from our
    # PythonActivity.
    # We need to cast our class into an activity and use it
    currentActivity = cast('android.app.Activity', PythonActivity.mActivity)

    # Forum discussion: https://groups.google.com/forum/#!msg/kivy-users/bjsG2j9bptI/-Oe_aGo0newJ
    def on_activity_result(request_code, result_code, intent):
        if request_code != RESULT_LOAD_IMAGE:
            Logger.warning('user_select_image: ignoring activity result that was not RESULT_LOAD_IMAGE')
            return

        if result_code == Activity.RESULT_CANCELED:
            Clock.schedule_once(lambda dt: callback(None), 0)
            return

        if result_code != Activity.RESULT_OK:
            # This may just go into the void...
            raise NotImplementedError('Unknown result_code "{}"'.format(result_code))

        selectedImage = intent.getData();  # Uri
        print(selectedImage.toString())
        #filePathColumn = [MediaStore_Images_Media_DATA]; # String[]
        ## Cursor
        #cursor = currentActivity.getContentResolver().query(
            #selectedImage, filePathColumn, None, None, None);
        #cursor.moveToFirst();

        ## int
        #columnIndex = cursor.getColumnIndex(filePathColumn[0]);
        ## String
        #picturePath = cursor.getString(columnIndex);
        #cursor.close();
        #Logger.info('android_ui: user_select_image() selected %s', picturePath)

        # This is possibly in a different thread?
        Clock.schedule_once(lambda dt: callback(selectedImage.toString()), 0)

    # See: http://pyjnius.readthedocs.org/en/latest/android.html
    activity.bind(on_activity_result=on_activity_result)

    #env = autoclass('android.os.Environment')
    #print(env.getExternalStoragePublicDirectory(env.DIRECTORY_DCIM).getPath())
    
    intent = Intent()

    # http://programmerguru.com/android-tutorial/how-to-pick-image-from-gallery/
    # http://stackoverflow.com/questions/18416122/open-gallery-app-in-android
    intent.setAction(Intent.ACTION_PICK)
    #intent.setAction(Intent.ACTION_GET_CONTENT)
    #intent.setType("image/*")
    #intent.putExtra(Intent.EXTRA_LOCAL_ONLY, True);

    # TODO internal vs external?
    intent.setData(Uri.parse('content://media/internal/images/media'))
    # TODO setType(Image)?

    currentActivity.startActivityForResult(intent, RESULT_LOAD_IMAGE)
    
    
