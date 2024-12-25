CHANGELOG_URL = 'https://bitbucket.org/fak3/paradox/raw/last_version/CHANGELOG.rst'

# SERVER_ADDRESS must be defined in config_android.py or config_local.py
SERVER_ADDRESS = None

# If True, state.server will be forced to equal config.SERVER_ADDRESS
# on start. Previously persisted server value from state db is ignored.
# Useful for local development. On android should be set to False.
FORGET_STORED_STATE_SERVER = False

MAX_SERVER_ERRORS = 20

SHOW_TEST_COORDINATORS = False
DEBUG = False

SENTRY = True


from pathlib import Path
SRCDIR = Path(__file__).parent

version = '2.2'

from kivy.utils import platform

if platform == 'android':
    from .config_android import *
else:
    try:
        from .config_local import *
    except ImportError:
        pass
