from modules.DatabaseModule.DBManager import DBManager
from modules.DatabaseModule.DBManagerTeraDeviceAccess import DBManagerTeraDeviceAccess
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraParticipantGroup import TeraParticipantGroup
from opentera.db.models.TeraService import TeraService
from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraProject import TeraProject
from opentera.db.models.TeraSite import TeraSite
from opentera.db.models.TeraSession import TeraSession
from tests.opentera.db.models.BaseModelsTest import BaseModelsTest


class DBManagerTeraDeviceAccessTest(BaseModelsTest):
    """
    Tests for the DBManagerTeraDeviceAccess class.
    """

    def test_device_query_sesion(self):
        """
        Query session for a device with id.
        """
        with self._flask_app.app_context():
            devices = TeraDevice.query.all()
            for device in devices:
                device_access : DBManagerTeraDeviceAccess = DBManager.deviceAccess(device)
                # Query invalid session
                session = device_access.query_session(session_id=0)
                self.assertIsNone(session)

    def test_device_query_existing_session(self):
        """
        Query session for a device with existing session.
        """
        with self._flask_app.app_context():
            devices = TeraDevice.query.all()
            for device in devices:
                device_access : DBManagerTeraDeviceAccess = DBManager.deviceAccess(device)
                pass


    def test_device_get_accessible_sessions_ids(self):
        """
        Get accessible sessions for a device.
        """
        with self._flask_app.app_context():
            devices = TeraDevice.query.all()
            for device in devices:
                device_access : DBManagerTeraDeviceAccess = DBManager.deviceAccess(device)
                pass

    def test_device_get_accessible_session_types_ids(self):
        """
        Get accessible session types for a device.
        """
        with self._flask_app.app_context():
            devices = TeraDevice.query.all()
            for device in devices:
                device_access : DBManagerTeraDeviceAccess = DBManager.deviceAccess(device)
                pass

    def test_device_get_accessible_assets(self):
        """
        Get accessible assets for a device.
        """
        with self._flask_app.app_context():
            devices = TeraDevice.query.all()
            for device in devices:
                device_access : DBManagerTeraDeviceAccess = DBManager.deviceAccess(device)
                pass

    def test_device_get_accessible_services(self):
        """
        Get accessible services for a device.
        """
        with self._flask_app.app_context():
            devices = TeraDevice.query.all()
            for device in devices:
                device_access : DBManagerTeraDeviceAccess = DBManager.deviceAccess(device)
                pass

    def test_device_get_accessible_tests_types_ids(self):
        """
        Get accessible tests types for a device.
        """
        with self._flask_app.app_context():
            devices = TeraDevice.query.all()
            for device in devices:
                device_access : DBManagerTeraDeviceAccess = DBManager.deviceAccess(device)
                pass
