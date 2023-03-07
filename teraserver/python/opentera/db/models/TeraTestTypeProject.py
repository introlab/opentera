from opentera.db.Base import BaseModel
from opentera.db.SoftDeleteMixin import SoftDeleteMixin
from opentera.db.SoftInsertMixin import SoftInsertMixin
from opentera.db.models.TeraTest import TeraTest
from opentera.db.models.TeraSession import TeraSession
from sqlalchemy import Column, ForeignKey, Integer, Sequence
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError


class TeraTestTypeProject(BaseModel, SoftDeleteMixin, SoftInsertMixin):
    __tablename__ = 't_tests_types_projects'
    id_test_type_project = Column(Integer, Sequence('id_test_type_project_sequence'), primary_key=True,
                                  autoincrement=True)
    id_test_type = Column('id_test_type', Integer, ForeignKey('t_tests_types.id_test_type', ondelete='cascade'),
                          nullable=False)
    id_project = Column('id_project', Integer, ForeignKey('t_projects.id_project', ondelete='cascade'), nullable=False)

    test_type_project_test_type = relationship("TeraTestType", viewonly=True)
    test_type_project_project = relationship("TeraProject", viewonly=True)

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        ignore_fields.extend(['test_type_project_test_type', 'test_type_project_project'])

        if minimal:
            ignore_fields.extend([])

        rval = super().to_json(ignore_fields=ignore_fields)

        return rval

    @staticmethod
    def create_defaults(test=False):
        if test:
            from opentera.db.models.TeraTestType import TeraTestType
            from opentera.db.models.TeraProject import TeraProject

            pre_test = TeraTestType.get_test_type_by_id(1)
            post_test = TeraTestType.get_test_type_by_id(2)
            general_test = TeraTestType.get_test_type_by_id(3)

            project = TeraProject.get_project_by_projectname('Default Project #1')
            secret_project = TeraProject.get_project_by_projectname('Secret Project #1')

            ttp = TeraTestTypeProject()
            ttp.id_test_type = pre_test.id_test_type
            ttp.id_project = project.id_project
            TeraTestTypeProject.db().session.add(ttp)

            ttp = TeraTestTypeProject()
            ttp.id_test_type = post_test.id_test_type
            ttp.id_project = project.id_project
            TeraTestTypeProject.db().session.add(ttp)

            ttp = TeraTestTypeProject()
            ttp.id_test_type = general_test.id_test_type
            ttp.id_project = secret_project.id_project
            TeraTestTypeProject.db().session.add(ttp)

            TeraTestTypeProject.db().session.commit()

    @staticmethod
    def get_test_type_project_by_id(stp_id: int, with_deleted: bool = False):
        return TeraTestTypeProject.query.execution_options(include_deleted=with_deleted)\
            .filter_by(id_test_type_project=stp_id).first()

    @staticmethod
    def get_projects_for_test_type(test_type_id: int, with_deleted: bool = False):
        return TeraTestTypeProject.query.execution_options(include_deleted=with_deleted)\
            .filter_by(id_test_type=test_type_id).all()

    @staticmethod
    def get_tests_types_for_project(project_id: int, with_deleted: bool = False):
        return TeraTestTypeProject.query.execution_options(include_deleted=with_deleted)\
            .filter_by(id_project=project_id).all()

    @staticmethod
    def get_test_type_project_for_test_type_project(project_id: int, test_type_id: int, with_deleted: bool = False):
        return TeraTestTypeProject.query.execution_options(include_deleted=with_deleted)\
            .filter_by(id_project=project_id, id_test_type=test_type_id).first()

    @staticmethod
    def get_test_type_project_for_project_and_service(project_id: int, service_id: int, with_deleted: bool = False):
        from opentera.db.models.TeraTestType import TeraTestType
        return TeraTestTypeProject.query.execution_options(include_deleted=with_deleted).join(TeraTestType).\
            filter(TeraTestType.id_service == service_id).\
            filter(TeraTestTypeProject.id_project == project_id).all()

    @staticmethod
    def delete_with_ids(test_type_id: int, project_id: int, autocommit: bool = True):
        delete_obj: TeraTestTypeProject = TeraTestTypeProject.query.filter_by(id_test_type=test_type_id,
                                                                              id_project=project_id).first()
        if delete_obj:
            TeraTestTypeProject.delete(delete_obj.id_test_type_project, autocommit=autocommit)

    @staticmethod
    def check_integrity(obj_to_check):
        # Make sure that the service is associated to that project
        service_projects = [proj.id_project for proj in
                            obj_to_check.test_type_project_test_type.test_type_service.service_projects]
        if obj_to_check.id_project not in service_projects:
            # We must also associate that service to that project!
            from opentera.db.models.TeraServiceProject import TeraServiceProject
            new_service_project = TeraServiceProject()
            new_service_project.id_service = obj_to_check.test_type_project_test_type \
                .test_type_service.id_service
            new_service_project.id_project = obj_to_check.test_type_project_project.id_project
            TeraServiceProject.insert(new_service_project)

    @classmethod
    def insert(cls, ttp):
        # Check if that site of that project has the site associated to it
        from opentera.db.models.TeraTestTypeSite import TeraTestTypeSite
        from opentera.db.models.TeraProject import TeraProject
        project = TeraProject.get_project_by_id(project_id=ttp.id_project)
        tt_site = TeraTestTypeSite.get_test_type_site_for_test_type_and_site(site_id=project.id_site,
                                                                             test_type_id=ttp.id_test_type)
        if not tt_site:
            raise IntegrityError(params='Test type not associated to project site',
                                 orig='TeraTestTypeProject.insert', statement='insert')
        inserted_obj = super().insert(ttp)
        TeraTestTypeProject.check_integrity(inserted_obj)
        return inserted_obj

    def delete_check_integrity(self) -> IntegrityError | None:
        session_ids = [session.id_session for session in TeraSession.get_sessions_for_project(self.id_project)]
        test_count = TeraTest.query.filter(TeraTest.id_session.in_(session_ids))\
            .filter(TeraTest.id_test_type == self.id_test_type).count()

        if test_count > 0:
            return IntegrityError('Test type has tests in this project', self.id_test_type, 't_tests')
        return None

    @classmethod
    def update(cls, update_id: int, values: dict):
        return
