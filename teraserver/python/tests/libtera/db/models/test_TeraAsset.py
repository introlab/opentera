import unittest
import os

from modules.DatabaseModule.DBManager import DBManager

from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraAsset import TeraAsset
from libtera.ConfigManager import ConfigManager


class TeraAssetTest(unittest.TestCase):

    filename = os.path.join(os.path.dirname(__file__), 'TeraAssetTest.db')

    SQLITE = {
        'filename': filename
    }

    def setUp(self):
        if os.path.isfile(self.filename):
            print('removing database')
            os.remove(self.filename)

        self.admin_user = None
        self.test_user = None

        self.config = ConfigManager()
        self.config.create_defaults()

        self.db_man = DBManager(self.config)

        self.db_man.open_local(self.SQLITE, echo=True, ram=True)

        # Creating default users / tests.
        self.db_man.create_defaults(self.config)

    def tearDown(self):
        pass

    def test_defaults(self):
        for asset in TeraAsset.query.all():
            self.assertGreater(len(asset.asset_name), 0)
            self.assertIsNotNone(asset.asset_session)
            self.assertIsNotNone(asset.asset_service_uuid)
            self.assertIsNotNone(asset.asset_uuid)

    def test_to_json(self):
        for asset in TeraAsset.query.all():
            json = asset.to_json()
            self.assertGreater(len(json), 0)

    def test_from_json(self):
        for asset in TeraAsset.query.all():
            json = asset.to_json()
            new_asset = TeraAsset()
            new_asset.from_json(json)
            self.assertEqual(new_asset.asset_name, asset.asset_name)
            self.assertEqual(new_asset.asset_service_uuid, asset.asset_service_uuid)
            self.assertEqual(new_asset.asset_type, asset.asset_type)
            self.assertEqual(new_asset.asset_uuid, asset.asset_uuid)
            self.assertEqual(new_asset.id_asset, asset.id_asset)
            self.assertEqual(new_asset.id_device, asset.id_device)
            self.assertEqual(new_asset.id_session, asset.id_session)




