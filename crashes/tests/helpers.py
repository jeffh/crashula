from django.db import models

def form_fields(form_class):
    "Returns a dict of all fields for a Django Form class, mapped by name."
    return form_class.base_fields

def form_field(form_class, name):
    "Returns field of a Django Form class for a given name."
    return form_class.base_fields[name]

def model_fields(model_class):
    "Returns a dict of all fields for a Django Model class, mapped by name."
    return {f.name:f for f in model_class._meta.fields}

def model_field(model_class, name):
    "Returns a field of a Django Model class for a given name."
    fields = model_class._meta.fields
    for field in fields:
        if field.name == name:
            return field
    raise TypeError('Could not find field {0!r} in {1}'.format(name, model_class.__name__))

class Fields(object):
    """Syntactic sugar around form_field or model_field.

    Allows dot-access to read field values:

        >>> model = Fields(MyModel)
        >>> model.title # returns django db field instance of MyModel.title
        >>> form = Fields(MyForm)
        >>> form.title # return django form field instance of MyForm.title

    Iterating over this object returns all the field objects.
    """
    def __init__(self, cls):
        "Returns a Field object that wraps the given Django Model or Form class."
        self.__cls = cls
        if hasattr(cls, 'base_fields'):
            self.__get_field = form_field
            self.__get_fields = form_fields
        else:
            self.__get_field = model_field
            self.__get_fields = model_fields

    def __getattr__(self, name):
        return self.__get_field(self.__cls, name)

    def __repr__(self):
        return 'Fields({0!r})'.format(self.__cls)

    def __iter__(self):
        return iter(self.__get_fields(self.__cls))

    def __len__(self):
        return len(self.__get_field(self.__cls))

### TODO: move into DB helpers

class FieldBase(object):
    MODEL_CLASS = None
    def __init__(self, **kwargs):
        self.values = kwargs

    def __eq__(self, field):
        assert isinstance(field, self.MODEL_CLASS)
        for name, value in self.values.items():
            field_value = getattr(field, name)
            assert field_value == value, 'assert %r.%s == %r, got %r' % (field, name, value, field_value)
        return True

class RelatedFieldBase(FieldBase):
    def __init__(self, to, **kwargs):
        self.values = kwargs
        self.values['to'] = to

    def __eq__(self, field):
        assert isinstance(field, self.MODEL_CLASS)
        NULL = object()
        for name, value in self.values.items():
            field_value = getattr(field, name, NULL)
            if field_value is NULL:
                field_value = getattr(field.rel, name)
            assert field_value == value, 'assert %r.%s == %r, got %r' % (field, name, value, field_value)
        return True


### Identical field types from django

class ForeignKey(RelatedFieldBase):
    MODEL_CLASS = models.ForeignKey

class ManyToManyField(RelatedFieldBase):
    MODEL_CLASS = models.ManyToManyField

class OneToOneField(RelatedFieldBase):
    MODEL_CLASS = models.OneToOneField

class AutoField(FieldBase):
    MODEL_CLASS = models.AutoField

class BigIntegerField(FieldBase):
    MODEL_CLASS = models.BigIntegerField

# django 1.5 >
if hasattr(models, 'BinaryField'):
    class BinaryField(FieldBase):
        MODEL_CLASS = models.BinaryField

class BooleanField(FieldBase):
    MODEL_CLASS = models.BooleanField

class CharField(FieldBase):
    MODEL_CLASS = models.CharField

class CommaSeparatedIntegerField(FieldBase):
    MODEL_CLASS = models.CommaSeparatedIntegerField

class DateField(FieldBase):
    MODEL_CLASS = models.DateField

class DateTimeField(FieldBase):
    MODEL_CLASS = models.DateTimeField

class DecimalField(FieldBase):
    MODEL_CLASS = models.DecimalField

class EmailField(FieldBase):
    MODEL_CLASS = models.EmailField

class FileField(FieldBase):
    MODEL_CLASS = models.FileField

class FilePathField(FieldBase):
    MODEL_CLASS = models.FilePathField

class FloatField(FieldBase):
    MODEL_CLASS = models.FloatField

class ImageField(FieldBase):
    MODEL_CLASS = models.ImageField

class IntegerField(FieldBase):
    MODEL_CLASS = models.IntegerField

class IPAddressField(FieldBase):
    MODEL_CLASS = models.IPAddressField

class GenericIPAddressField(FieldBase):
    MODEL_CLASS = models.GenericIPAddressField

class NullBooleanField(FieldBase):
    MODEL_CLASS = models.NullBooleanField

class PositiveIntegerField(FieldBase):
    MODEL_CLASS = models.PositiveIntegerField

class PositiveSmallIntegerField(FieldBase):
    MODEL_CLASS = models.PositiveSmallIntegerField

class SlugField(FieldBase):
    MODEL_CLASS = models.SlugField

class SmallIntegerField(FieldBase):
    MODEL_CLASS = models.SmallIntegerField

class TextField(FieldBase):
    MODEL_CLASS = models.TextField

class TimeField(FieldBase):
    MODEL_CLASS = models.TimeField

class URLField(FieldBase):
    MODEL_CLASS = models.URLField

