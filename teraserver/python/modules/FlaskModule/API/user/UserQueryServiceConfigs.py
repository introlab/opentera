from flask import jsonify, session, request
from flask_restx import Resource, reqparse, inputs
from modules.LoginModule.LoginModule import user_multi_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraServiceConfig import TeraServiceConfig
from modules.DatabaseModule.DBManager import DBManager
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc
from flask_babel import gettext

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_service', type=int, help='ID of service to get all configs from. Use in combination with '
                                                     'another ID field to filter.')
get_parser.add_argument('id_participant', type=int, help='ID of the participant from which to get the service specified'
                                                         ' with id_service or all configs')
get_parser.add_argument('id_user', type=int, help='ID of the user from which to get the service specified with '
                                                  'id_service or all configs')
get_parser.add_argument('id_device', type=int, help='ID of the device from which to get the service specified with '
                                                    'id_service or all configs')

# post_parser = reqparse.RequestParser()
# post_parser.add_argument('session', type=str, location='json', help='Session to create / update', required=True)
post_schema = api.schema_model('service_config', {'properties': TeraServiceConfig.get_json_schema(),
                                                  'type': 'object',
                                                  'location': 'json'})

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='Service config ID to delete', required=True)


class UserQueryServiceConfig(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @user_multi_auth.login_required
    @api.expect(get_parser)
    @api.doc(description='Get service configuration. id_service can be combined with id_user, id_participant or '
                         'id_device, if required.',
             responses={200: 'Success - returns list of configurations',
                        400: 'No parameters specified - id_service is at least required',
                        500: 'Database error'})
    def get(self):
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        parser = get_parser

        args = parser.parse_args()
        id_service = args['id_service']
        id_user = args['id_user']
        id_device = args['id_device']
        id_participant = args['id_participant']

        if (id_participant and (id_device or id_user)) or (id_user and id_device):
            return 'Can\'t combine id_user, id_participant and id_device in request', 400

        if not id_user and not id_device and not id_service and not id_participant:
            return 'Must specify at least one id parameter', 400

        # Do the query itself!
        configs = user_access.query_service_configs(service_id=id_service, user_id=id_user, device_id=id_device,
                                                    participant_id=id_participant)

        if not configs:
            configs = []
        if not isinstance(configs, list):
            configs = [configs]

        try:
            configs_list = []
            for config in configs:
                config_json = config.to_json()
                configs_list.append(config_json)

            return configs_list

        except InvalidRequestError:
            return '', 500

    @user_multi_auth.login_required
    @api.doc(description='Create / update service config. id_service_config must be set to "0" to create a new '
                         'config. A config can be created/modified if the user has admin access to the user, device or '
                         'participant',
             responses={200: 'Success',
                        403: 'Logged user can\'t create/update the specified session',
                        400: 'Badly formed JSON or missing fields(service_config, id_service_config, id_service) in the'
                             ' JSON body',
                        500: 'Internal error when saving service config'})
    @api.expect(post_schema)
    def post(self):
        # parser = post_parser

        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)
        # Using request.json instead of parser, since parser messes up the json!
        if 'service_config' not in request.json:
            return 'Missing service_config', 400

        json_config = request.json['service_config']

        # Validate if we have an id
        if 'id_service_config' not in json_config:
            return 'Missing id_service_config', 400

        if ('id_participant' in json_config and ('id_device' in json_config or 'id_user' in json_config)) \
                or ('id_user' in json_config and 'id_device' in json_config):
            return 'Can\'t combine id_user, id_participant and id_device in request', 400

        # Validate if we can modify
        if 'id_service' in json_config:
            if json_config['id_service'] not in user_access.get_accessible_services_ids(include_system_services=True):
                return 'Forbidden', 403

        if 'id_device' in json_config:
            if json_config['id_device'] not in user_access.get_accessible_devices_ids(admin_only=True):
                return 'Forbidden', 403

        if 'id_participant' in json_config:
            if json_config['id_participant'] not in user_access.get_accessible_participants_ids(admin_only=True):
                return 'Forbidden', 403

        if 'id_user' in json_config:
            # Can always modify "self" config
            if json_config['id_user'] != session['_user_id'] and \
                    json_config['id_user'] not in user_access.get_accessible_users_ids(admin_only=True):
                return 'Forbidden', 403

        import jsonschema
        # Do the update!
        if json_config['id_service_config'] > 0:
            # Already existing
            try:
                if not TeraServiceConfig.update(json_config['id_service_config'], json_config):
                    return 'Invalid config format provided', 400
            except exc.SQLAlchemyError:
                import sys
                print(sys.exc_info())
                return '', 500
            except (ValueError, jsonschema.exceptions.ValidationError) as err:
                return str(err), 400

        else:
            # New
            if 'id_service' not in json_config:
                return 'Missing id_service', 400

            if 'id_participant' not in json_config and 'id_user' not in json_config and 'id_device' not in json_config:
                return 'Missing at least one id field', 400

            try:
                new_sc = TeraServiceConfig()
                new_sc.from_json(json_config)
                if not TeraServiceConfig.insert(new_sc):
                    return 'Invalid config format provided', 400

                # Update ID for further use
                json_config['id_service_config'] = new_sc.id_service_config
            except exc.SQLAlchemyError:
                import sys
                print(sys.exc_info())
                return '', 500
            except (ValueError, jsonschema.exceptions.ValidationError) as err:
                return str(err), 400

        update_config = TeraServiceConfig.get_service_config_by_id(s_id=json_config['id_service_config'])
        return [update_config.to_json()]

    @user_multi_auth.login_required
    @api.expect(delete_parser)
    @api.doc(description='Delete a specific session',
             responses={200: 'Success',
                        403: 'Logged user can\'t delete config (must have admin access to the related object - user,'
                             'device or participant, or be its own config)',
                        500: 'Database error.'})
    def delete(self):
        parser = delete_parser

        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        args = parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        todel_config = TeraServiceConfig.get_service_config_by_id(id_todel)

        if todel_config.id_service not in user_access.get_accessible_services_ids(include_system_services=True):
            return 'Forbidden', 403

        if todel_config.id_user:
            if todel_config.id_user != session['_user_id'] and \
                    todel_config.id_user not in user_access.get_accessible_users_ids(admin_only=True):
                return 'Forbidden', 403

        if todel_config.id_participant:
            if todel_config.id_participant not in user_access.get_accessible_participants_ids(admin_only=True):
                return 'Forbidden', 403

        if todel_config.id_device:
            if todel_config.id_device not in user_access.get_accessible_devices_ids(admin_only=True):
                return 'Forbidden', 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraServiceConfig.delete(id_todel=id_todel)
        except exc.SQLAlchemyError:
            import sys
            print(sys.exc_info())
            return 'Database error', 500

        return '', 200