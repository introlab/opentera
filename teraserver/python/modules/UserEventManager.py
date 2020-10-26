from modules.EventManager import EventManager
import libtera.db.models as models
from modules.DatabaseModule.DBManagerTeraUserAccess import DBManagerTeraUserAccess
import messages.python as messages


class UserEventManager(EventManager):
    def __init__(self, user: models.TeraUser):
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

    def filter_leave_session_event(self, event: messages.LeaveSessionEvent):
        # Check if we are in that session or not
        if models.TeraSession.is_user_in_session(event.session_uuid, self.user.user_uuid):
            return True
        # Not accessible
        return False

    def filter_join_session_reply_event(self, event: messages.JoinSessionReplyEvent):
        # Check if we are in that session or not
        if models.TeraSession.is_user_in_session(event.session_uuid, self.user.user_uuid) \
                and event.user_uuid != self.user.user_uuid:
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
        from libtera.db.models import EventNameClassMap

        try:
            if event.object_type in EventNameClassMap:
                # Create instance
                obj = EventNameClassMap[event.object_type]()
                # Load from json
                obj.from_json(json.loads(event.object_value))

                # No way to determine if we can access this message
                # This should return minimal information
                if event.type == messages.DatabaseEvent.DB_DELETE:
                    return True

                # Any other type (UPDATE, CREATE) will verify if we can access first
                # TODO can we do better than test each type?
                if event.object_type == models.TeraUser.get_model_name():
                    if obj.id_user in self.accessManager.get_accessible_users_ids():
                        return True
                elif event.object_type == models.TeraParticipant.get_model_name():
                    if obj.id_participant in self.accessManager.get_accessible_participants_ids():
                        return True
                elif event.object_type == models.TeraDevice.get_model_name():
                    if obj.id_device in self.accessManager.get_accessible_devices_ids():
                        return True
                elif event.object_type == models.TeraUserGroup.get_model_name():
                    if obj.id_user_group in self.accessManager.get_accessible_users_groups_ids():
                        return True
                elif event.object_type == models.TeraSession.get_model_name():
                    if self.accessManager.query_session(obj.id_session):
                        return True
                elif event.object_type == models.TeraProject.get_model_name():
                    if obj.id_project in self.accessManager.get_accessible_projects_ids():
                        return True
                elif event.object_type == models.TeraSite.get_model_name():
                    if obj.id_site in self.accessManager.get_accessible_sites_ids():
                        return True
                elif event.object_type == models.TeraAsset.get_model_name():
                    # TODO Verify asset access
                    # if asset.asset_uuid in self.accessManager.get_accessible_assets_uuid():
                    #   return True
                    return False
        except json.JSONDecodeError as e:
            print('JSON Decode Error', e)
            return False

        # Default = no access
        return False
