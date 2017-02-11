from __future__ import unicode_literals

import types

from .default import GermaniumTestCase


def convert_to_test_obj(obj):
    obj.change_and_save = types.MethodType(change_and_save, obj)
    obj.reload = types.MethodType(reload, obj)
    return obj


def change_and_save(self, save_kwargs=None, **kwargs):
    save_kwargs = {} if save_kwargs is None else save_kwargs
    for attr, val in kwargs.items():
        setattr(self, attr, val)
    self.save(**save_kwargs)
    return self


def reload(self):
    if self.pk:
        self = self.__class__.objects.get(pk=self.pk)
    convert_to_test_obj(self)
    return self


class ModelTestCase(GermaniumTestCase):

    factory_class = None

    def inst_data_provider(self, **inst_kwargs):
        factory_class = inst_kwargs.pop('factory_class', self.factory_class)
        if 'pk' in inst_kwargs:
            inst = factory_class._get_model_class().objects.get(pk=inst_kwargs.get('pk'))
        else:
            inst = factory_class(**inst_kwargs)
        convert_to_test_obj(inst)
        return inst

    def insts_data_provider(self, count=10, **inst_kwargs):
        insts = []
        for _ in range(count):
            insts.append(self.inst_data_provider(**inst_kwargs))
        return insts
