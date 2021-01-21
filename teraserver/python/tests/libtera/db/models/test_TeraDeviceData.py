# import unittest
# from modules.DatabaseModule.DBManager import DBManager
# from opentera.db.models.TeraDeviceData import TeraDeviceData
# import os
# from opentera.ConfigManager import ConfigManager
# from sqlalchemy.exc import InvalidRequestError
#
#
# class TeraDeviceDataTest(unittest.TestCase):
#
#     filename = os.path.join(os.path.dirname(__file__), 'TeraDeviceDataTest.db')
#
#     SQLITE = {
#         'filename': filename
#     }
#
#     def setUp(self):
#         if os.path.isfile(self.filename):
#             print('removing database')
#             os.remove(self.filename)
#
#         self.config = ConfigManager()
#         # Create default config
#         self.config.create_defaults()
#         self.db_man = DBManager(self.config)
#         self.db_man.open_local(self.SQLITE)
#
#         # Creating default users / tests.
#         self.db_man.create_defaults(self.config)
#
#     def test_defaults(self):
#         pass
#
#     def test_query_filters(self):
#         # A particular device
#         val = TeraDeviceData.query_with_filters({'id_device': 1, 'id_session': 1, 'id_device_data': 1})
#         self.assertEqual(len(val), 1)
#
#         # All devices
#         val = TeraDeviceData.query_with_filters(None)
#         self.assertEqual(len(val), 2)
#
#         # A non existing device
#         val = TeraDeviceData.query_with_filters({'id_device': 5, 'id_session': 1, 'id_device_data': 1})
#         self.assertEqual(len(val), 0)
#
#         # A non existing field will throw an exception
#         def should_raise_exception():
#             TeraDeviceData.query_with_filters({'id_device_invalid': 1, 'id_session': 1, 'id_device_data': 1})
#
#         self.assertRaises(InvalidRequestError, should_raise_exception)
#
