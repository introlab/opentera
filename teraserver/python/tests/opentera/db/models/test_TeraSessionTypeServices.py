from tests.opentera.db.models.BaseModelsTest import BaseModelsTest
from opentera.db.models.TeraSessionTypeServices import TeraSessionTypeServices
from opentera.db.models.TeraSessionType import TeraSessionType
from opentera.db.models.TeraSessionTypeSite import TeraSessionTypeSite
from opentera.db.models.TeraSessionTypeProject import TeraSessionTypeProject
from opentera.db.models.TeraService import TeraService
from opentera.db.models.TeraServiceProject import TeraServiceProject
from opentera.db.models.TeraServiceSite import TeraServiceSite


class TeraSessionTypeServicesTest(BaseModelsTest):

    def test_to_json_full_and_minimal(self):
        with self._flask_app.app_context():
            sts_list = TeraSessionTypeServices.query.all()
            self.assertGreater(len(sts_list), 0)
            for minimal in [False, True]:
                for sts in sts_list:
                    self.assertIsNotNone(sts)
                    json = sts.to_json(minimal=minimal)
                    self.assertNotEqual(None, json)

                    if not minimal:
                        self.assertTrue('id_session_type_service' in json)
                        self.assertTrue('id_session_type' in json)
                        self.assertTrue('id_service' in json)
                        self.assertFalse('session_type_service_session_type' in json)
                        self.assertFalse('session_type_service_service' in json)
                    else:
                        # Same a minimal for now
                        self.assertTrue('id_session_type_service' in json)
                        self.assertTrue('id_session_type' in json)
                        self.assertTrue('id_service' in json)
                        self.assertFalse('session_type_service_session_type' in json)
                        self.assertFalse('session_type_service_service' in json)

    def test_from_json(self):
        with self._flask_app.app_context():
            for sts in TeraSessionTypeServices.query.all():
                json = sts.to_json()
                new_sts = TeraSessionTypeServices()
                new_sts.from_json(json)
                self.assertEqual(new_sts.id_session_type_service, sts.id_session_type_service)
                self.assertEqual(new_sts.id_session_type, sts.id_session_type)
                self.assertEqual(new_sts.id_service, sts.id_service)

    def test_get_with_id(self):
        with self._flask_app.app_context():
            sts_ids = [sts.id_session_type_service for sts in TeraSessionTypeServices.query.all()]
            self.db.session.expire_all()  # Clear cache
            for sts_id in sts_ids:
                test_sts = TeraSessionTypeServices.get_session_type_service_by_id(sts_id)
                self.assertEqual(test_sts.id_session_type_service, sts_id)

    def test_get_services_for_session_type(self):
        with self._flask_app.app_context():
            ses_types: list[TeraSessionType] = TeraSessionType.query.all()
            for ses_type in ses_types:
                secondary_services = ses_type.session_type_secondary_services
                self.db.session.expire_all()  # Clear cache
                associated_services = TeraSessionTypeServices.get_services_for_session_type(ses_type.id_session_type)
                self.assertEqual(len(secondary_services), len(associated_services))

    def test_get_session_types_for_service(self):
        with self._flask_app.app_context():
            services: list[TeraService] = TeraService.query.all()
            for service in services:
                sts_list = TeraSessionTypeServices.get_sessions_types_for_service(service.id_service)
                if sts_list:
                    for sts in sts_list:
                        st: TeraSessionType = TeraSessionType.get_session_type_by_id(sts.id_session_type)
                        self.assertTrue(sts.id_service in [serv.id_service for serv in st.session_type_secondary_services])

    def test_check_integrity_not_associated_to_site(self):
        with self._flask_app.app_context():
            st = TeraSessionType()
            st.session_type_name = 'Test'
            st.session_type_online = False
            st.session_type_color = ''
            st.session_type_category = 1
            TeraSessionType.insert(st)

            st_site = TeraSessionTypeSite()
            st_site.id_site = 1
            st_site.id_session_type = st.id_session_type
            TeraSessionTypeSite.insert(st_site)

            self.assertTrue(st.id_session_type in [s_type.id_session_type for s_type in
                                                   TeraSessionTypeSite.get_sessions_types_for_site(st_site.id_site)])

            # Try to associate EmailService, which is not in the site
            service: TeraService = TeraService.get_service_by_key('EmailService')
            self.assertFalse(service.id_service in [s.id_service for s in
                                                    TeraServiceSite.get_services_for_site(st_site.id_site)])

            sts = TeraSessionTypeServices()
            sts.id_service = service.id_service
            sts.id_session_type = st.id_session_type
            TeraSessionTypeServices.insert(sts)

            self.assertTrue(service.id_service in [s.id_service for s in
                                                    TeraServiceSite.get_services_for_site(st_site.id_site)])

            tss = TeraServiceSite.get_service_site_for_service_site(st_site.id_site, service.id_service)
            TeraServiceSite.delete(tss.id_service_site)
            TeraSessionType.delete(st.id_session_type)

    def test_check_integrity_not_associated_to_project(self):
        with self._flask_app.app_context():
            st = TeraSessionType()
            st.session_type_name = 'Test'
            st.session_type_online = False
            st.session_type_color = ''
            st.session_type_category = 1
            TeraSessionType.insert(st)

            st_site = TeraSessionTypeSite()
            st_site.id_site = 1
            st_site.id_session_type = st.id_session_type
            TeraSessionTypeSite.insert(st_site)

            self.assertTrue(st.id_session_type in [s_type.id_session_type for s_type in
                                                   TeraSessionTypeSite.get_sessions_types_for_site(st_site.id_site)])

            st_project = TeraSessionTypeProject()
            st_project.id_project = 1
            st_project.id_session_type = st.id_session_type
            TeraSessionTypeProject.insert(st_project)

            self.assertTrue(st.id_session_type in [s_type.id_session_type for s_type in
                                                  TeraSessionTypeProject.
                            get_sessions_types_for_project(st_project.id_project)])

            service: TeraService = TeraService.get_service_by_key('EmailService')

            site_service = TeraServiceSite()
            site_service.id_service = service.id_service
            site_service.id_site = st_site.id_site
            TeraServiceSite.insert(site_service)

            self.assertTrue(service.id_service in [serv.id_service for serv in
                                                   TeraServiceSite.get_services_for_site(site_service.id_site)])

            # Try to associate EmailService, which is not in the project
            self.assertFalse(service.id_service in [s.id_service for s in
                                                    TeraServiceProject.get_services_for_project(st_project.id_project)])

            sts = TeraSessionTypeServices()
            sts.id_service = service.id_service
            sts.id_session_type = st.id_session_type
            TeraSessionTypeServices.insert(sts)

            self.assertTrue(service.id_service in [s.id_service for s in
                                                    TeraServiceProject.get_services_for_project(st_project.id_project)])

            tsp = TeraServiceProject.get_service_project_for_service_project(st_project.id_project, service.id_service)
            TeraServiceProject.delete(tsp.id_service_project)
            tss = TeraServiceSite.get_service_site_for_service_site(st_site.id_site, service.id_service)
            TeraServiceSite.delete(tss.id_service_site)
            TeraSessionType.delete(st.id_session_type)


    def test_check_integrity_not_associated_to_site_and_project(self):
        with self._flask_app.app_context():
            st = TeraSessionType()
            st.session_type_name = 'Test'
            st.session_type_online = False
            st.session_type_color = ''
            st.session_type_category = 1
            TeraSessionType.insert(st)

            st_site = TeraSessionTypeSite()
            st_site.id_site = 1
            st_site.id_session_type = st.id_session_type
            TeraSessionTypeSite.insert(st_site)

            self.assertTrue(st.id_session_type in [s_type.id_session_type for s_type in
                                                   TeraSessionTypeSite.get_sessions_types_for_site(st_site.id_site)])

            st_project = TeraSessionTypeProject()
            st_project.id_project = 1
            st_project.id_session_type = st.id_session_type
            TeraSessionTypeProject.insert(st_project)

            self.assertTrue(st.id_session_type in [s_type.id_session_type for s_type in
                                                   TeraSessionTypeProject.
                            get_sessions_types_for_project(st_project.id_project)])

            service: TeraService = TeraService.get_service_by_key('EmailService')


            # Try to associate EmailService, which is not in the project and site
            self.assertFalse(service.id_service in [serv.id_service for serv in
                                                   TeraServiceSite.get_services_for_site(st_site.id_site)])
            self.assertFalse(service.id_service in [s.id_service for s in
                                                    TeraServiceProject.get_services_for_project(st_project.id_project)])

            sts = TeraSessionTypeServices()
            sts.id_service = service.id_service
            sts.id_session_type = st.id_session_type
            TeraSessionTypeServices.insert(sts)

            self.assertTrue(service.id_service in [serv.id_service for serv in
                                                    TeraServiceSite.get_services_for_site(st_site.id_site)])
            self.assertTrue(service.id_service in [s.id_service for s in
                                                   TeraServiceProject.get_services_for_project(st_project.id_project)])

            tsp = TeraServiceProject.get_service_project_for_service_project(st_project.id_project, service.id_service)
            TeraServiceProject.delete(tsp.id_service_project)
            tss = TeraServiceSite.get_service_site_for_service_site(st_site.id_site, service.id_service)
            TeraServiceSite.delete(tss.id_service_site)
            TeraSessionType.delete(st.id_session_type)

    def test_delete(self):
        with self._flask_app.app_context():
            service: TeraService = TeraService.get_service_by_key('EmailService')

            st = TeraSessionType()
            st.session_type_name = 'Test'
            st.session_type_online = False
            st.session_type_color = ''
            st.session_type_category = 1
            TeraSessionType.insert(st)

            sts = TeraSessionTypeServices()
            sts.id_service = service.id_service
            sts.id_session_type = st.id_session_type
            TeraSessionTypeServices.insert(sts)

            sts_id = sts.id_session_type_service
            TeraSessionTypeServices.delete(sts_id)
            self.assertIsNone(TeraSessionTypeServices.get_session_type_service_by_id(sts_id))
            TeraSessionType.delete(st.id_session_type)