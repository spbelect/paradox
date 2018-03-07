# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from weakref import WeakSet
from kivy._event import EventDispatcher


class ObjectsManager(object):
    def __init__(self, cls):
        self.cls = cls

    def get(self, **kwargs):
        for instance in self.cls._instances:
            match = True
            for attr in kwargs:
                if not hasattr(instance, attr) or \
                   not getattr(instance, attr) == kwargs[attr]:
                    match = False
                    break
            if match:
                return instance

    def all(self):
        return self.cls._instances


def objects_manager(cls):
    def __new__(subcls, *args, **kwargs):
        instance = super(cls, subcls).__new__(subcls, *args, **kwargs)
        cls._instances.add(instance)
        return instance
    cls.__new__ = staticmethod(__new__)
    cls._instances = WeakSet()
    cls.objects = ObjectsManager(cls)
    return cls
