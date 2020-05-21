from modules.EventManager import EventManager
from libtera.db.models.TeraUser import TeraUser
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
        # TODO how do we verify the invitation
        return True

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
