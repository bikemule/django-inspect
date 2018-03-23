from six import string_types
import inspect

from django.db import models


def get_all_related_objects(model):
    try:
        return model._meta.get_all_related_objects()
    except AttributeError:
        return [
            f for f in model._meta.get_fields() if
            (f.one_to_many or f.one_to_one) and
            f.auto_created and not f.concrete
        ]

def get_all_related_m2m_objects_with_model(obj):
    return  [
        (f, f.model if f.model != obj.__class__ else None)
        for f in obj._meta.get_fields(include_hidden=True)
        if f.many_to_many and f.auto_created
    ]

def get_all_related_many_to_many_objects(opts):
    return [f for f in opts.get_fields(include_hidden=True) if f.many_to_many and f.auto_created]

def get_compat_local_fields(obj):
    return obj._meta.get_fields()


class Inspect(object):
    """
    Provides inspection conveniences for django models.
    """

    def __init__(self, model):
        if not inspect.isclass(model):
            model = model.__class__
        if not issubclass(model, models.Model):
            raise TypeError("{} is not a django model".format(model.__name__))
        self._setup_ready = False
        self.model = model
        self.opts = model._meta

    def __getattr__(self, name):
        if not self._setup_ready:
            self._setup()
        return super(Inspect, self).__getattribute__(name)

    def _field_info(self, field):
        return field.name, field

    def _backwards_field_info(self, field):
        return field.get_accessor_name(), field.field

    def _setup_fields(self, backwards, fields):
        if backwards:
            field_info = self._backwards_field_info
            fk_list = self.backwards_fk_fields
            m2m_list = self.backwards_m2m_fields
        else:
            field_info = self._field_info
            fk_list = self.fk_fields
            m2m_list = self.m2m_fields
        for field in fields:
            name, field = field_info(field)
            if not backwards:
                self.fields.append(name)
            if isinstance(field, models.ForeignKey):
                fk_list.append(name)
                self.all_fk_fields.append(name)
            elif isinstance(field, models.ManyToManyField):
                m2m_list.append(name)
                self.all_m2m_fields.append(name)
            else:
                self.non_rel_fields.append(name)
            self.all_fields.append(name)

    def _setup_local_fields(self):
        local_fields = tuple(self.opts.local_fields)
        many_to_many = tuple(self.opts.many_to_many[:])
        self._setup_fields(False, local_fields + many_to_many)

    def _setup_backwards_fields(self):
        self._setup_fields(True, get_all_related_objects(self.model)
                           + get_all_related_many_to_many_objects(self.opts))

    def _setup(self):
        self.fields = []

        self.non_rel_fields = []

        self.fk_fields = []
        self.m2m_fields = []

        self.backwards_fk_fields = []
        self.backwards_m2m_fields = []

        self.all_fk_fields = []
        self.all_m2m_fields = []

        self.all_fields = []

        self._setup_local_fields()
        self._setup_backwards_fields()

        self._setup_ready = True

    def sub_inspect(self, path):
        if isinstance(path, string_types):
            path = path.split(".")
        fieldname = path.pop(0)
        try:
            descriptor = getattr(self.model, fieldname)
        except AttributeError:
            raise TypeError("{model}.{field} does not exist"
                            " or is not a relationship".format(model=self.model.__name__,
                                                               field=fieldname))
        if hasattr(descriptor, "field"):
            model = descriptor.field.rel.to
        else:
            model = descriptor.related.field.model
        inspect = self.__class__(model)
        if path:
            return inspect.sub_inspect(path)
        return inspect
