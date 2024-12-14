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
    
    

def sys_excepthook(err, traceback=None):
    """
    Send traceback to server, show error screen.
    """
    if str(err) == 'Event loop stopped before Future completed.':
        return

    traceback = u''.join(format_tb(traceback or err.__traceback__))
    message = f"{traceback}\n{err!r}\n{err}"
    send_debug_message(message)
    logger.exception(err)

    # https://github.com/kivy/kivy/issues/2458
    #
    # 2024-12-07 14:45:23.425 | ERROR    | paradox.exception_handler:sys_excepthook:44 -   File "kivy/_clock.pyx", line 649, in kivy._clock.CyClockBase._process_events
    #   File "kivy/_clock.pyx", line 218, in kivy._clock.ClockEvent.tick
    #   File "/home/z/pproj/paradox_dev/.venv/lib64/python3.12/site-packages/kivy/animation.py", line 364, in _update
    #     setattr(widget, key, value)
    #   File "kivy/weakproxy.pyx", line 35, in kivy.weakproxy.WeakProxy.__setattr__
    #   File "kivy/weakproxy.pyx", line 28, in kivy.weakproxy.WeakProxy.__ref__
    #
    # ReferenceError('weakly-referenced object no longer exists')
    # weakly-referenced object no longer exists
    #
    # ipdb> widget
    # <WeakProxy to None>
    # ipdb> self
    # <kivy.animation.Animation object at 0x7f08f88f8d70>
    # ipdb> key
    # 'x'
    # ipdb> isinstance(widget, WeakProxy)
    # True
    # ipdb> len(dir(widget))
    # 0
    # ipdb> isinstance(widget, WeakProxy) and not len(dir(widget))
    # True

    # TODO: Seems to be non-disruptive
    if isinstance(err, ReferenceError):
        return

    from paradox import uix
    uix.screenmgr.show_error_screen(message)
    
    
# Handle errors before kivy event loop is started.
sys.excepthook = lambda type, err, traceback: sys_excepthook(err, traceback)


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
 
