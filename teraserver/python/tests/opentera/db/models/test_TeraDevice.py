from opentera.db.models.TeraDevice import TeraDevice
from tests.opentera.db.models.BaseModelsTest import BaseModelsTest
from modules.FlaskModule.FlaskModule import flask_app


class TeraDeviceTest(BaseModelsTest):

    def test_defaults(self):
        pass

    def test_json(self):
        with flask_app.app_context():
            device = TeraDevice.get_device_by_name('Apple Watch #W05P1')
            json = device.to_json()
            self.assertNotEqual(None, json)
            print(json)
