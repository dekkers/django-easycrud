from django.conf import settings
from django.forms.models import ModelForm, ModelFormMetaclass
from django.utils.importlib import import_module

import imp


class FormClassCache(object):
    """
    A cache that stores all form classes that inherent from EasyCrudForm, used
    to lookup form classess that are declared on models. Using the Form class
    directly isn't possible because that would result in circular imports.

    Loosely based on django's model AppCache.
    """
    form_classes = {}
    loaded = False

    def __init__(self):
        raise RuntimeError("This class should never be instantiated")

    @classmethod
    def _populate(cls):
        if cls.loaded:
            return

        imp.acquire_lock()
        try:
            if cls.loaded:
                return
            for app_name in settings.INSTALLED_APPS:
                try:
                    import_module('.forms', app_name)
                except ImportError:
                    pass
            cls.loaded = True
        finally:
            imp.release_lock()

    @classmethod
    def get_form_class(cls, name):
        cls._populate()
        return cls.form_classes[name]

    @classmethod
    def register_form_class(cls, name, form_class):
        if name in cls.form_classes:
            raise ValueError("Form class with name %s already registered")
        else:
            cls.form_classes[name] = form_class

get_form_class = FormClassCache.get_form_class


class EasyCrudFormMetaclass(ModelFormMetaclass):
    def __new__(cls, name, bases, attrs):
        form_class = super(EasyCrudFormMetaclass, cls).__new__(cls, name, bases, attrs)
        FormClassCache.register_form_class(name, form_class)
        return form_class


class EasyCrudForm(ModelForm):
    __metaclass__ = EasyCrudFormMetaclass
