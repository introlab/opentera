from modules.BaseModule import BaseModule, ModuleNames
from services.VideoDispatch.ConfigManager import ConfigManager
from messages.python.TeraMessage_pb2 import TeraMessage
from messages.python.UserEvent_pb2 import UserEvent
from messages.python.ParticipantEvent_pb2 import ParticipantEvent
from messages.python.DeviceEvent_pb2 import DeviceEvent
from enum import Enum, unique
from datetime import datetime
from uuid import uuid4


@unique
class ParticipantStateNames(Enum):
    OFFLINE = str("OFFLINE")
    ONLINE = str("ONLINE")
    IN_SESSION = str("IN_SESSION")


class ParticipantDispatchState:
    def __init__(self, uuid: str, info: dict = {}, state: ParticipantStateNames = ParticipantStateNames.ONLINE):
        self._uuid = uuid
        self._state = state
        self._info = info
        self._timestamp = datetime.now()

    def get_state(self):
        return self._state

    def set_state(self, state):
        self._state = state

    def get_info(self):
        return self._info

    def set_info(self, info):
        self._info = info

    def get_timestamp(self):
        return self._timestamp

    def get_uuid(self):
        return self._uuid

    def __eq__(self, other):
        return other.uuid == self.uuid

    def __repr__(self):
        return '<ParticipantDispatchState uuid:' + str(self.uuid) + ' state:' + str(self.state) + ' >'

    # Properties
    state = property(get_state, set_state)
    info = property(get_info, set_info)
    timestamp = property(get_timestamp, None)
    uuid = property(get_uuid, None)


class ParticipantDispatch:
    def __init__(self):
        self.online = []
        self.in_session = []
        self.done = []

    def participant_online(self, uuid):
        # Create a new state for participant
        mystate = ParticipantDispatchState(uuid)
        self.online.append(mystate)

    def participant_offline(self, uuid):
        for participant_state in self.online:
            if participant_state.uuid == uuid:
                self.online.remove(participant_state)
                break

        for participant_state in self.in_session:
            if participant_state.uuid == uuid:
                self.in_session.remove(participant_state)
                participant_state.state = ParticipantStateNames.OFFLINE
                participant_state.info['session_end'] = datetime.now()
                self.done.append(participant_state)
                break

    def dispatch_next_participant(self):
        if not self.online:
            return None

        # First in line
        current_participant_state = self.online.pop()
        # Change state
        current_participant_state.state = ParticipantStateNames.IN_SESSION
        # Add session timestamp
        current_participant_state.info['session_start'] = datetime.now()
        # Append to in_session list
        self.in_session.append(current_participant_state)
        # Return uuid
        return current_participant_state.uuid


class OnlineUsersModule(BaseModule):

    def __init__(self,  config: ConfigManager):
        BaseModule.__init__(self, "VideoDispatchService.OnlineUsersModule", config)
        self.dispatch = ParticipantDispatch()

    def setup_module_pubsub(self):
        # Additional subscribe
        self.subscribe_pattern_with_callback('module.TeraServer.UserManagerModule.messages.events',
                                             self.notify_user_manager_event)

    def notify_user_manager_event(self, pattern, channel, message):
        """
        We have received a published message from redis
        """
        print('VideoDispatchService.OnlineUsersModule - notify_user_manager_event', pattern, channel, message)
        tera_message = TeraMessage()
        tera_message.ParseFromString(message)

        # We have a repeated Any field look for message type
        for any_msg in tera_message.data:
            # Test for UserEvent
            # Unused for now
            user_event = UserEvent()
            if any_msg.Unpack(user_event):
                if user_event.type == user_event.USER_CONNECTED:
                    pass
                elif user_event.type == user_event.USER_DISCONNECTED:
                    pass

            # Test for ParticipantEvent
            # We want to know if a participant is connected or disconnected
            participant_event = ParticipantEvent()
            if any_msg.Unpack(participant_event):
                if participant_event.type == participant_event.PARTICIPANT_CONNECTED:
                    self.dispatch.participant_online(participant_event.participant_uuid)
                elif participant_event.type == participant_event.PARTICIPANT_DISCONNECTED:
                    self.dispatch.participant_offline(participant_event.participant_uuid)

            # Test for DeviceEvent
            # Unused for now
            device_event = DeviceEvent()
            if any_msg.Unpack(device_event):
                if device_event.type == device_event.DEVICE_CONNECTED:
                    pass
                elif device_event.type == device_event.DEVICE_DISCONNECTED:
                    pass

    def notify_module_messages(self, pattern, channel, message):
        """
        We have received a published message from redis
        """
        print('VideoDispatchService.OnlineUsersModule - Received message ', pattern, channel, message)
        pass


if __name__ == '__main__':
    print('Testing...')
    mystate = ParticipantDispatchState(uuid4(), {}, ParticipantStateNames.ONLINE)
    print(mystate.state)
    mystate.state = ParticipantStateNames.OFFLINE
    print(mystate)

    dispatch = ParticipantDispatch()
    dispatch.participant_online(uuid4())

    test = dispatch.dispatch_next_participant()

    dispatch.participant_offline(test)

    print('done!')
