from flask import request
from flask_restx import Resource, reqparse, inputs

from modules.LoginModule.LoginModule import participant_multi_auth, current_participant
from modules.FlaskModule.FlaskModule import user_api_ns as api
from modules.DatabaseModule.DBManager import DBManager

from opentera.db.models.TeraServiceConfig import TeraServiceConfig

from flask_babel import gettext
from sqlalchemy import exc

import jsonschema

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_service', type=int, help='ID of service to get all configs from. Use in combination with '
                                                     'another ID field to filter.')
get_parser.add_argument('service_key', type=str, help='Service key to query. Can be used instead of id_service. If used'
                                                      'with id_service, service_key will be ignored.')
get_parser.add_argument('id_specific', type=str, help='ID of the specific configuration to get.')
get_parser.add_argument('list', type=inputs.boolean, help='Also includes a list of all available specifics configs.')

post_parser = api.parser()
post_schema = api.schema_model('service_config', {'properties': TeraServiceConfig.get_json_schema(),
                                                  'type': 'object',
                                                  'location': 'json'})

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='Service config ID to delete', required=True)

class ParticipantQueryServiceConfig(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Get service configuration. Requires either service id or key. Returns only the config for the'
                         'current participant.',
             responses={200: 'Success - returns service configuration',
                        400: 'No parameters specified - id_service is at least required',
                        500: 'Database error'})
    @api.expect(get_parser)
    @participant_multi_auth.login_required(role='limited')
    def get(self):
        """
        Get specific service configuration for the current participant
        """
        args = get_parser.parse_args()

        if not args['service_key'] and not args['id_service']:
            return gettext('Please provide either service key or ID'), 400

        if args['service_key'] and not args['id_service']:
            from opentera.db.models.TeraService import TeraService
            service = TeraService.get_service_by_key(args['service_key'])
            if not service:
                return gettext('Not found'), 400
            args['id_service'] = service.id_service

        participant_access = DBManager.participantAccess(current_participant)
        service_config = participant_access.query_service_configs(args['id_service'])

        if not service_config:
            # Return empty service config by default, even if service is invalid
            return {}, 200

        config_json = service_config.to_json(specific_id=args['id_specific'])
        if args['list']:
            config_json['service_config_specifics'] = service_config.get_specific_ids_list()
        return config_json

    @api.doc(description='Create / update service config for the participant. id_service_config must be set to "0" to '
                         'create a new config.',
             responses={200: 'Success',
                        403: 'Logged user can\'t create/update the specified session',
                        400: 'Badly formed JSON or missing fields(service_config, id_service_config, id_service) in the'
                             ' JSON body',
                        500: 'Internal error when saving service config'})
    @api.expect(post_schema)
    @participant_multi_auth.login_required(role='limited')
    def post(self):
        """
        Create / update service configuration for the current participant
        """
        participant_access = DBManager.participantAccess(current_participant)
        # Using request.json instead of parser, since parser messes up the json!
        if 'service_config' not in request.json:
            return gettext('Missing service_config'), 400

        json_config = request.json['service_config']

        # Validate if we have an id
        if 'id_service_config' not in json_config:
            return 'Missing id_service_config', 400

        if 'service_key' in json_config:
            from opentera.db.models.TeraService import TeraService
            json_config['id_service'] = TeraService.get_service_by_key(json_config['service_key']).id_service
            del json_config['service_key']

        if 'id_service' in json_config:
            if json_config['id_service'] not in participant_access.get_accessible_services_ids():
                return gettext('Forbidden'), 403

        # Prevent from changing anything else other than current participant config
        if 'id_user' in json_config:
            del json_config['id_user']

        if 'id_device' in json_config:
            del json_config['id_device']

        json_config['id_participant'] = current_participant.id_participant

        if json_config['id_service_config'] > 0:
            # Already existing
            try:
                if not TeraServiceConfig.update(json_config['id_service_config'], json_config):
                    return gettext('Invalid config format provided'), 400
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             ParticipantQueryServiceConfig.__name__,
                                             'post', 500, 'Database error', e)
                return gettext('Database Error'), 500
            except (ValueError, jsonschema.exceptions.ValidationError) as err:
                return str(err), 400

        else:
            # New
            if 'id_service' not in json_config:
                return gettext('Missing id_service'), 400

            try:
                new_sc = TeraServiceConfig()
                new_sc.from_json(json_config)
                if not TeraServiceConfig.insert(new_sc):
                    return gettext('Invalid config format provided'), 400

                # Update ID for further use
                json_config['id_service_config'] = new_sc.id_service_config
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             ParticipantQueryServiceConfig.__name__,
                                             'post', 500, 'Database error', e)
                return gettext('Database error'), 500
            except (ValueError, jsonschema.exceptions.ValidationError) as err:
                return str(err), 400

            # Update specific config if required
            if 'id_specific' in json_config:
                new_sc.set_config_for_specific_id(specific_id=json_config['id_specific'],
                                                  config=json_config['service_config_config'])

        update_config = TeraServiceConfig.get_service_config_by_id(s_id=json_config['id_service_config'])
        if 'id_specific' in json_config:
            return update_config.to_json(specific_id=json_config['id_specific'])
        else:
            return update_config.to_json()

    @api.doc(description='Delete a specific service configuration',
             responses={200: 'Success',
                        403: 'Logged participant can\'t delete config (not for the participant or no access to service)',
                        500: 'Database error.'})
    @api.expect(delete_parser)
    @participant_multi_auth.login_required(role='limited')
    def delete(self):
        """
        Delete a specific service configuration for an item
        """
        participant_access = DBManager.participantAccess(current_participant)
        args = delete_parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        todel_config = TeraServiceConfig.get_service_config_by_id(id_todel)

        if todel_config.id_service not in participant_access.get_accessible_services_ids():
            return gettext('Forbidden'), 403

        if todel_config.id_participant != current_participant.id_participant:
            return gettext('Forbidden'), 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraServiceConfig.delete(id_todel=id_todel)
        except exc.SQLAlchemyError as e:
            import sys
            print(sys.exc_info())
            self.module.logger.log_error(self.module.module_name,
                                         ParticipantQueryServiceConfig.__name__,
                                         'delete', 500, 'Database error', e)
            return gettext('Database error'), 500

        return '', 200