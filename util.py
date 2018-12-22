
import trio
from kivy.app import App


def nurse(f):
    def wrapped(*a, **kw):
        App.get_running_app().nursery.start_soon(f, *a, **kw)
        return True
    return wrapped
        

def delay(f, *a, timeout=0.1, **kw):
    async def _delay():
        if timeout:
            await trio.sleep(timeout)
        return await f(*a, **kw)
    App.nursery.start_soon(_delay)
