class ParticipantRegistry:
    def __init__(self):
        self.participant_list = list()
        self.participant_sessions_list = dict()

    def participant_online(self, uuid):
        print('participant_online: ', uuid)
        if not self.participant_list.__contains__(uuid):
            self.participant_list.append(uuid)

    def participant_offline(self, uuid):
        print('participant_offline', uuid)
        if self.participant_list.__contains__(uuid):
            self.participant_list.remove(uuid)
        if uuid in self.participant_sessions_list:
            del self.participant_sessions_list[uuid]

    def online_participants(self):
        return self.participant_list

    def participant_join_session(self, uuid, session_uuid):
        if uuid not in self.participant_sessions_list:
            self.participant_sessions_list[uuid] = session_uuid
        else:
            print('Error: participant ' + uuid + ' already in a session: ' + self.participant_sessions_list[uuid] + '!')

    def participant_leave_session(self, uuid, session_uuid):
        if uuid in self.participant_sessions_list:
            if self.participant_sessions_list[uuid] == session_uuid:
                del self.participant_sessions_list[uuid]
            else:
                print('Error: participant ' + uuid + ' wasn\'t in the session ' + session_uuid + '!')

    def busy_participants(self):
        return self.participant_sessions_list
