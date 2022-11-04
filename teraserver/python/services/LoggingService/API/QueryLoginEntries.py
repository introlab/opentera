from flask_restx import Resource, reqparse
from sqlalchemy.exc import InvalidRequestError
from services.LoggingService.FlaskModule import logging_api_ns as api
from opentera.services.ServiceAccessManager import ServiceAccessManager, current_user_client, \
    current_participant_client, current_device_client
from services.LoggingService.libloggingservice.db.models.LoginEntry import LoginEntry
import services.LoggingService.Globals as Globals

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
        # Request access from server params will depend on a user, participant or device
        params = {
            'from_user_uuid': current_user_client.user_uuid if current_user_client else None,
            'from_participant_uuid': current_participant_client.participant_uuid if current_participant_client else None,
            'from_device_uuid': current_device_client.device_uuid if current_device_client else None,
            'with_users_uuids': True,
            'with_projects_ids': True,
            'with_participants_uuids': True,
            'with_devices_uuids': True,
            'with_sites_ids': True,
            'admin': False
        }

        response = Globals.service.get_from_opentera('/api/service/access', params)
        if response.status_code == 200:
            # Response should include ourselves (user, participant or device)
            users_uuids = response.json['users_uuids']
            participants_uuids = response.json['participants_uuids']
            devices_uuids = response.json['devices_uuids']
            projects_ids = response.json['projects_ids']
            sites_ids = response.json['sites_ids']

            try:
                all_entries = []
                results = []
                all_entries.extend(LoginEntry.query.filter(
                    LoginEntry.login_user_uuid.in_(users_uuids) |
                    LoginEntry.login_participant_uuid.in_(participants_uuids) |
                    LoginEntry.login_device_uuid.in_(devices_uuids)).all())

                # Return json result
                for entry in all_entries:
                    results.append(entry.to_json(minimal=False))
                return results

            except InvalidRequestError:
                return '', 500

        else:
            return 'Unauthorized', 403
