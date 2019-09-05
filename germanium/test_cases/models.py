from .default import GermaniumTestCase


class ModelTestCase(GermaniumTestCase):

    factory_class = None

    def inst_data_provider(self, **inst_kwargs):
        factory_class = inst_kwargs.pop('factory_class', self.factory_class)
        if 'pk' in inst_kwargs:
            inst = factory_class._meta.model.objects.get(pk=inst_kwargs.get('pk'))
        else:
            inst = factory_class(**inst_kwargs)
        return inst

    def insts_data_provider(self, count=10, **inst_kwargs):
        insts = []
        for _ in range(count):
            insts.append(self.inst_data_provider(**inst_kwargs))
        return insts
