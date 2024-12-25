#from kivy.utils import platform

CHANGELOG_URL = 'https://bitbucket.org/fak3/paradox/raw/last_version/CHANGELOG.rst'

# SERVER_ADDRESS = 'http://127.0.0.1:8000'
SERVER_ADDRESS = ''

# If True, state.server will be forced to equal config.SERVER_ADDRESS
# on start. Previously persisted server value from state db is ignored.
# Useful for local development. On android should be set to False.
FORGET_STORED_STATE_SERVER = False


SHOW_TEST_COORDINATORS = False

DEBUG = True

#if platform == 'linux':
    #SENTRY = False

from loguru import logger
#logger.disable("paradox.client")
# logger.disable("paradox.uix.quiz_widgets.base")
