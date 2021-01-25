import unittest
import os

from modules.DatabaseModule.DBManager import DBManager

from opentera.db.models.TeraAsset import TeraAsset
from opentera.config.ConfigManager import ConfigManager
from tests.opentera.db.models.BaseModelsTest import BaseModelsTest


class TeraAssetTest(BaseModelsTest):

    filename = os.path.join(os.path.dirname(__file__), 'TeraAssetTest.db')

    SQLITE = {
        'filename': filename
    }

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




