from tests.opentera.db.models.BaseModelsTest import BaseModelsTest
from sqlalchemy import exc
from opentera.db.models.TeraServerSettings import TeraServerSettings
from modules.FlaskModule.FlaskModule import flask_app


class TeraServerSettingsTest(BaseModelsTest):

    def test_nullable_args(self):
        with flask_app.app_context():
            new_settings = TeraServerSettings()
            self.db.session.add(new_settings)
            self.assertRaises(exc.IntegrityError, self.db.session.commit)
            self.db.session.rollback()
            new_settings.server_settings_name = 'test_nullable_args'
            self.db.session.add(new_settings)
            self.assertRaises(exc.IntegrityError, self.db.session.commit)
            self.db.session.rollback()
            new_settings.server_settings_name = None
            new_settings.server_settings_value = 'Key'
            self.db.session.add(new_settings)
            self.assertRaises(exc.IntegrityError, self.db.session.commit)
            self.db.session.rollback()

    def test_unique_args(self):
        with flask_app.app_context():
            new_settings = TeraServerSettings()
            same_settings = TeraServerSettings()
            new_settings.server_settings_name = 'test_unique_args'
            same_settings.server_settings_name = 'test_unique_args'
            self.db.session.add(new_settings)
            self.db.session.add(same_settings)
            self.assertRaises(exc.IntegrityError, self.db.session.commit)
            self.db.session.rollback()

    def test_constants_check(self):
        with flask_app.app_context():
            for settings in TeraServerSettings.query.all():
                self.assertGreater(settings.id_server_settings, 0)
                self.assertIsNotNone(settings.server_settings_name)
                self.assertIsNotNone(settings.server_settings_value)
                self.assertEqual(settings.ServerDeviceTokenKey, 'TokenEncryptionKey')
                self.assertEqual(settings.ServerParticipantTokenKey, 'ParticipantTokenEncryptionKey')
                self.assertEqual(settings.ServerUUID, 'ServerUUID')
                self.assertEqual(settings.ServerVersions, 'ServerVersions')

    def test_set_and_get_settings(self):
        with flask_app.app_context():
            # test the get/set methods and the unique name
            TeraServerSettings.set_server_setting(setting_name='test_set_and_get_settings', setting_value='Key')
            new_settings = TeraServerSettings.get_server_setting(setting_name='test_set_and_get_settings')
            self.assertEqual(new_settings.server_settings_name, 'test_set_and_get_settings')
            self.assertEqual(new_settings.server_settings_value, 'Key')

    def test_generate_token_key(self):
        with flask_app.app_context():
            key_len_16 = TeraServerSettings.generate_token_key(length=16)
            key_len_32 = TeraServerSettings.generate_token_key(length=32)
            self.assertEqual(16, len(key_len_16))
            self.assertEqual(32, len(key_len_32))

    def test_get_server_setting_value(self):
        with flask_app.app_context():
            TeraServerSettings.set_server_setting(setting_name='test_get_server_setting_value', setting_value='Key')
            new_settings = TeraServerSettings.get_server_setting(setting_name='test_get_server_setting_value')
            self.assertEqual(new_settings.server_settings_value,
                             TeraServerSettings.get_server_setting_value(setting_name='test_get_server_setting_value'))
