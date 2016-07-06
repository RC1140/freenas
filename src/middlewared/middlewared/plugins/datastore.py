from middlewared.service import Service

import os
import sys

sys.path.append('/usr/local/www')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freenasUI.settings')

from django.core import serializers
# Make sure to load all modules
from django.db.models.loading import cache
cache.get_apps()


class DatastoreService(Service):

    def _filters_to_queryset(self, filters):
        opmap = {
            '=': 'exact',
            '>': 'gt',
            '>=': 'gte',
            '<': 'lt',
            '<=': 'lte',
        }

        rv = {}
        for f in filters:
            if len(f) == 3:
                name, op, value = f
                if op not in opmap:
                    raise Exception("Invalid operation {0}".format(op))
                rv['{0}__{1}'.format(name, opmap[op])] = value
            else:
                raise Exception("Invalid filter {0}".format(f))
        return rv

    def __get_model(self, name):
        """Helper method to get Model for given name
        e.g. network.interfaces -> Interfaces
        """
        app, model = name.split('.', 1)
        return cache.get_model(app, model)

    def __queryset_serialize(self, qs):
        for i in qs:
            entry = i.__dict__
            entry.pop('_state')
            yield entry

    def query(self, name, filters=None):
        model = self.__get_model(name)

        qs = model.objects.all()
        if filters:
            qs = qs.filter(**self._filters_to_queryset(filters))

        return list(self.__queryset_serialize(qs))

    def insert(self, name, data):
        """
        Insert a new entry to 'name'.

        returns: primary key
        """
        model = self.__get_model(name)
        obj = model(**data)
        obj.save()
        return obj.pk
