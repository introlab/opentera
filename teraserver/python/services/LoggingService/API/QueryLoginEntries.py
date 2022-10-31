from flask_restx import Resource, reqparse
from sqlalchemy.exc import InvalidRequestError
from services.LoggingService.FlaskModule import logging_api_ns as api
from opentera.services.ServiceAccessManager import ServiceAccessManager, current_user_client
from services.LoggingService.libloggingservice.db.models.LoginEntry import LoginEntry
from services.LoggingService.Globals import service

# Parser definition(s)
get_parser = api.parser()


class QueryLoginEntries(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.expect(get_parser)
    @api.doc(description='Query all login entries ',
             responses={200: 'Success - To be documented',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Logged user doesn\'t have permission to access the requested data'})
    @ServiceAccessManager.token_required(allow_dynamic_tokens=True, allow_static_tokens=False)
    def get(self):

        # TODO Only allow superadmins to query logs?
        if current_user_client and current_user_client.user_superadmin:

            # Request access from server
            params = {
                'from_user_uuid': current_user_client.user_uuid,
                'with_user_uuids': True,
                'with_projets_ids': True,
                'with_participants_uuids': True,
                'with_device_uuids': True,
                'with_sites_ids': True,
                'admin': False
            }

            response = service.get_from_opentera('/api/service/access', params)

            try:
                all_entries = LoginEntry.query.all()
                results = []
                for entry in all_entries:
                    results.append(entry.to_json(minimal=False))
                return results

            except InvalidRequestError:
                return '', 500

        return 'Unauthorized', 403
