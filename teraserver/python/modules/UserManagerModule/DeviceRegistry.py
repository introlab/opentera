class DeviceRegistry:
    def __init__(self):
        self.device_list = list()
        self.device_sessions_list = dict()

    def device_online(self, uuid):
        print('device_online: ', uuid)
        if not self.device_list.__contains__(uuid):
            self.device_list.append(uuid)

    def device_offline(self, uuid):
        print('device_offline', uuid)
        if self.device_list.__contains__(uuid):
            self.device_list.remove(uuid)
        if uuid in self.device_sessions_list:
            del self.device_sessions_list[uuid]

    def online_devices(self):
        return self.device_list

    def device_join_session(self, uuid, session_uuid):
        if uuid not in self.device_sessions_list:
            self.device_sessions_list[uuid] = session_uuid
        else:
            print('Error: device ' + uuid + ' already in a session: ' + self.user_sessions_list[uuid] + '!')

    def device_leave_session(self, uuid, session_uuid):
        if uuid in self.device_sessions_list:
            if self.device_sessions_list[uuid] == session_uuid:
                del self.device_sessions_list[uuid]
            else:
                print('Error: device ' + uuid + ' wasn\'t in the session ' + session_uuid + '!')

    def busy_devices(self):
        return self.device_sessions_list
