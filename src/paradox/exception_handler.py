import sys
from urllib.parse import urljoin
from datetime import datetime
from typing import Union
from traceback import format_tb


from app_state import state
from kivy.base import ExceptionManager
from loguru import logger
#from requests import post
import httpx
import kivy

from paradox import config


def send_debug_message(data: Union[Exception, str]):
    if isinstance(data, Exception):
        _traceback = format_tb(data.__traceback__)
        data = ''.join(_traceback) + f'\n {data!r} \n {data!s}'
        
    try:
        server = state.get('server', config.SERVER_ADDRESS)
        httpx.post(urljoin(server, 'api/v3/errors/'), json={
            'app_id': state.get('app_id', '666'),
            'timestamp': datetime.utcnow().isoformat(),
            'traceback': data
        })
    except Exception as e:
        logger.error(f'Failed to send debug message: \n {e!r}')
    
    

def sys_excepthook(err, type=None, traceback=None):
    """
    Send traceback to server, show error screen.
    """
    if str(err) == 'Event loop stopped before Future completed.':
        return

    if config.DEBUG:
        logger.opt(exception=(type, err, traceback)).exception('a')
        raise err
    traceback = u''.join(format_tb(traceback or err.__traceback__))
    message = f"{traceback}\n{err!r}\n{err}"
    logger.exception(err)
    send_debug_message(message)

    # https://github.com/kivy/kivy/issues/8954
    if isinstance(err, ReferenceError):
        return

    from paradox import uix
    uix.screenmgr.show_error_screen(message)
    
    
# Handle errors before kivy event loop is started.
sys.excepthook = lambda type, err, traceback: sys_excepthook(err, type=type, traceback=traceback)


def aioloop_exc_handler(loop, context: dict):
    """
    Handles exceptions in asyncio tasks.
    
    :param: `context` is a dict with keys:
      ‘message’: Error message;
      ‘exception’ (optional): Exception object;
      ‘future’ (optional): asyncio.Future instance;
      ‘handle’ (optional): asyncio.Handle instance;
      ‘protocol’ (optional): Protocol instance;
      ‘transport’ (optional): Transport instance;
      ‘socket’ (optional): socket.socket instance.

    bound by loop.set_exception_handler() in main.py
    """
    
    # TODO: investigate
    # File "/home/u1/.local/share/python-for-android/build/other_builds/python3-libffi-openssl-sqlite3/arm64-v8a__ndk_target_21/python3/Lib/ssl.py", line 763, in do_handshake
    # SSLZeroReturnError(6, 'TLS/SSL connection has been closed (EOF) (_ssl.c:1051)')
    # TLS/SSL connection has been closed (EOF) (_ssl.c:1051)
    
    # TODO: investigate https://bugs.python.org/issue36709 "Asyncio SSL keep-alive connections 
    # raise errors after loop close" - which one is this?
    
    logger.info(context['message'])
    
    # Ignore some known exceptions.
    if 'write error on socket transport' in context['message']:
        return
    if context['message'] in [
        'Event loop stopped before Future completed.',
        'Task was destroyed but it is pending!']:
        return
    
    sys_excepthook(context['exception'])
    
    
class KivyExcHandler:
    """
    Handle errors during kivy event loop execution.
    Assigned by kivy.base.ExceptionManager.add_handler() in main.py
    """
    def handle_exception(self, err):
        sys_excepthook(err)
        return kivy.base.ExceptionManager.PASS
 
