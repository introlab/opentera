from services.EmailService.ConfigManager import ConfigManager
from services.EmailService.libemailservice.db.DBManager import DBManager
import unittest
from flask import Flask

from services.EmailService.libemailservice.db.models import EmailTemplate


class EmailServiceEmailTemplateTest(unittest.TestCase):

    def setUp(self):
        self.flask_app = Flask('EmailServiceEmailTemplateTest')
        with self.flask_app.app_context():
            self.config = ConfigManager()
            self.config.create_defaults()
            self.dbman = DBManager(app=self.flask_app, test=True)
            self.dbman.open_local({}, False, True)
            self.dbman.create_defaults(self.config, test=True)

    def tearDown(self):
        with self.flask_app.app_context():
            self.dbman.db.session.rollback()

    def test_get_template_by_id(self):
        with self.flask_app.app_context():
            template = EmailTemplate.get_template_by_id(0)
            self.assertIsNone(template)

            template = EmailTemplate.get_template_by_id(1)
            self.assertIsNotNone(template)

    def test_get_project_template_by_key(self):
        with self.flask_app.app_context():
            template = EmailTemplate.get_template_by_key('PROJECT_EMAIL')
            self.assertIsNotNone(template)
            self.assertIsNotNone(template.id_project)

    def test_get_global_template_by_key(self):
        with self.flask_app.app_context():
            template = EmailTemplate.get_template_by_key('GENERAL_TEST_EMAIL')
            self.assertIsNotNone(template)

    def test_get_site_template_by_key(self):
        with self.flask_app.app_context():
            template = EmailTemplate.get_template_by_key('SITE_EMAIL')
            self.assertIsNotNone(template)
            self.assertIsNotNone(template.id_site)

    def test_get_template_by_key_wrong_key(self):
        with self.flask_app.app_context():
            template = EmailTemplate.get_template_by_key('WRONG_KEY')
            self.assertIsNone(template)

    def test_get_overriden_template_by_key(self):
        with self.flask_app.app_context():
            template = EmailTemplate.get_template_by_key('GENERAL_TEST_EMAIL', project_id=1)
            self.assertIsNotNone(template)
            self.assertTrue('PROJECT' in template.email_template)
            self.assertTrue('GLOBAL' in template.email_template)
            self.assertEqual(template.id_project, 1)

    def test_get_not_overriden_template_by_key(self):
        with self.flask_app.app_context():
            template = EmailTemplate.get_template_by_key('GENERAL_TEST_EMAIL', project_id=2)
            self.assertIsNotNone(template)
            self.assertFalse('PROJECT' in template.email_template)
            self.assertTrue('GLOBAL' in template.email_template)
            self.assertIsNone(template.id_project)
            self.assertIsNone(template.id_site)
