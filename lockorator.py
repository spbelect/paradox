import trio


locks = {}


class lock_or_exit:
    def __init__(self, name):
        self.name = name
        locks.setdefault(name, trio.Lock())
        
    def __call__(self, f):
        async def wrapped(*a, **kw):
            #import ipdb; ipdb.sset_trace()
            if locks[self.name].locked():
                return
            
            async with locks[self.name]:
                return await f(*a, **kw)
        return wrapped
