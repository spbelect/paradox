CHANGELOG_URL = 'https://bitbucket.org/fak3/paradox/raw/last_version/CHANGELOG.rst'

SERVER_ADDRESS = 'http://127.0.0.1:8000'
MAX_SERVER_ERRORS = 20

SHOW_TEST_COORDINATORS = False
DEBUG = False

SENTRY = True


from pathlib import Path
SRCDIR = Path(__file__).parent

version = '2.2'

try:
    from .config_local import *
except ImportError:
    pass
