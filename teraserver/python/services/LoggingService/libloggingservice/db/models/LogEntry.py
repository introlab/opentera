from services.LoggingService.libloggingservice.db.Base import db
from libtera.db.Base import BaseModel


class LogEntry(db.Model, BaseModel):
    __tablename__ = "t_log_entry"
    id_log_entry = db.Column(db.Integer, db.Sequence('id_log_entry_sequence'), primary_key=True, autoincrement=True)
    log_level = db.Column(db.Integer, nullable=False)
    sender = db.Column(db.String(), nullable=False)
    message = db.Column(db.String(), nullable=False)
    timestamp = db.Column(db.TIMESTAMP(timezone=True), nullable=False)

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []
        return super().to_json(ignore_fields=ignore_fields)


