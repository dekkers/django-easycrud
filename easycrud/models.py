from django.db import models
from django.db.models.base import ModelBase
from django.core.urlresolvers import reverse
from .utils import classproperty


class EasyCrudOptions(object):
    actions = ["create", "update", "delete"]
    exclude = []
    inline_models = []
    owner_ref = None

    def __init__(self, opts=None, **kwargs):
        if opts:
            opts = [(k, v) for k, v in opts.__dict__.items() if not k.startswith('__')]
        else:
            opts = []
        opts.extend(kwargs.items())
        for key, value in opts:
            setattr(self, key, value)

    def __iter__(self):
        return iter([(k, v) for (k, v) in self.__dict__.items() if not k.startswith('_')])


class EasyCrudModelBase(ModelBase):
    def __new__(cls, name, bases, attrs):
        EasyCrudMeta = attrs.pop('EasyCrudMeta', type('EasyCrudMeta', (), {}))

        for base in bases:
            if hasattr(base, '_easycrud_meta'):
                for (key, value) in base._easycrud_meta:
                    if not hasattr(EasyCrudMeta, key):
                        setattr(EasyCrudMeta, key, value)

        attrs['_easycrud_meta'] = EasyCrudOptions(EasyCrudMeta)
        return super(EasyCrudModelBase, cls).__new__(cls, name, bases, attrs)


class EasyCrudModel(models.Model):
    __metaclass__ = EasyCrudModelBase

    class Meta:
        abstract = True

    @classmethod
    def _get_model_url(cls, action):
        viewname = '%s_%s' % (cls.__name__.lower(), action)
        return reverse(viewname)

    def _get_object_url(self, action):
        viewname = '%s_%s' % (self.__class__.__name__.lower(), action)
        return reverse(viewname, args=[str(self.pk)])

    @classproperty
    @classmethod
    def create_url(cls):
        return cls._get_model_url('create')

    @property
    def detail_url(self):
        return self._get_object_url('detail')

    @property
    def update_url(self):
        return self._get_object_url('update')

    @property
    def delete_url(self):
        return self._get_object_url('delete')

    @classproperty
    @classmethod
    def has_create(cls):
        return "create" in cls._easycrud_meta.actions

    @classproperty
    @classmethod
    def has_update(cls):
        return "update" in cls._easycrud_meta.actions

    @classproperty
    @classmethod
    def has_delete(cls):
        return "delete" in cls._easycrud_meta.actions

    @classproperty
    @classmethod
    def model_name(cls):
        return cls._meta.verbose_name

    @classproperty
    @classmethod
    def model_name_plural(cls):
        return cls._meta.verbose_name_plural

    def get_absolute_url(self):
        return self.detail_url
