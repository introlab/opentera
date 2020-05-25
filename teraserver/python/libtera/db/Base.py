from flask_sqlalchemy import SQLAlchemy, event
import inspect
import datetime
# import uuid
import time

db = SQLAlchemy()


class BaseModel:

    version_id = db.Column(db.BigInteger, nullable=False, default=time.time()*1000)

    # Using timestamp as version tracker - multiplying by 1000 to keep ms part without using floats (which seems to
    # cause problems with the mapper)
    __mapper_args__ = {
        'version_id_col': version_id,
        'version_id_generator': lambda version: time.time()*1000  # uuid.uuid4().hex
    }

    def to_json(self, ignore_fields=None):
        if ignore_fields is None:
            ignore_fields = []
        pr = {}
        for name in dir(self):
            if not name.startswith('__') and not name.startswith('_') and not name.startswith('query') and \
                    not name.startswith('metadata') and name != 'version_id' and name not in ignore_fields:
                value = getattr(self, name)
                if not inspect.ismethod(value) and not inspect.isfunction(value):
                    if isinstance(value, datetime.datetime):
                        value = value.isoformat()
                    pr[name] = value
        return pr

    def from_json(self, json):
        for name in json:
            if hasattr(self, name):
                setattr(self, name, json[name])
            else:
                print('Attribute ' + name + ' not found.')

    @classmethod
    def clean_values(cls, values: dict):
        # This method is used to remove item from the values dict that are not properties of the object
        obj_properties = list()

        # Build available properties
        for name in dir(cls):
            value = getattr(cls, name)
            if not name.startswith('__') and not inspect.ismethod(value) and not inspect.isfunction(value) and not \
                    name.startswith('_') and not name.startswith('query') and not name.startswith('metadata'):
                obj_properties.append(name)

        # Remove any property not in the available list
        clean_values = values.copy()
        for value in values:
            if value not in obj_properties:
                del clean_values[value]

        return clean_values

    @classmethod
    def get_count(cls):
        count = db.session.query(cls).count()
        return count

    @classmethod
    def get_primary_key_name(cls):
        from sqlalchemy import inspect
        return inspect(cls).primary_key[0].name

    @classmethod
    def update(cls, update_id: int, values: dict):
        values = cls.clean_values(values)
        update_obj = cls.query.filter(getattr(cls, cls.get_primary_key_name()) == update_id).first()  # .update(values)
        update_obj.from_json(values)
        db.session.commit()

    @classmethod
    def insert(cls, db_object):
        # Clear primary key value
        setattr(db_object, cls.get_primary_key_name(), None)

        # Add to database session and commit
        db.session.add(db_object)
        db.session.commit()

    @classmethod
    def delete(cls, id_todel):
        delete_obj = cls.query.filter(getattr(cls, cls.get_primary_key_name()) == id_todel).first()
        db.session.delete(delete_obj)
        db.session.commit()

    @classmethod
    def query_with_filters(cls, filters=None):
        if filters is None:
            filters = dict()
        # return cls.query.filter_by(**filters).all()

        query = cls.query

        # Direct elements from that model
        for filter_item in filters:
            if filter_item.key() in dir(cls) and filter_item is not None:
                # Filter item is a direct property
                query = query.filter_by(**filter_item)
            else:
                # Check for joined models
                pass

        return query.all()



