import uuid


class TeraClient:

    def __init__(self):
        self.__user_uuid = None

    @property
    def user_uuid(self):
        return self.__user_uuid

    @user_uuid.setter
    def user_uuid(self, u_uuid: uuid):
        self.__user_uuid = u_uuid
