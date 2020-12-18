import os
from tests.libtera.db.models.BaseModelsTest import BaseModelsTest
from sqlalchemy import exc
from libtera.db.Base import db

from libtera.db.models.TeraProject import TeraProject

class TeraProjectTest(BaseModelsTest):

    filename = os.path.join(os.path.dirname(__file__), 'TeraProjectTest.db')

    SQLITE = {
        'filename': filename
    }

    # __tablename__ = 't_projects'
    # id_project = db.Column(db.Integer, db.Sequence('id_project_sequence'), primary_key=True, autoincrement=True)
    # id_site = db.Column(db.Integer, db.ForeignKey('t_sites.id_site', ondelete='cascade'), nullable=False)
    # project_name = db.Column(db.String, nullable=False, unique=False)

    #
    # project_site = db.relationship("TeraSite")
    # project_participants = db.relationship("TeraParticipant", passive_deletes=True)
    # project_participants_groups = db.relationship("TeraParticipantGroup", passive_deletes=True)
    # project_devices = db.relationship("TeraDevice", secondary="t_devices_projects", back_populates="device_projects")
    # project_session_types = db.relationship("TeraSessionType", secondary="t_sessions_types_projects",
    #                                         back_populates="session_type_projects")

    def test_nullable_args(self):
        new_project = TeraProject()
        new_project.id_site = 1
        new_project.project_name = None
        db.session.add(new_project)
        self.assertRaises(exc.IntegrityError, db.session.commit)
        db.session.rollback()
        new_project = TeraProject()
        new_project.id_site = None
        new_project.project_name = 'Project Name'
        db.session.add(new_project)
        self.assertRaises(exc.IntegrityError, db.session.commit)

    def test_unique_args(self):
        pass

    def test_to_json(self):
        new_project = TeraProject()
        new_project.id_site = 1
        new_project.project_name = 'Project Name'
        db.session.add(new_project)
        db.session.commit()
        new_project_json = new_project.to_json()
        new_project_json_minimal = new_project.to_json(minimal=True)
        self._check_json(project_test=new_project_json)
        self._check_json(project_test=new_project_json_minimal, minimal=True)

    def _check_json(self, project_test, minimal=False):
        self.assertGreaterEqual(project_test['id_project'], 1)
        self.assertEqual(project_test['id_site'], 1)
        self.assertEqual(project_test['project_name'], 'Project Name')
        if not minimal:
            self.assertEqual(project_test['site_name'], 'Default Site')

    def test_to_json_create_event(self):
        new_project = TeraProject()
        new_project.id_site = 1
        new_project.project_name = 'Project Name'
        db.session.add(new_project)
        db.session.commit()
        new_project_json = new_project.to_json_create_event()
        self._check_json(project_test=new_project_json, minimal=True)

    def test_to_json_update_event(self):
        new_project = TeraProject()
        new_project.id_site = 1
        new_project.project_name = 'Project Name'
        db.session.add(new_project)
        db.session.commit()
        new_project_json = new_project.to_json_update_event()
        self._check_json(project_test=new_project_json, minimal=True)

    def test_to_json_delete_event(self):
        new_project = TeraProject()
        new_project.id_site = 1
        new_project.project_name = 'Project Name'
        db.session.add(new_project)
        db.session.commit()
        new_project_json = new_project.to_json_delete_event()
        self.assertGreaterEqual(new_project_json['id_project'], 1)

    def test_get_users_ids_in_project(self):
        new_project = TeraProject()
        new_project.id_site = 1
        new_project.project_name = 'Project Name'
        db.session.add(new_project)
        db.session.commit()
        users_ids = new_project.get_users_ids_in_project()
        self.assertIsNotNone(users_ids)

    def test_get_users_ids_in_project(self):
        new_project = TeraProject()
        new_project.id_site = 1
        new_project.project_name = 'Project Name'
        db.session.add(new_project)
        db.session.commit()
        users = new_project.get_users_in_project()
        self.assertIsNotNone(users)

    def test_get_project_by_projectname(self):
        new_project = TeraProject()
        new_project.id_site = 1
        new_project.project_name = 'Project Name'
        db.session.add(new_project)
        db.session.commit()
        same_project = new_project.get_project_by_projectname(projectname='Project Name')
        self.assertEqual(same_project, new_project)

    def test_get_project_by_id(self):
        new_project = TeraProject()
        new_project.id_site = 1
        new_project.project_name = 'Project Name'
        db.session.add(new_project)
        db.session.commit()
        same_project = new_project.get_project_by_id(project_id=new_project.id_project)
        self.assertEqual(same_project, new_project)

    def test_insert_and_delete(self):
        new_project = TeraProject()
        new_project.id_site = 1
        new_project.project_name = 'Project Name'
        TeraProject.insert(project=new_project)
        # self.assertRaises(Exception, TeraProject.insert(project=new_project))
        id_to_del = new_project.id_project
        TeraProject.delete(id_todel=id_to_del)
        # try:
        #     TeraProject.insert(project=new_project)
        # except Exception as e:
        #     print(e)
        # self.assertRaises(Exception, TeraProject.insert(project=new_project))
        # don't know why the self.assertRaises doesnt work here