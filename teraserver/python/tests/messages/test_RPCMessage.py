import unittest

from opentera.messages.python.RPCMessage_pb2 import RPCMessage, Value
import datetime


class RPCMessageTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_valuetypes(self):
        message = RPCMessage()
        message.method = 'online_users'
        message.timestamp = datetime.datetime.now().timestamp()
        message.id = 1
        message.reply_to = 'reply-to-name'

        test_double = Value()
        test_double.double_value = 2.0

        test_float = Value()
        test_float.float_value = 4.0

        test_int64 = Value()
        test_int64.int_value = 5

        test_uint64 = Value()
        test_uint64.uint_value = 7

        test_bool = Value()
        test_bool.bool_value = True

        test_bytes = Value()
        test_bytes.bytes_value = b'12345'

        test_string = Value()
        test_string.string_value = 'Hello World!'

        # Extend args
        message.args.extend([test_double, test_float, test_int64, test_uint64, test_bool, test_bytes, test_string])

        # Verify values
        self.assertEqual(2.0, getattr(message.args[0], 'double_value'))
        self.assertEqual(4.0, getattr(message.args[1], 'float_value'))
        self.assertEqual(5, getattr(message.args[2], 'int_value'))
        self.assertEqual(7, getattr(message.args[3], 'uint_value'))
        self.assertEqual(True, getattr(message.args[4], 'bool_value'))
        self.assertEqual(b'12345', getattr(message.args[5], 'bytes_value'))
        self.assertEqual('Hello World!', getattr(message.args[6], 'string_value'))

        # Check arg size
        self.assertEqual(7, len(message.args))

        # Test WhichOneof
        for value in message.args:
            self.assertNotEqual(None, getattr(value, value.WhichOneof('arg_value')))
