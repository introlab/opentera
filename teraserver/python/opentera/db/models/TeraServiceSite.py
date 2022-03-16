from opentera.db.Base import db, BaseModel


class TeraServiceSite(db.Model, BaseModel):
    __tablename__ = 't_services_sites'
    id_service_site = db.Column(db.Integer, db.Sequence('id_service_site_sequence'), primary_key=True,
                                autoincrement=True)
    id_service = db.Column(db.Integer, db.ForeignKey('t_services.id_service', ondelete='cascade'), nullable=False)
    id_site = db.Column(db.Integer, db.ForeignKey('t_sites.id_site', ondelete='cascade'), nullable=False)

    service_site_service = db.relationship("TeraService", viewonly=True)
    service_site_site = db.relationship("TeraSite", viewonly=True)

    def __init__(self):
        pass

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        ignore_fields.extend(['service_site_service', 'service_site_site'])

        if minimal:
            ignore_fields.extend([])

        return super().to_json(ignore_fields=ignore_fields)

    @staticmethod
    def get_services_for_site(id_site: int):
        return TeraServiceSite.query.filter_by(id_site=id_site).all()

    @staticmethod
    def get_sites_for_service(id_service: int):
        return TeraServiceSite.query.filter_by(id_service=id_service).all()

    @staticmethod
    def get_service_site_by_id(service_site_id: int):
        return TeraServiceSite.query.filter_by(id_service_site=service_site_id).first()

    @staticmethod
    def get_service_site_for_service_site(site_id: int, service_id: int):
        return TeraServiceSite.query.filter_by(id_site=site_id, id_service=service_id).first()

    @staticmethod
    def create_defaults(test=False):
        if test:
            from opentera.db.models.TeraService import TeraService
            from opentera.db.models.TeraSite import TeraSite

            site1 = TeraSite.get_site_by_sitename('Default Site')
            site2 = TeraSite.get_site_by_sitename('Top Secret Site')

            service_rehab = TeraService.get_service_by_key('VideoRehabService')
            service_filetransfer = TeraService.get_service_by_key('FileTransferService')
            service_logging = TeraService.get_service_by_key('LoggingService')

            service_site = TeraServiceSite()
            service_site.id_site = site1.id_site
            service_site.id_service = service_rehab.id_service
            db.session.add(service_site)

            service_site = TeraServiceSite()
            service_site.id_site = site1.id_site
            service_site.id_service = service_filetransfer.id_service
            db.session.add(service_site)

            service_site = TeraServiceSite()
            service_site.id_site = site1.id_site
            service_site.id_service = service_logging.id_service
            db.session.add(service_site)

            service_site = TeraServiceSite()
            service_site.id_site = site2.id_site
            service_site.id_service = service_filetransfer.id_service
            db.session.add(service_site)

            db.session.commit()
        else:
            # Automatically associate services that are in a project to that site
            from opentera.db.models.TeraServiceProject import TeraServiceProject
            for sp in TeraServiceProject.query_with_filters():
                project_site_id = sp.service_project_project.id_site
                if not TeraServiceSite.get_service_site_for_service_site(site_id=project_site_id,
                                                                         service_id=
                                                                         sp.service_project_service.id_service):
                    # No association - create a new one
                    service_site = TeraServiceSite()
                    service_site.id_site = project_site_id
                    service_site.id_service = sp.service_project_service.id_service
                    db.session.add(service_site)
                    db.session.commit()

    @staticmethod
    def delete_with_ids(service_id: int, site_id: int):
        delete_obj = TeraServiceSite.query.filter_by(id_service=service_id, id_site=site_id).first()
        if delete_obj:
            TeraServiceSite.delete(delete_obj.id_service_site)

    @classmethod
    def delete(cls, id_todel):
        from opentera.db.models.TeraServiceProject import TeraServiceProject
        # Delete all association with projects for that site
        delete_obj = TeraServiceSite.query.filter_by(id_service_site=id_todel).first()

        if delete_obj:
            projects = TeraServiceProject.get_projects_for_service(delete_obj.id_service)
            for service_project in projects:
                TeraServiceProject.delete(service_project.id_service_project)

            from opentera.db.models.TeraSessionTypeSite import TeraSessionTypeSite
            session_types = TeraSessionTypeSite.get_session_type_site_for_site_and_service(
                site_id=delete_obj.id_site, service_id=delete_obj.id_service)
            for session_type in session_types:
                TeraSessionTypeSite.delete(session_type.id_session_type_site)

            # Ok, delete it
            super().delete(id_todel)
