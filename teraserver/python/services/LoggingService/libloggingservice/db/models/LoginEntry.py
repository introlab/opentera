from opentera.db.Base import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, String, BigInteger, TIMESTAMP, Sequence


class LoginEntry(BaseModel):
    __tablename__ = "t_logins"
    id_login_event = Column(Integer, Sequence('id_login_event_sequence'), primary_key=True, autoincrement=True)
    login_timestamp = Column(TIMESTAMP(timezone=True), nullable=False)
    login_log_level = Column(Integer, nullable=False)
    login_sender = Column(String(), nullable=False)
    login_user_uuid = Column(String(36), nullable=True)
    login_participant_uuid = Column(String(36), nullable=True)
    login_device_uuid = Column(String(36), nullable=True)
    login_service_uuid = Column(String(36), nullable=True)
    login_status = Column(Integer, nullable=False)
    login_type = Column(Integer, nullable=False)
    login_client_ip = Column(String, nullable=False)
    login_server_endpoint = Column(String, nullable=True)
    login_client_name = Column(String, nullable=True)
    login_client_version = Column(String, nullable=True)
    login_os_name = Column(String, nullable=True)
    login_os_version = Column(String, nullable=True)
    login_message = Column(String, nullable=True)

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []
        return super().to_json(ignore_fields=ignore_fields)

    @staticmethod
    def get_login_entry_by_id(id_login_event: int):
        return LoginEntry.query.filter_by(id_login_event=id_login_event).first()

    @staticmethod
    def get_login_entries_by_user_uuid(user_uuid: str):
        return LoginEntry.query.filter_by(login_user_uuid=user_uuid).all()

    @staticmethod
    def get_login_entries_by_participant_uuid(participant_uuid: str):
        return LoginEntry.query.filter_by(login_participant_uuid=participant_uuid).all()

    @staticmethod
    def get_login_entries_by_device_uuid(device_uuid: str):
        return LoginEntry.query.filter_by(login_device_uuid=device_uuid).all()

    @staticmethod
    def get_login_entries_by_service_uuid(service_uuid: str):
        return LoginEntry.query.filter_by(login_service_uuid=service_uuid).all()
