import sys

from kivy.base import ExceptionManager
from loguru import logger
import kivy

from paradox import config


def send_error_message(message):
    from requests import post
    from urllib.parse import urljoin
    try:
        server = state.get('server', config.SERVER_ADDRESS)
        post(urljoin(server, 'api/v2/errors/'), json={
            'app_id': state.get('app_id', '666'),
            #'hash': md5(_traceback.encode('utf-8')).hexdigest(),
            'timestamp': datetime.utcnow().isoformat(),
            'traceback': message
        })
    except:
        pass
    
    
def common_exc_handler(err):
    """
    Send traceback to server, show error screen.
    """
    if str(err) == 'Event loop stopped before Future completed.':
        return
    _traceback = traceback.format_tb(err.__traceback__)
    message = u''.join(_traceback) + '\n' + repr(err) + '\n' + str(err)
    send_error_message(message)
    logger.error(message)
    from paradox import uix
    uix.screenmgr.show_error_screen(message)
    
    
# Handle errors before kivy event loop is started.
sys.excepthook = lambda type, err, traceback: common_exc_handler(err)


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
    
    common_exc_handler(context['exception'])
    
    
class KivyExcHandler:
    """
    Handle errors during kivy event loop execution.
    """
    def handle_exception(self, err):
        common_exc_handler(err)
        return kivy.base.ExceptionManager.PASS
 
