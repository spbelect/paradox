
import trio
from app_state import state
#from kivy.app import App


def nurse(f):
    def wrapped(*a, **kw):
        state._nursery.start_soon(f, *a, **kw)
        return True
    return wrapped
        

def delay(f, *a, timeout=0.1, **kw):
    async def _delay():
        if timeout:
            await trio.sleep(timeout)
        return await f(*a, **kw)
    state._nursery.start_soon(_delay)
