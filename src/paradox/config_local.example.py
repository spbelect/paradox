#from kivy.utils import platform

CHANGELOG_URL = 'https://bitbucket.org/fak3/paradox/raw/last_version/CHANGELOG.rst'

# SERVER_ADDRESS = 'http://127.0.0.1:8000'
SERVER_ADDRESS = ''

SHOW_TEST_COORDINATORS = False

DEBUG = True

#if platform == 'linux':
    #SENTRY = False

from loguru import logger
#logger.disable("paradox.client")
# logger.disable("paradox.uix.quiz_widgets.base")
