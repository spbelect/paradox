#from kivy.utils import platform

CHANGELOG_URL = 'https://bitbucket.org/fak3/paradox/raw/last_version/CHANGELOG.rst'

SERVER_ADDRESS = 'http://127.0.0.1:8000'
#SERVER_ADDRESS = 'https://spbtest-2019.herokuapp.com/'
BACKUP_SERVER_ADDRESS = 'http://127.0.0.1:8000'

SERVER_GISTS = [
    #'https://gist.githubusercontent.com/Fak3/4dce12f2d09f74e4ba1779794baa5f3c/raw/gistfile1.txt',
    #'https://gist.githubusercontent.com/Fak3/cd3baed54162b2849916dce886d7d1ce/raw/gistfile1.txt'
]
    
HAS_BACKUP_SERVER = True
SHOW_TEST_COORDINATORS = False

DEBUG = True

#if platform == 'linux':
    #SENTRY = False

from loguru import logger
#logger.disable("paradox.client")
# logger.disable("paradox.uix.quiz_widgets.base")
