from flask_sqlalchemy import SQLAlchemy
import inspect
import datetime

db = SQLAlchemy()


class BaseModel:

    def to_json(self, ignore_fields=None):
        if ignore_fields is None:
            ignore_fields = []
        pr = {}
        for name in dir(self):
            value = getattr(self, name)
            if not name.startswith('__') and not inspect.ismethod(value) and not inspect.isfunction(value) and not \
                    name.startswith('_') and not name.startswith('query') and not name.startswith('metadata') and \
                    name not in ignore_fields:
                if isinstance(value, datetime.datetime):
                    value = value.isoformat()
                pr[name] = value
        return pr
