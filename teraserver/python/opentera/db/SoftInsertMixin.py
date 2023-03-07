from sqlalchemy.inspection import inspect
from sqlalchemy import text


class SoftInsertMixin:

    @classmethod
    # Returns the id of the object inserted
    def soft_insert(cls, db_object):
        primary_key_name = inspect(db_object.__class__).primary_key[0].name
        # Check if we have an already present deleted association and, if so, restores it
        # Get foreign keys for that object
        foreign_keys = list(inspect(db_object.__class__).tables[0].foreign_keys)

        # Check if object already exists
        query = db_object.query.execution_options(include_deleted=True)
        for key in foreign_keys:
            # query = query.filter(key == getattr(db_object, key.parent.name))
            value = getattr(db_object, key.parent.name)
            if value:
                query = query.filter(text(key.parent.name + '=' + str(value)))
            else:
                query = query.filter(text(key.parent.name + '=NULL'))
        item = query.first()

        if item:
            # Undelete that item only
            if getattr(item, 'deleted_at', None):
                setattr(item, 'deleted_at', None)
            cls.commit()
            return item
        else:
            # Insert item
            setattr(db_object, primary_key_name, None)
            cls.db().session.add(db_object)
            cls.commit()
            return db_object

        # item = TeraDeviceParticipant.query_device_participant_for_participant_device(device_id=db_object.id_device,
        #                                                                              participant_id=
        #                                                                              db_object.id_participant,
        #                                                                              with_deleted=True)
        # if item:
        #     if item.deleted_at:
        #         item.deleted_at = None
        #
        # else:
        #     # No existing item found
