# -*- coding: utf-8 -*-

from sqlalchemy import Integer
from sqlalchemy.types import TypeDecorator
from sqlalchemy.ext.declarative import DeclarativeMeta
import enum
import json
import numbers


class EnumType(TypeDecorator):
    """Store IntEnum as Integer"""

    impl = Integer

    def __init__(self, *args, **kwargs):
        self.enum_class = kwargs.pop('enum_class')
        TypeDecorator.__init__(self, *args, **kwargs)

    def process_bind_param(self, value, dialect):
        if value is not None:
            if not isinstance(value, self.enum_class):
                raise TypeError("Value should %s type" % self.enum_class)
            return value.value

    def process_result_value(self, value, dialect):
        if value is not None:
            if not isinstance(value, int):
                if isinstance(value, numbers.Number):
                    int(value)
                else:
                    raise TypeError("value should have int type")
            return self.enum_class(value)


def recursive_alchemy_encoder(revisit_self=False, fields_to_expand=[]):
    """ http://stackoverflow.com/questions/5022066/how-to-serialize-sqlalchemy-result-to-json """

    _visited_objs = []

    class AlchemyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj.__class__, DeclarativeMeta):
                # don't re-visit self
                if revisit_self:
                    if obj in _visited_objs:
                        return None
                    _visited_objs.append(obj)

                # go through each field in this SQLalchemy class
                fields = {}
                for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                    val = obj.__getattribute__(field)

                    if isinstance(val, enum.Enum):
                        val = val.name

                    # is this field another SQLalchemy object, or a list of SQLalchemy objects?
                    elif isinstance(val.__class__, DeclarativeMeta) or (isinstance(val, list) and len(val) > 0 and isinstance(val[0].__class__, DeclarativeMeta)):
                        # unless we're expanding this field, stop here
                        if field not in fields_to_expand:
                            # not expanding this field: set it to None and continue
                            fields[field] = None
                            continue

                    else:
                        try:
                            json.dumps(val) # this will fail on non-encodable values, like other classes
                        except TypeError:
                            val = None

                    # a json-encodable dict
                    fields[field] = val

                return fields

            return json.JSONEncoder.default(self, obj)
    return AlchemyEncoder

    # _visited_objs = []
    #
    # class AlchemyEncoder(json.JSONEncoder):
    #     def default(self, obj):
    #         if isinstance(obj.__class__, DeclarativeMeta):
    #             # don't re-visit self
    #             if obj in _visited_objs:
    #                 return None
    #             _visited_objs.append(obj)
    #
    #             # an SQLAlchemy class
    #             fields = {}
    #             for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
    #                 # fields[field] = obj.__getattribute__(field)
    #                 data = obj.__getattribute__(field)
    #                 if isinstance(data, enum.Enum):
    #                     data = data.name
    #                 try:
    #                     json.dumps(data) # this will fail on non-encodable values, like other classes
    #                     fields[field] = data
    #                 except TypeError:
    #                     fields[field] = None
    #
    #             # a json-encodable dict
    #             return fields
    #
    #         return json.JSONEncoder.default(self, obj)
    # return AlchemyEncoder
