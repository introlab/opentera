from modules.EventManager import EventManager
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraSession import TeraSession
from modules.DatabaseModule.DBManagerTeraParticipantAccess import DBManagerTeraParticipantAccess
import opentera.messages.python as messages


class ParticipantEventManager(EventManager):
    def __init__(self, participant: TeraParticipant):
        EventManager.__init__(self)
        self.participant = participant
        self.accessManager = DBManagerTeraParticipantAccess(self.participant)

    def filter_device_event(self, event: messages.DeviceEvent):

        # Device is associated with participant?
        device = TeraDevice.get_device_by_uuid(event.device_uuid)
        if device:
            for participant in device.device_participants:
                if participant.participant_uuid == self.participant.participant_uuid:
                    return True

        # Not accessible
        return False

    def filter_join_session_event(self, event: messages.JoinSessionEvent):
        # Check if we are invited
        if self.participant.participant_uuid in event.session_participants:
            return True
        # Not accessible
        return False

    def filter_participant_event(self, event: messages.ParticipantEvent):
        # Only accept events to current participant
        if event.participant_uuid == self.participant.participant_uuid:
            return True

        # Not accessible
        return False

    def filter_stop_session_event(self, event: messages.StopSessionEvent):
        # TODO How to we keep track of session ids?
        return True

    def filter_leave_session_event(self, event: messages.LeaveSessionEvent):
        # Check if we are in that session or not
        if TeraSession.is_participant_in_session(event.session_uuid, self.participant.participant_uuid):
            return True
        # Not accessible
        return False

    def filter_join_session_reply_event(self, event: messages.JoinSessionReplyEvent):
        # Check if we are in that session or not
        if TeraSession.is_participant_in_session(event.session_uuid, self.participant.participant_uuid)  \
                and event.participant_uuid != self.participant.participant_uuid:
            return True
        # Not accessible
        return False

    def filter_user_event(self, event: messages.UserEvent):
        # Not accessible
        return False

    def filter_database_event(self, event: messages.DatabaseEvent):
        # Default = no access
        return False
