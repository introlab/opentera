from libtera.db.models.TeraService import TeraService


class DBManagerTeraServiceAccess:
    def __init__(self, service: TeraService):
        self.service = service

    def get_accessible_devices(self, admin_only=False):
        from libtera.db.models.TeraDevice import TeraDevice
        from libtera.db.models.TeraDeviceProject import TeraDeviceProject

        # Get projects availables to that service
        proj_id_list = self.get_accessible_projects_ids(admin_only=admin_only)

        query = TeraDevice.query.join(TeraDeviceProject).filter(TeraDeviceProject.id_project.in_(proj_id_list))
        return query.all()

    def get_accessible_devices_ids(self, admin_only=False):
        devices = []

        for device in self.get_accessible_devices(admin_only=admin_only):
            devices.append(device.id_device)

        return devices

    def get_accessible_projects(self, admin_only=False):
        project_list = []

        # Build project list - get projects where that service is associated
        from libtera.db.models.TeraServiceProject import TeraServiceProject
        service_projects = TeraServiceProject.get_projects_for_service(self.service.id_service)

        for service_project in service_projects:
            project_list.append(service_project.service_project_project)

        return project_list

    def get_accessible_projects_ids(self, admin_only=False):
        projects = []

        for project in self.get_accessible_projects(admin_only=admin_only):
            projects.append(project.id_project)

        return projects

    def get_accessible_sessions(self, admin_only=False):
        from libtera.db.models.TeraSession import TeraSession
        from libtera.db.models.TeraParticipant import TeraParticipant

        part_ids = self.get_accessible_participants_ids(admin_only=admin_only)
        return TeraSession.query.join(TeraSession.session_participants).\
            filter(TeraParticipant.id_participant.in_(part_ids)).all()

    def get_accessible_sessions_ids(self, admin_only=False):
        ses_ids = []

        for ses in self.get_accessible_sessions(admin_only=admin_only):
            ses_ids.append(ses.id_session)

        return ses_ids

    def get_accessible_participants(self, admin_only=False):
        project_id_list = self.get_accessible_projects_ids(admin_only=admin_only)
        participant_list = []

        from libtera.db.models.TeraParticipant import TeraParticipant
        participant_list.extend(TeraParticipant.query.filter(TeraParticipant.id_project.in_(project_id_list)))

        return participant_list

    def get_accessible_participants_ids(self, admin_only=False):
        parts = []

        for part in self.get_accessible_participants(admin_only=admin_only):
            parts.append(part.id_participant)

        return parts