#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    if os.path.exists('django_settings_local.py'):
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_settings_local")
    else:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_settings")

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
