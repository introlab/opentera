"""
Functions related to dynamic generation of the soft-delete mixin.
Adapted from:
https://github.com/flipbit03/sqlalchemy-easy-softdelete
"""

from datetime import datetime
from typing import Any, Callable, Optional, Type

from sqlalchemy import Column, DateTime, text
from sqlalchemy.inspection import inspect
from sqlalchemy.sql.type_api import TypeEngine
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.event import listens_for
from sqlalchemy.orm import ORMExecuteState, Session
from sqlalchemy.engine import Engine, Connection
from sqlalchemy.sql import Select

from functools import cache

from opentera.db.SoftDeleteQueryRewriter import SoftDeleteQueryRewriter


@cache
def activate_soft_delete_hook(deleted_field_name: str, disable_soft_delete_option_name: str):
    """Activate an event hook to rewrite the queries."""
    # Enable Soft Delete on all Relationship Loads which implement SoftDeleteMixin
    # @listens_for(Session, "do_orm_execute")
    # def soft_delete_execute(state: ORMExecuteState):
    #     if not state.is_select:
    #         return
    #     if 'include_deleted' in state.session.info and len(state.session.info['include_deleted']) > 0:
    #         print('test_include_deleted')
    #         return
    #
    #     adapted = SoftDeleteQueryRewriter(deleted_field_name, disable_soft_delete_option_name).rewrite_statement(
    #         state.statement
    #     )
    #     state.statement = adapted
    @listens_for(Engine, "before_execute", retval=True)
    def soft_delete_execute(conn: Connection, clauseelement, multiparams, params, execution_options):
        if not isinstance(clauseelement, Select):
            return clauseelement, multiparams, params

        if disable_soft_delete_option_name in execution_options and execution_options[disable_soft_delete_option_name]:
            print('test_include_deleted')
            return clauseelement, multiparams, params

        adapted = SoftDeleteQueryRewriter(deleted_field_name, disable_soft_delete_option_name).rewrite_statement(
            clauseelement
        )
        return adapted, multiparams, params


def generate_soft_delete_mixin_class(
    deleted_field_name: str = "deleted_at",
    class_name: str = "_SoftDeleteMixin",
    deleted_field_type: TypeEngine = DateTime(timezone=True),
    disable_soft_delete_filtering_option_name: str = "include_deleted",
    generate_delete_method: bool = True,
    delete_method_name: str = "delete",
    delete_method_default_value: Callable[[], Any] = lambda: datetime.utcnow(),
    generate_undelete_method: bool = True,
    undelete_method_name: str = "undelete",
    handle_cascade_delete: bool = True
) -> Type:
    """Generate the actual soft-delete Mixin class."""
    class_attributes = {deleted_field_name: Column(deleted_field_name, deleted_field_type)}

    def get_class_from_tablename(_self, tablename: str) -> DeclarativeMeta | None:
        for mapper in _self.registry.mappers:
            if mapper.class_.__tablename__ == tablename:
                return mapper.class_
        return None

    class_attributes['get_class_from_tablename'] = get_class_from_tablename

    if generate_delete_method:

        def delete_method(_self, v: Optional[Any] = None):
            setattr(_self, deleted_field_name, v or delete_method_default_value())
            if handle_cascade_delete:
                primary_key_name = inspect(_self.__class__).primary_key[0].name
                for relation in inspect(_self.__class__).relationships.items():
                    # Relationship has a cascade delete or a secondary table
                    if relation[1].cascade.delete:
                        # Item has a delete_at field (thus supports soft-delete)
                        if deleted_field_name in relation[1].entity.columns.keys():
                            # Cascade soft delete for each item
                            for item in getattr(_self, relation[0]):
                                item_deleter = getattr(item, delete_method_name)
                                item_deleter()
                    if relation[1].secondary is not None:
                        # Item has a delete_at field (thus supports soft-delete)
                        if deleted_field_name in relation[1].entity.columns.keys():
                            model_class = _self.get_class_from_tablename(relation[1].secondary.name)
                            if model_class:
                                related_items = model_class.query.filter(text(primary_key_name + "=" +
                                                                              str(getattr(_self, primary_key_name)))
                                                                         ).all()
                                for item in related_items:
                                    item_deleter = getattr(item, delete_method_name)
                                    item_deleter()

        class_attributes[delete_method_name] = delete_method

    if generate_undelete_method:

        def undelete_method(_self):
            if handle_cascade_delete:
                primary_key_name = inspect(_self.__class__).primary_key[0].name
                for relation in inspect(_self.__class__).relationships.items():
                    if relation[1].cascade.delete:  # Relationship has a cascade delete
                        # Item has a delete_at field (thus supports soft-delete)
                        if deleted_field_name in relation[1].entity.columns.keys():
                            # Cascade undelete - must manually query to get deleted rows
                            related_items = relation[1].entity.class_.query.execution_options(include_deleted=True).\
                                filter(text(primary_key_name + '=' + str(getattr(_self, primary_key_name)))).all()
                            for item in related_items:
                                item_undeleter = getattr(item, undelete_method_name)
                                item_undeleter()
                    if relation[1].secondary is not None:
                        # Item has a delete_at field (thus supports soft-delete)
                        if deleted_field_name in relation[1].entity.columns.keys():
                            model_class = _self.get_class_from_tablename(relation[1].secondary.name)
                            if model_class:
                                related_items = model_class.query.filter(text(primary_key_name + '=' +
                                                                              str(getattr(_self, primary_key_name)))
                                                                         ).execution_options(include_deleted=True).all()
                                for item in related_items:
                                    item_undeleter = getattr(item, undelete_method_name)
                                    item_undeleter()

            setattr(_self, deleted_field_name, None)

        class_attributes[undelete_method_name] = undelete_method

    activate_soft_delete_hook(deleted_field_name, disable_soft_delete_filtering_option_name)

    generated_class = type(class_name, tuple(), class_attributes)

    return generated_class


# Create a Class that inherits from our class builder
class SoftDeleteMixin(generate_soft_delete_mixin_class(delete_method_name='soft_delete',
                                                       undelete_method_name='soft_undelete')):
    # type hint for autocomplete IDE support
    deleted_at: datetime


