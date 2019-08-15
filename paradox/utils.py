# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import asyncio
import base64
import calendar
import hashlib
import json
import re
import time

from functools import wraps
from asyncio import create_task, sleep
from inspect import iscoroutinefunction
from datetime import datetime
from loguru import logger

#from kivy.app import App
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


def md5_file(file_name, chunk_size=4096):
    """
    Sometimes the files can be large to fit in memory. So it would
    be good to chunk the file and update the hash.
    This function will read 4096 bytes sequentially and
    feed them to the Md5 function

    :param chunk_size: The chunk size to the file read
    :param file_name: The path of the file
    :return: base64-encoded MD5 hash of the file
    """
    hash_md5 = hashlib.md5()
    with open(file_name, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
 
 
def asynced(f):
    @wraps(f)
    def wrapper(*a, **kw):
        delay(f, *a, timeout=0, **kw)
    return wrapper

def delay(f, *a, timeout=0.1, **kw):
    async def _delay():
        if timeout:
            await sleep(timeout)
        if iscoroutinefunction(f):
            return await f(*a, **kw)
        else:
            return f(*a, **kw)
    create_task(_delay())


async def ask_permissions(*permissions):
    import android
    if android.api_version <= 22:
        return True
    grantresults = []
    got_result = asyncio.Event()
    
    def permissionresult(permissions, grants):
        logger.debug(f'{permissions} {grants}')
        grantresults.extend(grants)
        got_result.set()
        
    from android.permissions import request_permissions, Permission
    request_permissions([getattr(Permission, x) for x in permissions], callback=permissionresult)
    await got_result.wait()
    return all(grantresults)
    
