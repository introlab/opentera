from modules.EventManager import EventManager
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraParticipant import TeraParticipant
from libtera.db.models.TeraDevice import TeraDevice
from libtera.db.models.TeraAsset import TeraAsset
from modules.DatabaseModule.DBManagerTeraUserAccess import DBManagerTeraUserAccess
import messages.python as messages


class UserEventManager(EventManager):
    def __init__(self, user: TeraUser):
        EventManager.__init__(self)
        self.user = user
        self.accessManager = DBManagerTeraUserAccess(self.user)

    def filter_device_event(self, event: messages.DeviceEvent):
        # If uuid is accessible, return true
        if event.device_uuid in self.accessManager.get_accessible_devices_uuids():
            return True
        # Not accessible
        return False

    def filter_join_session_event(self, event: messages.JoinSessionEvent):
        # Check if we are invited
        if self.user.user_uuid in event.session_users:
            return True
        # Not accessible
        return False

    def filter_participant_event(self, event: messages.ParticipantEvent):
        # If uuid is accessible, return true
        if event.participant_uuid in self.accessManager.get_accessible_participants_uuids():
            return True

        # Not accessible
        return False

    def filter_stop_session_event(self, event: messages.StopSessionEvent):
        # Default = no access
        # TODO How to we keep track of session ids?
        return True

    def filter_user_event(self, event: messages.UserEvent):
        # If uuid is accessible, return true
        if event.user_uuid in self.accessManager.get_accessible_users_uuids():
            return True

        # Not accessible
        return False

    def filter_database_event(self, event: messages.DatabaseEvent):
        import json
        # Default = no access
        try:
            if event.object_type == TeraUser.get_model_name():
                user = TeraUser()
                user.from_json(json.loads(event.object_value))
                # Minimal ->we have only id_user
                if user.id_user in self.accessManager.get_accessible_users_ids():
                    return True
            elif event.object_type == TeraParticipant.get_model_name():
                participant = TeraParticipant()
                participant.from_json(json.loads(event.object_value))
                # Minimal ->we have only id_participant
                if participant.id_participant in self.accessManager.get_accessible_participants_ids():
                    return True
            elif event.object_type == TeraDevice.get_model_name():
                device = TeraDevice()
                device.from_json(json.loads(event.object_value))
                # Minimal ->we have only id_device
                if device.id_device in self.accessManager.get_accessible_devices_ids():
                    return True
            elif event.object_type == TeraAsset.get_model_name():
                # TODO Verify asset access
                asset = TeraAsset()
                asset.from_json(json.loads(event.object_value))
                # if asset.asset_uuid in self.accessManager.get_accessible_assets_uuid():
                #   return True
                return False
        except json.JSONDecodeError as e:
            print('JSON Decode Error', e)
            return False
        finally:
            return False
