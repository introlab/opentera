

class UserRegistry:
    def __init__(self):
        self.user_list = list()
        self.user_sessions_list = dict()

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

    def user_join_session(self, uuid, session_uuid):
        if not self.user_sessions_list[uuid]:
            self.user_sessions_list[uuid] = session_uuid
        else:
            print('Error: user ' + uuid + ' already in a session: ' + self.user_sessions_list[uuid] + '!')

    def user_leave_session(self, uuid, session_uuid):
        if self.user_sessions_list[uuid]:
            if self.user_sessions_list[uuid] == session_uuid:
                del self.user_sessions_list[uuid]
            else:
                print('Error: user ' + uuid + ' wasn\'t in the session ' + session_uuid + '!')

    def busy_users(self):
        return self.user_sessions_list
