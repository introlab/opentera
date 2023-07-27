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
from sqlalchemy.exc import IntegrityError

from functools import cache

from opentera.db.SoftDeleteQueryRewriter import SoftDeleteQueryRewriter


@cache
def activate_soft_delete_hook(deleted_field_name: str, disable_soft_delete_option_name: str):
    """Activate an event hook to rewrite the queries."""
    # Enable Soft Delete on all Relationship Loads which implement SoftDeleteMixin
    @listens_for(Session, "do_orm_execute")
    def soft_delete_execute(state: ORMExecuteState):
        if not state.is_select:
            return

        if disable_soft_delete_option_name in state.execution_options \
                and state.execution_options[disable_soft_delete_option_name]:
            return

        if 'include_deleted' in state.session.info and len(state.session.info['include_deleted']) > 0:
            return

        adapted = SoftDeleteQueryRewriter(deleted_field_name, disable_soft_delete_option_name).rewrite_statement(
            state.statement
        )
        state.statement = adapted
    # @listens_for(Engine, "before_execute", retval=True)
    # def soft_delete_execute(conn: Connection, clauseelement, multiparams, params, execution_options):
    #     if not isinstance(clauseelement, Select):
    #         return clauseelement, multiparams, params
    #
    #     if disable_soft_delete_option_name in execution_options and execution_options[disable_soft_delete_option_name]:
    #         # print('test_include_deleted')
    #         return clauseelement, multiparams, params
    #
    #     adapted = SoftDeleteQueryRewriter(deleted_field_name, disable_soft_delete_option_name).rewrite_statement(
    #         clauseelement
    #     )
    #     return adapted, multiparams, params


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
    handle_cascade_delete: bool = True,
    generate_hard_delete_method: bool = True,
    hard_delete_method_name: str = "hard_delete"
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

    if generate_hard_delete_method:
        def hard_delete_method(_self):
            _self.handle_include_deleted_flag(True)
            # Callback actions before doing hard delete, if required
            if getattr(_self, 'hard_delete_before', None):
                _self.hard_delete_before()
            if handle_cascade_delete:
                primary_key_name = inspect(_self.__class__).primary_key[0].name
                for relation in inspect(_self.__class__).relationships.items():
                    # Relationship has a cascade delete or a secondary table
                    if relation[1].cascade.delete:
                        for item in getattr(_self, relation[0]):
                            # print("Cascade deleting " + str(item))
                            hard_item_deleter = getattr(item, hard_delete_method_name)
                            hard_item_deleter()

                    if relation[1].secondary is not None and relation[1].passive_deletes:
                        if deleted_field_name in relation[1].entity.columns.keys():
                            model_class = _self.get_class_from_tablename(relation[1].secondary.name)
                            if model_class:
                                related_items = model_class.query.filter(text(primary_key_name + "=" +
                                                                              str(getattr(_self, primary_key_name)))
                                                                         ).execution_options(include_deleted=True).all()
                                for item in related_items:
                                    # print("Cascade deleting " + str(model_class) + ": " + primary_key_name + " = " +
                                    #       str(getattr(_self, primary_key_name)))
                                    item_hard_deleter = getattr(item, hard_delete_method_name)
                                    item_hard_deleter()

            if _self not in _self.db().session.deleted:
                _self.db().session.delete(_self)
                _self.commit()
            _self.handle_include_deleted_flag(False)

        class_attributes[hard_delete_method_name] = hard_delete_method

    if generate_undelete_method:
        def get_undelete_cascade_relations(_self) -> list:
            return []  # By default, no relationships are automatically undeleted when undeleting

        class_attributes['get_undelete_cascade_relations'] = get_undelete_cascade_relations

        def undelete_method(_self):
            if not getattr(_self, deleted_field_name):
                print("Object " + str(_self.__class__) + " not deleted - returning.")
                return

            current_obj = inspect(_self.__class__)
            primary_key_name = current_obj.primary_key[0].name

            # Check data integrity before undeleting
            for col in current_obj.columns:
                if not col.foreign_keys:
                    continue
                # If column foreign key is not nullable or there is a value for this object, we must check if
                # related object is still there
                col_value = getattr(_self, col.name, None)
                if not col.nullable or col_value:
                    remote_table_name = list(col.foreign_keys)[0].column.table.name
                    model_class = _self.get_class_from_tablename(remote_table_name)
                    remote_key_name = list(col.foreign_keys)[0].column.key
                    related_item = model_class.query.filter(text(remote_key_name + '="' + str(col_value) + '"')).first()
                    if not related_item:
                        # A required object isn't there (soft-deleted) - throw exception to undelete it first!
                        raise IntegrityError('Cannot undelete: unsatisfied foreign key - ' + col.name, col_value,
                                             remote_table_name)
            # Undelete!
            # print("Undeleting " + str(_self.__class__))
            setattr(_self, deleted_field_name, None)

            # Check relationships that are cascade deleted to restore them
            if handle_cascade_delete:
                for relation in inspect(_self.__class__).relationships.items():
                    # Relationship has a cascade undelete ?
                    if relation[1].key in _self.get_undelete_cascade_relations():
                        # Item has a delete_at field (thus supports soft-delete)
                        if deleted_field_name in relation[1].entity.columns.keys():
                            # Cascade undelete - must manually query to get deleted rows
                            remote_primary_key = list(relation[1].remote_side)[0].name
                            local_primary_key = list(relation[1].local_columns)[0].name
                            self_key_value = getattr(_self, local_primary_key)
                            if not self_key_value:
                                continue
                            related_items = relation[1].entity.class_.query.execution_options(include_deleted=True).\
                                filter(text(remote_primary_key + '=' + str(self_key_value))).all()
                            for item in related_items:
                                # print("--> Undeleting relationship " + relation[1].key)
                                item_undeleter = getattr(item, undelete_method_name)
                                item_undeleter()
                            continue

                    # Check secondary relationships and restore them if both ends are now undeleted
                    if relation[1].secondary is not None:
                        if deleted_field_name in relation[1].entity.columns.keys():
                            model_class = _self.get_class_from_tablename(relation[1].secondary.name)
                            related_items = model_class.query.execution_options(include_deleted=True).\
                                filter(text(primary_key_name + '=' + str(getattr(_self, primary_key_name)))).all()
                            for item in related_items:
                                # Check if other side of the relationship is present and, if so, restores it
                                remote_primary_key = relation[1].target.primary_key.columns[0].name
                                remote_model = _self.get_class_from_tablename(relation[1].target.name)
                                remote_item = remote_model.query.filter(
                                    text(remote_primary_key + '=' + str(getattr(item, remote_primary_key)))).first()
                                if remote_item:
                                    #  print("--> Undeleting relationship with " + relation[1].target.name)
                                    item_undeleter = getattr(item, undelete_method_name)
                                    item_undeleter()

            # _self.handle_include_deleted_flag(True)
            # setattr(_self, deleted_field_name, None)
            # print("Undeleting " + str(_self.__class__))
            # if handle_cascade_delete:
            #     primary_key_name = inspect(_self.__class__).primary_key[0].name
            #     for relation in inspect(_self.__class__).relationships.items():
            #         print(str(_self.__class__) + " - relation " + str(relation))
            #         if relation[1].secondary is not None:
            #             print("-> Undeleting secondary table relationship " + relation[1].secondary.name)
            #             # Item has a delete_at field (thus supports soft-delete)
            #             if deleted_field_name in relation[1].entity.columns.keys():
            #                 model_class = _self.get_class_from_tablename(relation[1].secondary.name)
            #                 if model_class:
            #                     related_items = model_class.query.filter(text(primary_key_name + '=' +
            #                                                                   str(getattr(_self, primary_key_name)))
            #                                                              ).execution_options(include_deleted=True).all()
            #                     for item in related_items:
            #                         item_undeleter = getattr(item, undelete_method_name)
            #                         item_undeleter()
            #
            #                         # Undelete "left-side" item of the relationship
            #                         remote_primary_key = relation[1].target.primary_key.columns[0].name
            #                         remote_model = _self.get_class_from_tablename(relation[1].target.name)
            #                         remote_item = remote_model.query.filter(text(remote_primary_key + '=' +
            #                                                                      str(getattr(item, remote_primary_key)))
            #                                                                 ).execution_options(include_deleted=True)\
            #                             .first()
            #                         if remote_item:
            #                             print("--> Undeleting left side of secondary table " + relation[1].target.name)
            #                             item_undeleter = getattr(remote_item, undelete_method_name)
            #                             item_undeleter()
            #
            #                     continue
            #         # Check for parents or related items
            #         if relation[1].back_populates:
            #             print("--> Undeleting back_populates relationship " + str(relation[1]))
            #             # if relation[1].cascade.delete:  # Relationship has a cascade delete
            #             # Item has a delete_at field (thus supports soft-delete)
            #             if deleted_field_name in relation[1].entity.columns.keys():
            #                 # Cascade undelete - must manually query to get deleted rows
            #                 remote_primary_key = list(relation[1].remote_side)[0].name
            #                 local_primary_key = list(relation[1].local_columns)[0].name
            #                 self_key_value = getattr(_self, local_primary_key)
            #                 if not self_key_value:
            #                     continue
            #                 related_items = relation[1].entity.class_.query.execution_options(include_deleted=True).\
            #                     filter(text(remote_primary_key + '=' + str(self_key_value))).all()
            #                 for item in related_items:
            #                     item_undeleter = getattr(item, undelete_method_name)
            #                     item_undeleter()
            #                 continue
            #         print("Skipped undelete")
            #     _self.handle_include_deleted_flag(False)

        class_attributes[undelete_method_name] = undelete_method

    activate_soft_delete_hook(deleted_field_name, disable_soft_delete_filtering_option_name)

    generated_class = type(class_name, tuple(), class_attributes)

    return generated_class


# Create a Class that inherits from our class builder
class SoftDeleteMixin(generate_soft_delete_mixin_class(delete_method_name='soft_delete',
                                                       undelete_method_name='soft_undelete')):
    # type hint for autocomplete IDE support
    deleted_at: datetime


