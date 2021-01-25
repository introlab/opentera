import os
from tests.opentera.db.models.BaseModelsTest import BaseModelsTest
from sqlalchemy import exc
from opentera.db.Base import db

from opentera.db.models.TeraServerSettings import TeraServerSettings


class TeraServerSettingsTest(BaseModelsTest):

    filename = os.path.join(os.path.dirname(__file__), 'TeraServerSettingsTest.db')

    SQLITE = {
        'filename': filename
    }

    def test_nullable_args(self):
        new_settings = TeraServerSettings()
        db.session.add(new_settings)
        self.assertRaises(exc.IntegrityError, db.session.commit)
        db.session.rollback()
        new_settings.server_settings_name = 'Name'
        db.session.add(new_settings)
        self.assertRaises(exc.IntegrityError, db.session.commit)
        db.session.rollback()
        new_settings.server_settings_name = None
        new_settings.server_settings_value = 'Key'
        db.session.add(new_settings)
        self.assertRaises(exc.IntegrityError, db.session.commit)

    def test_unique_args(self):
        new_settings = TeraServerSettings()
        same_settings = TeraServerSettings()
        new_settings.server_settings_name = 'Name'
        same_settings.server_settings_name = 'Name'
        db.session.add(new_settings)
        db.session.add(same_settings)
        self.assertRaises(exc.IntegrityError, db.session.commit)

    def test_constants_check(self):
        for settings in TeraServerSettings.query.all():
            self.assertGreater(settings.id_server_settings, 0)
            self.assertIsNotNone(settings.server_settings_name)
            self.assertIsNotNone(settings.server_settings_value)
            self.assertEqual(settings.ServerDeviceTokenKey, 'TokenEncryptionKey')
            self.assertEqual(settings.ServerParticipantTokenKey, 'ParticipantTokenEncryptionKey')
            self.assertEqual(settings.ServerUUID, 'ServerUUID')
            self.assertEqual(settings.ServerVersions, 'ServerVersions')

    def test_set_and_get_settings(self):
        # test the get/set methods and the unique name
        TeraServerSettings.set_server_setting(setting_name='Nom Unique', setting_value='Key')
        new_settings = TeraServerSettings.get_server_setting(setting_name='Nom Unique')
        self.assertEqual(new_settings.server_settings_name, 'Nom Unique')
        self.assertEqual(new_settings.server_settings_value, 'Key')

    def test_generate_token_key(self):
        key_len_16 = TeraServerSettings.generate_token_key(length=16)
        key_len_32 = TeraServerSettings.generate_token_key(length=32)
        self.assertEqual(16, len(key_len_16))
        self.assertEqual(32, len(key_len_32))

    def test_get_server_setting_value(self):
        TeraServerSettings.set_server_setting(setting_name='Nom Unique', setting_value='Key')
        new_settings = TeraServerSettings.get_server_setting(setting_name='Nom Unique')
        self.assertEqual(new_settings.server_settings_value, TeraServerSettings.get_server_setting_value(setting_name='Nom Unique'))