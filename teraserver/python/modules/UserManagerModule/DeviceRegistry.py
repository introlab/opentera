from datetime import datetime


class DeviceRegistry:
    def __init__(self):
        self.device_list = list()
        self.device_sessions = dict()
        self.device_status = dict()

    def device_online(self, uuid):
        print('device_online: ', uuid)
        if not self.device_list.__contains__(uuid):
            self.device_list.append(uuid)

    def device_offline(self, uuid):
        print('device_offline', uuid)
        if self.device_list.__contains__(uuid):
            self.device_list.remove(uuid)
        if uuid in self.device_sessions:
            del self.device_sessions[uuid]
        if uuid in self.device_status:
            del self.device_status[uuid]

    def online_devices(self):
        return self.device_list

    def device_join_session(self, uuid, session_uuid):
        if uuid not in self.device_sessions:
            self.device_sessions[uuid] = session_uuid
        # else:
        #     print('Error: device ' + uuid + ' already in a session: ' + self.user_sessions[uuid] + '!')

    def device_leave_session(self, uuid, session_uuid):
        if uuid in self.device_sessions:
            if self.device_sessions[uuid] == session_uuid:
                del self.device_sessions[uuid]
            else:
                print('Error: device ' + uuid + ' wasn\'t in the session ' + session_uuid + '!')

    def device_update_status(self, uuid, status: str, timestamp):
        # Only if device is connected
        if uuid in self.device_list:
            self.device_status[uuid] = {'status': status, 'timestamp': timestamp}
            return self.device_status[uuid]
        return None

    def device_get_status(self, uuid):
        if uuid in self.device_status:
            return self.device_status[uuid]
        return None

    def status_devices(self):
        return self.device_status

    def busy_devices(self):
        return self.device_sessions
