
from hashlib import md5
from itertools import chain

from kivy.network.urlrequest import UrlRequest

from ..scheduler import schedule


server = 'http://127.0.0.1:8000'
backup_server = 'http://127.0.0.1:8000'
sentry_server = 'http://127.0.0.1:8000'
getter_started = False


def get_server(name):
    #return 'http://127.0.0.1:8000'
    global getter_started
    if not getter_started:
        getter_started = True
        schedule('net.release.getserver_loop')

    if name == 'primary':
        return server
    elif name == 'sentry':
        return sentry_server
    else:
        return backup_server


def on_g_error(request, error):
    schedule('net.release.getserver_loop', timeout=5 * 60)


def on_g_success(request, result):
    global server
    server = result.strip()
    ##print server
    schedule('net.release.getserver_loop', timeout=5 * 60)


def on_bak_success(request, result):
    global backup_server
    backup_server = result.strip()
    #print 'bak', backup_server


def on_sentry_success(request, result):
    global sentry_server
    sentry_server = result.strip()
    #print 'sen', sentry_server


def on_ch_success(request, result):
    g_url = 'https://gist.githubusercontent.com/Fak3/4dce12f2d09f74e4ba1779794baa5f3c/raw/gistfile1.txt'
    UrlRequest(
        g_url,
        timeout=20,
        on_success=on_g_success,
        on_error=on_g_error,
        on_failure=on_g_error)

    b_url = 'https://gist.githubusercontent.com/Fak3/cd3baed54162b2849916dce886d7d1ce/raw/gistfile1.txt'
    UrlRequest(b_url, timeout=20, on_success=on_bak_success)

    s_url = 'https://gist.githubusercontent.com/Fak3/c70a243f4adbe76cb0253e5d74aff23e/raw/gistfile1.txt'
    UrlRequest(s_url, timeout=20, on_success=on_sentry_success)


def on_ch_error(request, error):
    schedule('net.release.getserver_loop', timeout=9)


def getserver_loop():
    ch_url = 'https://bitbucket.org/fak3/paradox/raw/last_version/CHANGELOG.rst'
    UrlRequest(
        ch_url,
        timeout=20,
        on_success=on_ch_success,
        on_error=on_ch_error,
        on_failure=on_ch_error)

x1 = 't'
x3 = 'm'
x6 = 'a'
x7 = 'p'


def make_packet(packet):
    z = 'di_'
    f = 'ppa'
    x = str(packet[(z + f)[::-1]]) + packet[x1 + 'i' + x3 + 'e' + 's' + x1 + x6 + x3 + x7]
    y = 724256347
    hh = 83582627823547224923546 % 1361724712718385691
    #print y, hh
    gg = ''.join(chain(*zip(x, str(y) + str(hh))))
    filler = md5(gg).hexdigest()
    return dict(packet, hash=filler)
