# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import calendar
import json
import re
import time

from datetime import datetime

from kivy.app import App
from kivy.utils import platform


def open_url(url):
    if platform == 'android':
        from jnius import cast
        from jnius import autoclass
        # import the needed Java class
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Intent = autoclass('android.content.Intent')
        Uri = autoclass('android.net.Uri')

        # create the intent
        intent = Intent()
        intent.setAction(Intent.ACTION_VIEW)
        intent.setData(Uri.parse(url))

        # PythonActivity.mActivity is the instance of the current Activity
        # BUT, startActivity is a method from the Activity class, not from our
        # PythonActivity.
        # We need to cast our class into an activity and use it
        currentActivity = cast('android.app.Activity', PythonActivity.mActivity)
        currentActivity.startActivity(intent)
    elif platform == 'linux':
        import webbrowser
        webbrowser.open(url)


#def utc_to_local(utc_dt):
    ## get integer timestamp to avoid precision lost
    #timestamp = calendar.timegm(utc_dt.timetuple())
    #local_dt = datetime.fromtimestamp(timestamp)
    ###assert utc_dt.resolution >= timedelta(microseconds=1)
    #return local_dt.replace(microsecond=utc_dt.microsecond)


def strptime(string, format):
    try:
        return datetime.strptime(string, format)
    except TypeError:
        # Workaround for http://bugs.python.org/issue27400
        return datetime(*(time.strptime(string, format)[0:6]))
