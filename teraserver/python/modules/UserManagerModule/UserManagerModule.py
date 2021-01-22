from opentera.config.ConfigManager import ConfigManager
from opentera.messages.python.TeraModuleMessage_pb2 import TeraModuleMessage
from opentera.messages.python.UserEvent_pb2 import UserEvent
from opentera.messages.python.ParticipantEvent_pb2 import ParticipantEvent
from opentera.messages.python.DeviceEvent_pb2 import DeviceEvent
from opentera.messages.python.JoinSessionEvent_pb2 import JoinSessionEvent
from opentera.messages.python.StopSessionEvent_pb2 import StopSessionEvent
from opentera.messages.python.LeaveSessionEvent_pb2 import LeaveSessionEvent
from opentera.messages.python.JoinSessionReplyEvent_pb2 import JoinSessionReplyEvent
from opentera.modules.BaseModule import BaseModule, ModuleNames
from modules.UserManagerModule.UserRegistry import UserRegistry
from modules.UserManagerModule.ParticipantRegistry import ParticipantRegistry
from modules.UserManagerModule.DeviceRegistry import DeviceRegistry


class UserManagerModule(BaseModule):

    def __init__(self, config: ConfigManager):
        BaseModule.__init__(self, ModuleNames.USER_MANAGER_MODULE_NAME.value, config)

        # Create state registries
        self.user_registry = UserRegistry()
        self.participant_registry = ParticipantRegistry()
        self.device_registry = DeviceRegistry()
        self.send_participant_event = True
        self.send_device_event = True

    def __del__(self):
        pass

    def setup_rpc_interface(self):
        self.rpc_api['online_users'] = {'args': [], 'returns': 'list', 'callback': self.online_users_rpc_callback}
        self.rpc_api['busy_users'] = {'args': [], 'returns': 'dict', 'callback': self.busy_users_rpc_callback}
        self.rpc_api['status_users'] = {'args': [], 'returns': 'dict', 'callback': self.status_users_rpc_callback}

        self.rpc_api['online_participants'] = {'args': [], 'returns': 'list',
                                               'callback': self.online_participants_rpc_callback}
        self.rpc_api['busy_participants'] = {'args': [], 'returns': 'dict',
                                             'callback': self.busy_participants_rpc_callback}

        self.rpc_api['status_participants'] = {'args': [], 'returns': 'dict',
                                               'callback': self.status_participants_rpc_callback}

        self.rpc_api['online_devices'] = {'args': [], 'returns': 'list',
                                          'callback': self.online_devices_rpc_callback}
        self.rpc_api['busy_devices'] = {'args': [], 'returns': 'dict', 'callback': self.busy_devices_rpc_callback}

        self.rpc_api['status_devices'] = {'args': [], 'returns': 'dict', 'callback': self.status_devices_rpc_callback}

    def online_users_rpc_callback(self, *args, **kwargs):
        # print('online_users_rpc_callback', args, kwargs)
        return self.user_registry.online_users()

    def online_participants_rpc_callback(self, *args, **kwargs):
        # print('online_participants_rpc_callback', args, kwargs)
        return self.participant_registry.online_participants()

    def online_devices_rpc_callback(self, *args, **kwargs):
        # print('online_devices_rpc_callback', args, kwargs)
        return self.device_registry.online_devices()

    def busy_users_rpc_callback(self, *args, **kwargs):
        # print('busy_users_rpc_callback', args, kwargs)
        return self.user_registry.busy_users()

    def busy_participants_rpc_callback(self, *args, **kwargs):
        # print('busy_participants_rpc_callback', args, kwargs)
        return self.participant_registry.busy_participants()

    def busy_devices_rpc_callback(self, *args, **kwargs):
        # print('busy_devices_rpc_callback', args, kwargs)
        return self.device_registry.busy_devices()

    def status_users_rpc_callback(self, *args, **kwargs):
        # Get online users
        online_users = [uuid for uuid in self.user_registry.online_users()]
        # Get busy users
        busy_users = [uuid for uuid in self.user_registry.busy_users()]
        # Get unique uuids (merge lists)
        all_uuids = set(online_users + busy_users)

        result = {}
        for user_uuid in all_uuids:
            online_flag = False
            busy_flag = False
            if user_uuid in online_users:
                online_flag = True
            if user_uuid in busy_users:
                busy_flag = True

            result[user_uuid] = {'online': online_flag, 'busy': busy_flag}
        return result

    def status_participants_rpc_callback(self, *args, **kwargs):
        # Get online participants
        online_participants = [uuid for uuid in self.participant_registry.online_participants()]
        # Get busy participants
        busy_participants = [uuid for uuid in self.participant_registry.busy_participants()]
        # Get unique uuids (merge lists)
        all_uuids = set(online_participants + busy_participants)

        result = {}
        for participant_uuid in all_uuids:
            online_flag = False
            busy_flag = False
            if participant_uuid in online_participants:
                online_flag = True
            if participant_uuid in busy_participants:
                busy_flag = True

            result[participant_uuid] = {'online': online_flag, 'busy': busy_flag}
        return result

    def status_devices_rpc_callback(self, *args, **kwargs):
        # Get online devices
        online_devices = [uuid for uuid in self.device_registry.online_devices()]
        # Get busy devices
        busy_devices = [uuid for uuid in self.device_registry.busy_devices()]
        # Get unique uuids (merge lists)
        all_uuids = set(online_devices + busy_devices)

        result = {}
        for device_uuid in all_uuids:
            online_flag = False
            busy_flag = False
            if device_uuid in online_devices:
                online_flag = True
            if device_uuid in busy_devices:
                busy_flag = True

            result[device_uuid] = {'online': online_flag, 'busy': busy_flag}
        return result

    def setup_module_pubsub(self):
        pass

    def notify_module_messages(self, pattern, channel, message):
        """
        We have received a published message from redis
        """
        # print('UserManagerModule - Received message ', pattern, channel, message)

        tera_message = TeraModuleMessage()
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

            # Test for DeviceEvent
            device_event = DeviceEvent()
            if any_msg.Unpack(device_event):
                if device_event.type == device_event.DEVICE_CONNECTED:
                    self.handle_device_connected(tera_message.head, device_event)
                elif device_event.type == device_event.DEVICE_DISCONNECTED:
                    self.handle_device_disconnected(tera_message.head, device_event)

            # Test for JoinSessionEvent
            join_session_event = JoinSessionEvent()
            if any_msg.Unpack(join_session_event):
                self.handle_join_session_event(join_session_event)

            # Test for StopSessionEvent
            stop_session_event = StopSessionEvent()
            if any_msg.Unpack(stop_session_event):
                self.handle_stop_session_event(stop_session_event)

            # Test for LeaveSessionEvent
            leave_session_event = LeaveSessionEvent()
            if any_msg.Unpack(leave_session_event):
                self.handle_leave_session_event(leave_session_event)

            # Test for JoinSessionReplyEvent
            join_session_reply = JoinSessionReplyEvent()
            if any_msg.Unpack(join_session_reply):
                self.handle_join_session_reply_event(join_session_reply)

    def handle_user_connected(self, header, user_event: UserEvent):
        self.user_registry.user_online(user_event.user_uuid)
        self.logger.log_info(self.module_name, 'user online', user_event.user_uuid)
        # Send message to event topic
        self.send_event_message(user_event, self.event_topic_name())

    def handle_user_disconnected(self, header, user_event: UserEvent):
        self.user_registry.user_offline(user_event.user_uuid)
        self.logger.log_info(self.module_name, 'user offline', user_event.user_uuid)
        # Send message to event topic
        self.send_event_message(user_event, self.event_topic_name())

    def handle_participant_connected(self, header, participant_event: ParticipantEvent):
        self.participant_registry.participant_online(participant_event.participant_uuid)
        self.logger.log_info(self.module_name, 'participant online', participant_event.participant_uuid)
        # Send message to event topic
        self.send_event_message(participant_event, self.event_topic_name())

    def handle_participant_disconnected(self, header, participant_event: ParticipantEvent):
        self.participant_registry.participant_offline(participant_event.participant_uuid)
        self.logger.log_info(self.module_name, 'participant offline', participant_event.participant_uuid)
        # Send message to event topic
        self.send_event_message(participant_event, self.event_topic_name())

    def handle_device_connected(self, header, device_event: DeviceEvent):
        self.device_registry.device_online(device_event.device_uuid)
        self.logger.log_info(self.module_name, 'device online', device_event.device_uuid)
        # Send message to event topic
        self.send_event_message(device_event, self.event_topic_name())

    def handle_device_disconnected(self, header, device_event: DeviceEvent):
        self.device_registry.device_offline(device_event.device_uuid)
        self.logger.log_info(self.module_name, 'device offline', device_event.device_uuid)
        # Send message to event topic
        self.send_event_message(device_event, self.event_topic_name())

    def set_users_in_session(self, session_uuid: str, user_uuids: list, in_session: bool):
        self.logger.log_info(self.module_name, 'set_users_in_session', session_uuid, user_uuids, in_session)

        for user in user_uuids:
            user_event = UserEvent()
            user_event.user_uuid = user
            if in_session:
                self.user_registry.user_join_session(user, session_uuid)
                user_event.type = UserEvent.USER_JOINED_SESSION
            else:
                self.user_registry.user_leave_session(user, session_uuid)
                user_event.type = UserEvent.USER_LEFT_SESSION

            # Get full name
            from opentera.db.models.TeraUser import TeraUser
            user_data = TeraUser.get_user_by_uuid(user)
            user_event.user_fullname = user_data.get_fullname()
            self.send_event_message(user_event, self.event_topic_name())

    def set_participants_in_session(self, session_uuid: str, participant_uuids: list, in_session: bool):
        self.logger.log_info(self.module_name, 'set_participants_in_session', session_uuid,
                             participant_uuids, in_session)

        for participant in participant_uuids:
            participant_event = ParticipantEvent()
            participant_event.participant_uuid = participant
            if in_session:
                self.participant_registry.participant_join_session(participant, session_uuid)
                participant_event.type = ParticipantEvent.PARTICIPANT_JOINED_SESSION
            else:
                self.participant_registry.participant_leave_session(participant, session_uuid)
                participant_event.type = ParticipantEvent.PARTICIPANT_LEFT_SESSION

            # TODO: Get others infos for that participant
            from opentera.db.models.TeraParticipant import TeraParticipant
            part_data = TeraParticipant.get_participant_by_uuid(participant)
            participant_event.participant_name = part_data.participant_name
            participant_event.participant_project_name = part_data.participant_project.project_name
            participant_event.participant_site_name = part_data.participant_project.project_site.site_name
            self.send_event_message(participant_event, self.event_topic_name())

    def set_devices_in_session(self, session_uuid: str, device_uuids: list, in_session: bool):
        self.logger.log_info(self.module_name, 'set_devices_in_session', session_uuid,
                             device_uuids, in_session)

        for device in device_uuids:
            device_event = DeviceEvent()
            device_event.device_uuid = device
            if in_session:
                self.device_registry.device_join_session(device, session_uuid)
                device_event.type = DeviceEvent.DEVICE_JOINED_SESSION
            else:
                self.device_registry.device_leave_session(device, session_uuid)
                device_event.type = DeviceEvent.DEVICE_LEFT_SESSION

            from opentera.db.models.TeraDevice import TeraDevice
            device_data = TeraDevice.get_device_by_uuid(device)
            device_event.device_name = device_data.device_name
            self.send_event_message(device_event, self.event_topic_name())

    def handle_join_session_event(self, join_event: JoinSessionEvent):
        self.logger.log_info(self.module_name, 'JoinSessionEvent', 'session', join_event.session_uuid)
        self.set_users_in_session(session_uuid=join_event.session_uuid, user_uuids=join_event.session_users,
                                  in_session=True)

        self.set_participants_in_session(session_uuid=join_event.session_uuid,
                                         participant_uuids=join_event.session_participants,
                                         in_session=True)
        self.set_devices_in_session(session_uuid=join_event.session_uuid,
                                    device_uuids=join_event.session_devices,
                                    in_session=True)

    def handle_stop_session_event(self, stop_event: StopSessionEvent):
        self.logger.log_info(self.module_name, 'StopSessionEvent', 'session', stop_event.session_uuid)
        session_users = []
        session_devices = []
        session_participants = []

        for uuid, session_uuid in self.user_registry.busy_users().items():
            if session_uuid == stop_event.session_uuid:
                session_users.append(uuid)

        for uuid, session_uuid in self.participant_registry.busy_participants().items():
            if session_uuid == stop_event.session_uuid:
                session_participants.append(uuid)

        for uuid, session_uuid in self.device_registry.busy_devices().items():
            if session_uuid == stop_event.session_uuid:
                session_devices.append(uuid)

        self.set_users_in_session(session_uuid=stop_event.session_uuid, user_uuids=session_users,
                                  in_session=False)

        self.set_participants_in_session(session_uuid=stop_event.session_uuid,
                                         participant_uuids=session_participants,
                                         in_session=False)

        self.set_devices_in_session(session_uuid=stop_event.session_uuid,
                                    device_uuids=session_devices,
                                    in_session=False)

    def handle_leave_session_event(self, leave_event: LeaveSessionEvent):
        self.logger.log_info(self.module_name, 'LeaveSessionEvent', 'session', leave_event.session_uuid)
        self.set_users_in_session(session_uuid=leave_event.session_uuid, user_uuids=leave_event.leaving_users,
                                  in_session=False)

        self.set_participants_in_session(session_uuid=leave_event.session_uuid,
                                         participant_uuids=leave_event.leaving_participants,
                                         in_session=False)
        self.set_devices_in_session(session_uuid=leave_event.session_uuid,
                                    device_uuids=leave_event.leaving_devices,
                                    in_session=False)

    def handle_join_session_reply_event(self, join_reply: JoinSessionReplyEvent):
        # Clear busy states of elements that refused to join session
        self.logger.log_info(self.module_name, 'JoinSessionReplyEvent', 'session', join_reply.session_uuid)
        if join_reply.join_reply != JoinSessionReplyEvent.REPLY_ACCEPTED:
            self.set_users_in_session(session_uuid=join_reply.session_uuid, user_uuids=[join_reply.user_uuid],
                                      in_session=False)

            self.set_participants_in_session(session_uuid=join_reply.session_uuid,
                                             participant_uuids=[join_reply.participant_uuid],
                                             in_session=False)

            self.set_devices_in_session(session_uuid=join_reply.session_uuid,
                                        device_uuids=[join_reply.device_uuid],
                                        in_session=False)
