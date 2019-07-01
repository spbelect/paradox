#!/usr/bin/env python
from os.path import expanduser, join
import os
import sys

if __name__ == "__main__":
    data_dir = os.environ.get('XDG_CONFIG_HOME', '~/.config')
    os.environ['DBDIR'] = expanduser(join(data_dir, 'paradox'))
    
    if os.path.exists('django_settings_local.py'):
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_settings_local")
    else:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_settings")

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
