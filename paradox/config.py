CHANGELOG_URL = 'https://bitbucket.org/fak3/paradox/raw/last_version/CHANGELOG.rst'

SERVER_ADDRESS = 'http://127.0.0.1:8000'
BACKUP_SERVER_ADDRESS = 'http://127.0.0.1:8000'

HAS_BACKUP_SERVER = True
DEBUG = False

SENTRY = True

version = '1.7'

try:
    from .config_local import *
except ImportError:
    pass
