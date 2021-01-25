# Messages
import opentera.messages.python as messages


class EventManager:
    def __init__(self):
        self.registered_events = set()  # Collection of unique elements

    def register_to_event(self, event_type):
        pass

    def unregister_to_event(self, event_type):
        pass

    def filter_device_event(self, event: messages.DeviceEvent):
        # Default = no access
        return False

    def filter_join_session_event(self, event: messages.JoinSessionEvent):
        # Default = no access
        return False

    def filter_join_session_reply_event(self, event: messages.JoinSessionReplyEvent):
        # Default = no access
        return False

    def filter_leave_session_event(self, event: messages.LeaveSessionEvent):
        # Default = no access
        return False

    def filter_participant_event(self, event: messages.ParticipantEvent):
        # Default = no access
        return False

    def filter_stop_session_event(self, event: messages.StopSessionEvent):
        # Default = no access
        return False

    def filter_user_event(self, event: messages.UserEvent):
        # Default = no access
        return False

    def filter_database_event(self, event: messages.DatabaseEvent):
        # Default = no access
        return False

    def filter_events(self, message: messages.TeraEvent) -> messages.TeraEvent:
        # Will receive message containing events
        # Let's try to unpack the messages first and call the adequate method

        # Create a copy of the message
        filtered_message = messages.TeraEvent()
        filtered_message.CopyFrom(message)

        for any_msg in filtered_message.events:

            # Test for DeviceEvent
            device_event = messages.DeviceEvent()
            # Test for JoinSessionEvent
            join_session_event = messages.JoinSessionEvent()
            # Test for ParticipantEvent
            participant_event = messages.ParticipantEvent()
            # Test for StopSessionEvent
            stop_session_event = messages.StopSessionEvent()
            # Test for UserEvent
            user_event = messages.UserEvent()
            # Test for DatabaseEvent
            database_event = messages.DatabaseEvent()
            # Test for LeaveSessionEvent
            leave_session_event = messages.LeaveSessionEvent()
            # Test for JoinSessionReply
            join_session_reply = messages.JoinSessionReplyEvent()

            if any_msg.Unpack(device_event):
                if not self.filter_device_event(device_event):
                    print('removing:', device_event)
                    filtered_message.events.remove(any_msg)
            elif any_msg.Unpack(join_session_event):
                if not self.filter_join_session_event(join_session_event):
                    print('removing:', join_session_event)
                    filtered_message.events.remove(any_msg)
            elif any_msg.Unpack(participant_event):
                if not self.filter_participant_event(participant_event):
                    print('removing:', participant_event)
                    filtered_message.events.remove(any_msg)
            elif any_msg.Unpack(stop_session_event):
                if not self.filter_stop_session_event(stop_session_event):
                    print('removing:', stop_session_event)
                    filtered_message.events.remove(any_msg)
            elif any_msg.Unpack(leave_session_event):
                if not self.filter_leave_session_event(leave_session_event):
                    print('removing:', leave_session_event)
                    filtered_message.events.remove(any_msg)
            elif any_msg.Unpack(user_event):
                if not self.filter_user_event(user_event):
                    print('removing:', user_event)
                    filtered_message.events.remove(any_msg)
            elif any_msg.Unpack(database_event):
                if not self.filter_database_event(database_event):
                    print('removing', database_event)
                    filtered_message.events.remove(any_msg)
            elif any_msg.Unpack(join_session_reply):
                if not self.filter_join_session_reply_event(join_session_reply):
                    print('removing', join_session_reply)
                    filtered_message.events.remove(any_msg)
            else:
                print('Unknown event, removing: ', any_msg)
                filtered_message.events.remove(any_msg)

        # Return filtered message
        return filtered_message

