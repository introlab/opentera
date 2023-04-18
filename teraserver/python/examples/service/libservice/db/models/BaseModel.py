from opentera.db.Base import BaseMixin
from sqlalchemy.ext.declarative import declarative_base


# Declarative base, inherit from Base for all models
BaseModel = declarative_base(cls=BaseMixin)