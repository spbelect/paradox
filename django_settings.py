#from environ import Env
INSTALLED_APPS = ['paradox'] 

SECRET_KEY = 'o294qynv5o9q2n'

USE_I18N = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite'
    }
}
