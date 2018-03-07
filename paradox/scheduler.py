# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys

from importlib import import_module

import six

from kivy.clock import Clock


def import_string(dotted_path):
    """
    Copied from Django.
    Import a dotted module path and return the attribute/class designated by the
    last name in the path. Raise ImportError if the import failed.
    """
    try:
        module_path, class_name = dotted_path.rsplit('.', 1)
    except ValueError:
        msg = "%s doesn't look like a module path" % dotted_path
        six.reraise(ImportError, ImportError(msg), sys.exc_info()[2])

    module = import_module(module_path)

    try:
        return getattr(module, class_name)
    except AttributeError:
        msg = 'Module "%s" does not define a "%s" attribute/class' % (
            module_path, class_name)
        six.reraise(ImportError, ImportError(msg), sys.exc_info()[2])


def schedule(task, *args, **kwargs):
    if isinstance(task, (str, unicode)):
        task = import_string('paradox.' + task)
    timeout = kwargs.pop('timeout', 0)
    Clock.schedule_once(lambda *a: task(*args, **kwargs), timeout)
