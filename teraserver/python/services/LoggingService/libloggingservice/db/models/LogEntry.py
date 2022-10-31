
from opentera.db.Base import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, String, BigInteger, TIMESTAMP, Sequence


class LogEntry(BaseModel):
    __tablename__ = "t_log_entry"
    id_log_entry = Column(Integer, Sequence('id_log_entry_sequence'), primary_key=True, autoincrement=True)
    log_level = Column(Integer, nullable=False)
    sender = Column(String(), nullable=False)
    message = Column(String(), nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []
        return super().to_json(ignore_fields=ignore_fields)


