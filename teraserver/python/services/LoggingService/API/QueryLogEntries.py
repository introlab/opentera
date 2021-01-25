from flask_restx import Resource, reqparse
from sqlalchemy.exc import InvalidRequestError
from services.LoggingService.FlaskModule import logging_api_ns as api
from opentera.services.ServiceAccessManager import ServiceAccessManager, current_user_client
from services.LoggingService.libloggingservice.db.models.LogEntry import LogEntry

# Parser definition(s)
get_parser = api.parser()


class QueryLogEntries(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.parser = reqparse.RequestParser()

    @api.expect(get_parser)
    @api.doc(description='To be documented '
                         'To be documented',
             responses={200: 'Success - To be documented',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Logged user doesn\'t have permission to access the requested data'})
    @ServiceAccessManager.token_required
    def get(self):

        # TODO Only allow superadmins to query logs?
        if current_user_client and current_user_client.user_superadmin:
            try:
                all_entries = LogEntry.query.all()
                results = []
                for entry in all_entries:
                    results.append(entry.to_json(minimal=False))
                return results

            except InvalidRequestError:
                return '', 500

        return 'Unauthorized', 403
