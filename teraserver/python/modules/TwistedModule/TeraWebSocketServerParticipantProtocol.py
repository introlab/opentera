# WebSockets
from autobahn.websocket.types import ConnectionDeny

# OpenTera
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.modules.BaseModule import ModuleNames, create_module_message_topic_from_name, create_module_event_topic_from_name

# Messages
import opentera.messages.python as messages

from google.protobuf.any_pb2 import Any

# Twisted
from twisted.internet import defer

# Event manager
from modules.ParticipantEventManager import ParticipantEventManager

from modules.TwistedModule.TeraWebSocketServerProtocol import TeraWebSocketServerProtocol
from opentera.redis.RedisVars import RedisVars


class TeraWebSocketServerParticipantProtocol(TeraWebSocketServerProtocol):

    def __init__(self, config):
        TeraWebSocketServerProtocol.__init__(self, config=config)
        self.participant = None

    @defer.inlineCallbacks
    def redisConnectionMade(self):
        print('TeraWebSocketServerParticipantProtocol - redisConnectionMade (redis)', self)

        # This will wait until subscribe result is available...
        # ret = yield self.subscribe_pattern_with_callback(self.answer_topic(), self.redis_tera_message_received)
        # print(ret)

        if self.participant:
            # Events from UserManagerModule
            yield self.subscribe_pattern_with_callback(create_module_event_topic_from_name(
                ModuleNames.USER_MANAGER_MODULE_NAME), self.redis_event_message_received)

            # Events from FlaskModule
            yield self.subscribe_pattern_with_callback(
                create_module_event_topic_from_name(ModuleNames.TWISTED_MODULE_NAME, self.participant.participant_uuid),
                self.redis_tera_module_message_received)

            # Events from FileTransferService
            yield self.subscribe_pattern_with_callback(
                RedisVars.build_service_event_topic('FileTransferService'), self.redis_event_message_received)

            # Events from DatabaseModule
            yield self.subscribe_pattern_with_callback(create_module_event_topic_from_name(
                ModuleNames.DATABASE_MODULE_NAME), self.redis_event_message_received)

            # Direct events
            yield self.subscribe_pattern_with_callback(self.event_topic(), self.redis_event_message_received)

            # MAKE SURE TO SUBSCRIBE TO EVENTS BEFORE SENDING ONLINE MESSAGE
            tera_message = self.create_tera_message(
                create_module_message_topic_from_name(ModuleNames.USER_MANAGER_MODULE_NAME))
            participant_connected = messages.ParticipantEvent()
            participant_connected.participant_uuid = str(self.participant.participant_uuid)
            participant_connected.type = messages.ParticipantEvent.PARTICIPANT_CONNECTED
            participant_connected.participant_name = self.participant.participant_name
            participant_connected.participant_project_name = self.participant.participant_project.project_name
            participant_connected.participant_site_name = self.participant.participant_project.project_site.site_name
            # Need to use Any container
            any_message = Any()
            any_message.Pack(participant_connected)
            tera_message.data.extend([any_message])

            # Publish to login module (bytes)
            self.publish(create_module_message_topic_from_name(ModuleNames.USER_MANAGER_MODULE_NAME),
                         tera_message.SerializeToString())
        else:
            print(type(self).__name__, ' - closing - unauthorized.')
            super().onClose(False, None, None)

    def onConnect(self, request):
        """
        Cannot send message at this stage, needs to verify connection here.
        """
        print('TeraWebSocketServerParticipantProtocol - onConnect')

        if request.params.__contains__('id'):
            # Look for session id in
            my_id = request.params['id']
            print('TeraWebSocketServerParticipantProtocol - testing id: ', my_id, self)

            value = self.redisGet(my_id[0])

            if value is not None:
                # Needs to be converted from bytes to string to work
                participant_uuid = value.decode("utf-8")
                print('TeraWebSocketServerParticipantProtocol - participant uuid ', participant_uuid, self)

                # User verification
                self.participant = TeraParticipant.get_participant_by_uuid(participant_uuid)
                if self.participant is not None:
                    # Remove key
                    print('TeraWebSocketServerParticipantProtocol - OK! removing key', self)
                    self.redisDelete(my_id[0])

                    # Set event manager
                    self.event_manager = ParticipantEventManager(self.participant)

                    # log information
                    self.logger.log_info(self, "Participant websocket connected",
                                         self.participant.participant_name, self.participant.participant_uuid)

                    return

        # if we get here we need to close the websocket, auth failed.
        # To deny a connection, raise an Exception
        raise ConnectionDeny(ConnectionDeny.FORBIDDEN,
                             "TeraWebSocketServerParticipantProtocol - Websocket authentication failed (key, uuid).")

    @defer.inlineCallbacks
    def onClose(self, wasClean, code, reason):
        print('TeraWebSocketServerParticipantProtocol - onClose', self, wasClean, code, reason)
        if self.participant:
            # Advertise that participant leaved
            tera_message = self.create_tera_message(
                create_module_message_topic_from_name(ModuleNames.USER_MANAGER_MODULE_NAME))
            participant_disconnected = messages.ParticipantEvent()
            participant_disconnected.participant_uuid = str(self.participant.participant_uuid)
            participant_disconnected.type = messages.ParticipantEvent.PARTICIPANT_DISCONNECTED
            participant_disconnected.participant_name = self.participant.participant_name
            participant_disconnected.participant_project_name = self.participant.participant_project.project_name
            participant_disconnected.participant_site_name = self.participant.participant_project.project_site.site_name

            # Need to use Any container
            any_message = Any()
            any_message.Pack(participant_disconnected)
            tera_message.data.extend([any_message])

            # Publish to login module (bytes)
            self.publish(create_module_message_topic_from_name(ModuleNames.USER_MANAGER_MODULE_NAME),
                         tera_message.SerializeToString())

            # Events from UserManagerModule
            yield self.unsubscribe_pattern_with_callback(
                create_module_event_topic_from_name(ModuleNames.USER_MANAGER_MODULE_NAME),
                self.redis_event_message_received)

            # Events from FlaskModule
            yield self.unsubscribe_pattern_with_callback(
                create_module_event_topic_from_name(ModuleNames.TWISTED_MODULE_NAME, self.participant.participant_uuid),
                self.redis_tera_module_message_received)

            # Events from DatabaseModule
            yield self.unsubscribe_pattern_with_callback(
                create_module_event_topic_from_name(ModuleNames.DATABASE_MODULE_NAME),
                self.redis_event_message_received)

            # Events from FileTransferService
            yield self.unsubscribe_pattern_with_callback(
                RedisVars.build_service_event_topic('FileTransferService'), self.redis_event_message_received)

            # Direct events
            yield self.unsubscribe_pattern_with_callback(self.event_topic(), self.redis_event_message_received)

            # log information
            self.logger.log_info(self, "Participant websocket disconnected",
                                 self.participant.participant_name, self.participant.participant_uuid)

        super().onClose(wasClean, code, reason)

    def answer_topic(self):
        if self.participant:
            return 'websocket.participant.' + self.participant.participant_uuid
        return super().answer_topic()

    def event_topic(self):
        if self.participant:
            return 'websocket.participant.' + self.participant.participant_uuid + '.events'
        return super().event_topic()

