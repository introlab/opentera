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
        # Default = no access
        print(event)
        return False

    def filter_join_session_event(self, event: messages.JoinSessionEvent):
        # Default = no access
        print(event)
        return False

    def filter_participant_event(self, event: messages.ParticipantEvent):
        # Default = no access
        print(event)
        return False

    def filter_stop_session_event(self, event: messages.StopSessionEvent):
        # Default = no access
        print(event)
        return False

    def filter_user_event(self, event: messages.UserEvent):
        # Default = no access
        print(event)

        if event.user_uuid in self.accessManager.get_accessible_users_uuids():
            return True

        return False
