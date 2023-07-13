from tests.opentera.db.models.BaseModelsTest import BaseModelsTest
from sqlalchemy import exc
from opentera.db.models.TeraProject import TeraProject
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraParticipantGroup import TeraParticipantGroup


class TeraProjectTest(BaseModelsTest):

    def test_nullable_args(self):
        with self._flask_app.app_context():
            new_project = TeraProject()
            new_project.id_site = 1
            new_project.project_name = None
            self.db.session.add(new_project)
            self.assertRaises(exc.IntegrityError, self.db.session.commit)
            self.db.session.rollback()
            new_project = TeraProject()
            new_project.id_site = None
            new_project.project_name = 'test_nullable_args'
            self.db.session.add(new_project)
            self.assertRaises(exc.IntegrityError, self.db.session.commit)

    def test_unique_args(self):
        pass

    def test_to_json(self):
        with self._flask_app.app_context():
            new_project = TeraProject()
            new_project.id_site = 1
            new_project.project_name = 'test_to_json'
            self.db.session.add(new_project)
            self.db.session.commit()
            new_project_json = new_project.to_json()
            new_project_json_minimal = new_project.to_json(minimal=True)
            self._check_json(new_project, project_test=new_project_json)
            self._check_json(new_project, project_test=new_project_json_minimal, minimal=True)

    def _check_json(self, project: TeraProject, project_test: dict, minimal=False):
        self.assertGreaterEqual(project_test['id_project'], project.id_project)
        self.assertEqual(project_test['id_site'], project.id_site)
        self.assertEqual(project_test['project_name'], project.project_name)
        if not minimal:
            self.assertEqual(project_test['site_name'], project.project_site.site_name)

    def test_to_json_create_event(self):
        with self._flask_app.app_context():
            new_project = TeraProject()
            new_project.id_site = 1
            new_project.project_name = 'test_to_json_create_event'
            self.db.session.add(new_project)
            self.db.session.commit()
            new_project_json = new_project.to_json_create_event()
            self._check_json(new_project, project_test=new_project_json, minimal=True)

    def test_to_json_update_event(self):
        with self._flask_app.app_context():
            new_project = TeraProject()
            new_project.id_site = 1
            new_project.project_name = 'test_to_json_update_event'
            self.db.session.add(new_project)
            self.db.session.commit()
            new_project_json = new_project.to_json_update_event()
            self._check_json(new_project, project_test=new_project_json, minimal=True)

    def test_to_json_delete_event(self):
        with self._flask_app.app_context():
            new_project = TeraProject()
            new_project.id_site = 1
            new_project.project_name = 'test_to_json_delete_event'
            self.db.session.add(new_project)
            self.db.session.commit()
            new_project_json = new_project.to_json_delete_event()
            self.assertGreaterEqual(new_project_json['id_project'], 1)

    def test_get_users_ids_in_project(self):
        with self._flask_app.app_context():
            new_project = TeraProject()
            new_project.id_site = 1
            new_project.project_name = 'test_get_users_ids_in_project'
            self.db.session.add(new_project)
            self.db.session.commit()
            users_ids = new_project.get_users_ids_in_project()
            self.assertIsNotNone(users_ids)

    def test_get_users_in_project(self):
        with self._flask_app.app_context():
            new_project = TeraProject()
            new_project.id_site = 1
            new_project.project_name = 'test_get_users_in_project'
            self.db.session.add(new_project)
            self.db.session.commit()
            users = new_project.get_users_in_project()
            self.assertIsNotNone(users)

    def test_get_project_by_projectname(self):
        with self._flask_app.app_context():
            new_project = TeraProject()
            new_project.id_site = 1
            new_project.project_name = 'test_get_project_by_projectname'
            self.db.session.add(new_project)
            self.db.session.commit()
            same_project = new_project.get_project_by_projectname(projectname=new_project.project_name)
            self.assertEqual(same_project, new_project)

    def test_get_project_by_id(self):
        with self._flask_app.app_context():
            new_project = TeraProject()
            new_project.id_site = 1
            new_project.project_name = 'test_get_project_by_id'
            self.db.session.add(new_project)
            self.db.session.commit()
            same_project = new_project.get_project_by_id(project_id=new_project.id_project)
            self.assertEqual(same_project, new_project)

    def test_insert_and_delete(self):
        with self._flask_app.app_context():
            new_project = TeraProject()
            new_project.id_site = 1
            new_project.project_name = 'test_insert_and_delete'
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

    def test_update_set_inactive(self):
        with self._flask_app.app_context():
            new_project = TeraProject()
            new_project.id_site = 1
            new_project.project_name = 'test_update_set_inactive'
            self.db.session.add(new_project)
            self.db.session.commit()

            # Create participants
            participants = []
            for i in range(3):
                part = TeraParticipant()
                part.id_project = new_project.id_project
                part.participant_name = 'Participant #' + str(i+1)
                part.participant_enabled = True
                TeraParticipant.insert(part)
                participants.append(part)

            for part in participants:
                self.assertTrue(part.participant_enabled)

            # Associate devices
            devices = []
            for i in range(2):
                device = TeraDevice()
                device.device_name = 'Device #' + str(i+1)
                device.id_device_type = 1
                TeraDevice.insert(device)
                devices.append(device)
            part = participants[0]
            for device in devices:
                device.device_participants.append(part)
            self.db.session.commit()

            # Set project inactive
            TeraProject.update(new_project.id_project, {'project_enabled': False})

            # Check if participants are inactive
            for part in participants:
                self.assertFalse(part.participant_enabled)

            # Check that associated devices are not anymore
            for device in devices:
                self.assertEqual([], device.device_participants)

    def test_soft_delete(self):
        with self._flask_app.app_context():
            # Create new
            project = TeraProject()
            project.project_name = "Test project"
            project.id_site = 1
            TeraProject.insert(project)
            self.assertIsNotNone(project.id_project)
            id_project = project.id_project

            # Soft delete
            TeraProject.delete(id_project)

            # Make sure it is deleted
            self.assertIsNone(TeraProject.get_project_by_id(id_project))

            # Query, with soft delete flag
            project = TeraProject.query.filter_by(id_project=id_project) \
                .execution_options(include_deleted=True).first()
            self.assertIsNotNone(project)
            self.assertIsNotNone(project.deleted_at)

    def test_hard_delete(self):
        with self._flask_app.app_context():
            # Create new
            project = TeraProject()
            project.project_name = "Test project"
            project.id_site = 1
            TeraProject.insert(project)
            self.assertIsNotNone(project.id_project)
            id_project = project.id_project

            # Create a new participant in that project
            participant = TeraParticipant()
            participant.participant_name = "Test participant"
            participant.id_project = id_project
            TeraParticipant.insert(participant)
            self.assertIsNotNone(participant.id_participant)
            id_participant = participant.id_participant

            # Soft delete to prevent relationship integrity errors as we want to test hard-delete cascade here
            TeraParticipant.delete(id_participant)
            TeraProject.delete(id_project)

            # Check that relationships are still there
            self.assertIsNone(TeraParticipant.get_participant_by_id(id_participant))
            self.assertIsNotNone(TeraParticipant.get_participant_by_id(id_participant, True))
            self.assertIsNone(TeraProject.get_project_by_id(id_project))
            self.assertIsNotNone(TeraProject.get_project_by_id(id_project, True))

            # Hard delete
            TeraProject.delete(id_project, hard_delete=True)

            # Make sure eveything is deleted
            self.assertIsNone(TeraParticipant.get_participant_by_id(id_participant, True))
            self.assertIsNone(TeraProject.get_project_by_id(id_project, True))

    def test_project_relationships_deletion_and_access(self):
        with self._flask_app.app_context():
            # Create new
            project = TeraProject()
            project.project_name = "Test project"
            project.id_site = 1
            TeraProject.insert(project)
            self.assertIsNotNone(project.id_project)
            id_project = project.id_project

            # Create participant groups
            group = TeraParticipantGroup()
            group.participant_group_name = "Test participant group 1"
            group.id_project = id_project
            TeraParticipantGroup.insert(group)
            self.assertIsNotNone(group.id_participant_group)
            id_participant_group1 = group.id_participant_group

            participant = TeraParticipant()
            participant.participant_name = "Test participant"
            participant.id_project = 1
            participant.id_participant_group = id_participant_group1
            TeraParticipant.insert(participant)
            self.assertIsNotNone(participant.id_participant)
            id_participant = participant.id_participant

            group = TeraParticipantGroup()
            group.participant_group_name = "Test participant group 2"
            group.id_project = id_project
            TeraParticipantGroup.insert(group)
            self.assertIsNotNone(group.id_participant_group)
            id_participant_group2 = group.id_participant_group

            self.assertEqual(2, len(project.project_participants_groups))

            # Soft delete one group
            TeraParticipantGroup.delete(id_participant_group2)

            self.db.session.expire_all()
            project = TeraProject.get_project_by_id(id_project)
            self.assertEqual(1, len(project.project_participants_groups))

            self.db.session.expire_all()
            project = TeraProject.get_project_by_id(id_project, with_deleted=True)
            self.assertEqual(1, len(project.project_participants_groups))  # Don't get deleted groups even with flag

            self.assertEqual(1, len(project.project_participants_groups[0].participant_group_participants))
            TeraParticipant.delete(id_participant)
            self.db.session.expire_all()
            project = TeraProject.get_project_by_id(id_project)
            self.assertEqual(0, len(project.project_participants_groups[0].participant_group_participants))


