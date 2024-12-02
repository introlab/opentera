# from opentera.db.Base import BaseModel
# from opentera.db.SoftDeleteMixin import SoftDeleteMixin
# from opentera.db.SoftInsertMixin import SoftInsertMixin
# from sqlalchemy import Column, ForeignKey, Integer, String, Sequence, Boolean, TIMESTAMP
# from sqlalchemy.orm import relationship


# class TeraSessionServices(BaseModel, SoftDeleteMixin, SoftInsertMixin):
#     __tablename__ = 't_sessions_services'
#     id_session_service = Column(Integer, Sequence('id_session_service_sequence'), primary_key=True, autoincrement=True)
#     id_session = Column(Integer, ForeignKey('t_sessions.id_session', ondelete='cascade'), nullable=False)
#     id_service = Column(Integer, ForeignKey('t_services.id_service', ondelete='cascade'), nullable=False)

#     session_service_session = relationship('TeraSession', viewonly=True)
#     session_service_service = relationship('TeraService', viewonly=True)


#     def to_json(self, ignore_fields=[], minimal=False):
#         ignore_fields.extend(['session_service_session', 'session_service_service'])

#         if minimal:
#             ignore_fields.extend([])

#         rval = super().to_json(ignore_fields=ignore_fields)

#         return rval

#     @staticmethod
#     def get_session_count_for_service(id_service: int, with_deleted: bool = False) -> int:
#         return TeraSessionServices.get_count(filters={'id_service': id_service}, with_deleted=with_deleted)

#     @classmethod
#     def update(cls, update_id: int, values: dict):
#         return
