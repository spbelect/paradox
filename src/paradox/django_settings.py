import os

#from environ import Env
INSTALLED_APPS = ['paradox'] 

SECRET_KEY = 'o294qynv5o9q2n'

USE_I18N = False
USE_TZ = True
#TIME_ZONE = 'Europe/Moscow'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.environ['DBDIR'] + '/db.sqlite'
    }
}
