
from collections.abc import Iterable

async def retry(fn, *args, **kw):
    for x in range(30):
        res = fn(*args, **kw)
        if res:
            return res
        await sleep(0.1)
    else:
        raise Exception(f'retry failed: {fn} {args!r} {kw!r}')


async def wait_instance(widget, **kwargs):
    for x in range(30):
        res = list(widget.instances.filter(**kwargs))
        if res:
            return res[0]
        await sleep(0.1)
    else:
        raise Exception(f'No such widget: {widget} {kwargs!r}')


#async def wait_result(callable, *args, **kwargs):
    #for x in range(30):
        #res = callable(*args, **kwargs)
        #if res:
            #return res
        #await sleep(0.1)
    #else:
        #raise Exception(f'No such widget: {callable}, *args, **kwargs')

#def props(**kw):
    #return


async def wait_listitem(iterable: Iterable, **kwargs):
    """
    Wait for any item in the given iterable to have matching attributes provided
    in kwargs. Return first matching item or raise Exception on timeout.

    Example below waits for a child widget of mywidget, which has attribute called
    'text' with value 'mytext', and then return it:

    >> child = await wait_listitem(mywidget.children, text='mytext')

    """
    for x in range(30):
        for item in iterable:
            if all((getattr(item, k) == v) for k, v in kwargs.items()):
                return item
        await sleep(0.1)
    else:
        raise Exception(f'No such widget: {iterable} {kwargs!r}')
