from BaseLoggingServiceAPITest import BaseLoggingServiceAPITest
from services.LoggingService.FlaskModule import flask_app


class LoggingServiceDBManagerTest(BaseLoggingServiceAPITest):
    test_endpoint = '/api/'

    def setUp(self):
        super().setUp()
        from services.LoggingService.FlaskModule import logging_api_ns
        from BaseLoggingServiceAPITest import FakeFlaskModule
        # Setup minimal API
        from services.LoggingService.API.QueryLogEntries import QueryLogEntries
        kwargs = {'flaskModule': FakeFlaskModule(config=BaseLoggingServiceAPITest.getConfig())}
        logging_api_ns.add_resource(QueryLogEntries, '/log_entries', resource_class_kwargs=kwargs)

        # Create test client
        self.test_client = flask_app.test_client()

    def tearDown(self):
        super().tearDown()

    def test_working(self):
        pass

