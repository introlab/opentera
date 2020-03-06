from libtera.ConfigManager import ConfigManager
from messages.python.TeraMessage_pb2 import TeraMessage
from messages.python.RPCMessage_pb2 import RPCMessage
from messages.python.CreateSession_pb2 import CreateSession
from messages.python.UserEvent_pb2 import UserEvent
from messages.python.ParticipantEvent_pb2 import ParticipantEvent
from messages.python.DeviceEvent_pb2 import DeviceEvent
from modules.BaseModule import BaseModule, ModuleNames, create_module_topic_from_name
from google.protobuf.any_pb2 import Any
import datetime


class OnlineUserRegistry:
    def __init__(self):
        self.user_list = list()

    def user_online(self, uuid):
        print('user_online: ', uuid)
        if not self.user_list.__contains__(uuid):
            self.user_list.append(uuid)

    def user_offline(self, uuid):
        print('user_offline', uuid)
        if self.user_list.__contains__(uuid):
            self.user_list.remove(uuid)

    def online_users(self):
        return self.user_list


# TODO Should be moved somewhere else?
class OnlineParticipantRegistry:
    def __init__(self):
        self.participant_list = list()

    def participant_online(self, uuid):
        print('participant_online: ', uuid)
        if not self.participant_list.__contains__(uuid):
            self.participant_list.append(uuid)

    def participant_offline(self, uuid):
        print('participant_offline', uuid)
        if self.participant_list.__contains__(uuid):
            self.participant_list.remove(uuid)

    def online_participants(self):
        return self.participant_list


# TODO Should be moved somewhere else?
class OnlineDeviceRegistry:
    def __init__(self):
        self.device_list = list()

    def device_online(self, uuid):
        print('device_online: ', uuid)
        if not self.device_list.__contains__(uuid):
            self.device_list.append(uuid)

    def device_offline(self, uuid):
        print('device_offline', uuid)
        if self.device_list.__contains__(uuid):
            self.device_list.remove(uuid)

    def online_devices(self):
        return self.device_list


class UserManagerModule(BaseModule):

    def __init__(self, config: ConfigManager):
        BaseModule.__init__(self, ModuleNames.USER_MANAGER_MODULE_NAME.value, config)

        # Create user registry
        self.user_registry = OnlineUserRegistry()
        self.participant_registry = OnlineParticipantRegistry()
        self.device_registry = OnlineDeviceRegistry()
        self.send_participant_event = True
        self.send_device_event = True

    def __del__(self):
        pass

    def setup_rpc_interface(self):
        self.rpc_api['online_users'] = {'args': [], 'returns': 'list', 'callback': self.online_users_rpc_callback}
        self.rpc_api['online_participants'] = {'args': [], 'returns': 'list',
                                               'callback': self.online_participants_rpc_callback}

    def online_users_rpc_callback(self, *args, **kwargs):
        print('online_users_rpc_callback', args, kwargs)
        return self.user_registry.online_users()

    def online_participants_rpc_callback(self, *args, **kwargs):
        print('online_participants_rpc_callback', args, kwargs)
        return self.participant_registry.online_participants()

    def online_devices_rpc_callback(self, *args, **kwargs):
        print('online_devices_rpc_callback', args, kwargs)
        return self.device_registry.online_devices()

    def setup_module_pubsub(self):
        pass

    def notify_module_messages(self, pattern, channel, message):
        """
        We have received a published message from redis
        """
        print('UserManagerModule - Received message ', pattern, channel, message)

        tera_message = TeraMessage()
        tera_message.ParseFromString(message)
        # tera_message.ParseFromString(message.encode('utf-8'))

        # We have a repeated Any field look for message type
        for any_msg in tera_message.data:
            # Test for UserEvent
            user_event = UserEvent()
            if any_msg.Unpack(user_event):
                if user_event.type == user_event.USER_CONNECTED:
                    self.handle_user_connected(tera_message.head, user_event)
                elif user_event.type == user_event.USER_DISCONNECTED:
                    self.handle_user_disconnected(tera_message.head, user_event)

            # Test for ParticipantEvent
            participant_event = ParticipantEvent()
            if any_msg.Unpack(participant_event):
                if participant_event.type == participant_event.PARTICIPANT_CONNECTED:
                    self.handle_participant_connected(tera_message.head, participant_event)
                elif participant_event.type == participant_event.PARTICIPANT_DISCONNECTED:
                    self.handle_participant_disconnected(tera_message.head, participant_event)

                # Send back event to participant...
                if self.send_participant_event:
                    tera_message = self.create_tera_message(
                        dest='websocket.participant.' + participant_event.participant_uuid)
                    any_message = Any()
                    any_message.Pack(participant_event)
                    tera_message.data.extend([any_message])
                    self.publish(tera_message.head.dest, tera_message.SerializeToString())

            # Test for DeviceEvent
            device_event = DeviceEvent()
            if any_msg.Unpack(device_event):
                if device_event.type == device_event.DEVICE_CONNECTED:
                    self.handle_device_connected(tera_message.head, device_event)
                elif device_event.type == device_event.DEVICE_DISCONNECTED:
                    self.handle_device_disconnected(tera_message.head, device_event)

                # Send back event to participant...
                if self.send_device_event:
                    tera_message = self.create_tera_message(
                        dest='websocket.device.' + device_event.device_uuid)
                    any_message = Any()
                    any_message.Pack(device_event)
                    tera_message.data.extend([any_message])
                    self.publish(tera_message.head.dest, tera_message.SerializeToString())

    def handle_user_connected(self, header, user_event: UserEvent):
        self.user_registry.user_online(user_event.user_uuid)

        for user_uuid in self.user_registry.online_users():
            # TODO Check for permissions...
            # Send to everyone?
            tera_message = self.create_tera_message(dest='websocket.user.' + user_uuid)

            any_message = Any()
            any_message.Pack(user_event)
            tera_message.data.extend([any_message])

            self.publish(tera_message.head.dest, tera_message.SerializeToString())

    def handle_user_disconnected(self, header, user_event: UserEvent):
        self.user_registry.user_offline(user_event.user_uuid)

        for user_uuid in self.user_registry.online_users():
            # TODO Check for permissions...
            # Send to everyone?
            tera_message = self.create_tera_message(dest='websocket.user.' + user_uuid)

            any_message = Any()
            any_message.Pack(user_event)
            tera_message.data.extend([any_message])

            self.publish(tera_message.head.dest, tera_message.SerializeToString())

    def handle_participant_connected(self, header, participant_event: ParticipantEvent):
        self.participant_registry.participant_online(participant_event.participant_uuid)

        for user_uuid in self.user_registry.online_users():
            # TODO Check for permissions...
            # Send to everyone?
            tera_message = self.create_tera_message(dest='websocket.user.' + user_uuid)

            any_message = Any()
            any_message.Pack(participant_event)
            tera_message.data.extend([any_message])

            self.publish(tera_message.head.dest, tera_message.SerializeToString())

    def handle_participant_disconnected(self, header, participant_event: ParticipantEvent):
        self.participant_registry.participant_offline(participant_event.user_uuid)

        for user_uuid in self.user_registry.online_users():
            # TODO Check for permissions...
            # Send to everyone?
            tera_message = self.create_tera_message(dest='websocket.user.' + user_uuid)

            any_message = Any()
            any_message.Pack(participant_event)
            tera_message.data.extend([any_message])

            self.publish(tera_message.head.dest, tera_message.SerializeToString())

    def handle_device_connected(self, header, device_event: DeviceEvent):
        self.device_registry.device_online(device_event.device_uuid)

        for user_uuid in self.user_registry.online_users():
            # TODO Check for permissions...
            # Send to everyone?
            tera_message = self.create_tera_message(dest='websocket.user.' + user_uuid)

            any_message = Any()
            any_message.Pack(device_event)
            tera_message.data.extend([any_message])

            self.publish(tera_message.head.dest, tera_message.SerializeToString())

    def handle_device_disconnected(self, header, device_event: DeviceEvent):
        self.device_registry.device_offline(device_event.device_uuid)

        for user_uuid in self.user_registry.online_users():
            # TODO Check for permissions...
            # Send to everyone?
            tera_message = self.create_tera_message(dest='websocket.user.' + user_uuid)

            any_message = Any()
            any_message.Pack(device_event)
            tera_message.data.extend([any_message])

            self.publish(tera_message.head.dest, tera_message.SerializeToString())
