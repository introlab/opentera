from modules.BaseModule import BaseModule, ModuleNames
from .ConfigManager import ConfigManager
from messages.python.TeraMessage_pb2 import TeraMessage
from messages.python.UserEvent_pb2 import UserEvent
from messages.python.ParticipantEvent_pb2 import ParticipantEvent
from messages.python.DeviceEvent_pb2 import DeviceEvent


class UserDispatch:
    def __init__(self):
        pass


class OnlineUsersModule(BaseModule):

    def __init__(self,  config: ConfigManager):
        BaseModule.__init__(self, "VideoDispatchService.OnlineUsersModule", config)

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
                    pass
                elif participant_event.type == participant_event.PARTICIPANT_DISCONNECTED:
                    pass

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

