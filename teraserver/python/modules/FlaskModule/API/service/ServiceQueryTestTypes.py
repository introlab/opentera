from flask_restx import Resource
from flask_babel import gettext
from flask import request
from sqlalchemy import exc
from modules.LoginModule.LoginModule import LoginModule, current_service
from modules.FlaskModule.FlaskModule import service_api_ns as api
from modules.DatabaseModule.DBManager import DBManager
from opentera.db.models.TeraTestTypeProject import TeraTestTypeProject
from opentera.db.models.TeraTestTypeSite import TeraTestTypeSite
from opentera.db.models.TeraTestType import TeraTestType
from opentera.db.models.TeraParticipant import TeraParticipant


# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_site', type=int, help='ID of the site to query test types for')
get_parser.add_argument('id_project', type=int, help='ID of the project to query test types for')
get_parser.add_argument('id_participant', type=int, help='ID of the participant to query types for')
get_parser.add_argument('test_type_key', type=str, help='Test type key to query for')
get_parser.add_argument('id_test_type', type=int, help='ID of the test type to query for')

post_parser = api.parser()
post_schema = api.schema_model('service_test_type', {'properties': TeraTestType.get_json_schema(), 'type': 'object',
                                                     'location': 'json'})

delete_parser = api.parser()
delete_parser.add_argument('uuid', type=str, help='Test type UUID to delete', required=True)


class ServiceQueryTestTypes(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Return test types information for the current service',
             responses={200: 'Success',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Service doesn\'t have permission to access the requested data'},
             params={'token': 'Secret token'})
    @api.expect(get_parser)
    @LoginModule.service_token_or_certificate_required
    def get(self):
        args = get_parser.parse_args(strict=True)
        service_access = DBManager.serviceAccess(current_service)

        test_types = []
        if args['id_site']:
            if args['id_site'] in service_access.get_accessibles_sites_ids():
                test_types = [tt.test_type_site_test_type for tt in
                              TeraTestTypeSite.get_tests_types_for_site(args['id_site'])]
        elif args['id_project']:
            if args['id_project'] in service_access.get_accessible_projects_ids():
                test_types = [tt.test_type_project_test_type for tt in
                              TeraTestTypeProject.get_tests_types_for_project(args['id_project'])]
        elif args['id_participant']:
            if args['id_participant'] in service_access.get_accessible_participants_ids():
                part_info = TeraParticipant.get_participant_by_id(args['id_participant'])
                test_types = [tt.test_type_project_test_type for tt in
                              TeraTestTypeProject.get_tests_types_for_project(part_info.id_project)]
        elif args['id_test_type']:
            if args['id_test_type'] in service_access.get_accessible_tests_types_ids():
                test_types = [TeraTestType.get_test_type_by_id(args['id_test_type'])]
        elif args['test_type_key']:
            test_type = TeraTestType.get_test_type_by_key(args['test_type_key'])
            if test_type and test_type.id_test_type in service_access.get_accessible_tests_types_ids():
                test_types = [test_type]
        else:
            test_types = service_access.get_accessible_tests_types()

        return [tt.to_json() for tt in test_types]

    @api.doc(description='Create / update test type. id_test_type must be set to "0" to create a new '
                         'type.',
             responses={200: 'Success',
                        403: 'Service can\'t create/update the specified test type',
                        400: 'Badly formed JSON or missing field in the JSON body',
                        500: 'Internal error when saving test type'},
             params={'token': 'Secret token'})
    @api.expect(post_schema)
    @LoginModule.service_token_or_certificate_required
    def post(self):
        # Using request.json instead of parser, since parser messes up the json!
        if 'test_type' not in request.json:
            return gettext('Missing test_type'), 400

        json_test_type = request.json['test_type']

        # Validate if we have an id
        if 'id_test_type' not in json_test_type:
            return gettext('Missing id_test_type'), 400

        if 'id_service' in json_test_type and json_test_type['id_service'] != current_service.id_service:
            return gettext('Forbidden'), 403

        if json_test_type['id_test_type'] != 0:
            test_type = TeraTestType.get_test_type_by_id(json_test_type['id_test_type'])
            if not test_type or test_type.id_service != current_service.id_service:
                return gettext('Forbidden'), 403
            # Updating
            try:
                TeraTestType.update(json_test_type['id_test_type'], json_test_type)
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             ServiceQueryTestTypes.__name__,
                                             'post', 500, 'Database error', str(e))
                return gettext('Database error'), 500
        else:
            # New
            # Always force id to this service
            json_test_type['id_service'] = current_service.id_service
            try:
                missing_fields = TeraTestType.validate_required_fields(json_data=json_test_type)
                if missing_fields:
                    return gettext('Missing fields') + ': ' + str([field for field in missing_fields]), 400

                new_tt = TeraTestType()
                new_tt.from_json(json_test_type)
                TeraTestType.insert(new_tt)
                # Update ID for further use
                json_test_type['id_test_type'] = new_tt.id_test_type
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             ServiceQueryTestTypes.__name__,
                                             'post', 500, 'Database error', str(e))
                return gettext('Database error'), 500
        update_test_type = TeraTestType.get_test_type_by_id(json_test_type['id_test_type'])
        if update_test_type:
            json_test_type = update_test_type.to_json()
        return json_test_type

    @api.doc(description='Delete a specific test type',
             responses={200: 'Success',
                        403: 'Service can\'t delete test type',
                        500: 'Database error.'},
             params={'token': 'Secret token'})
    @api.expect(delete_parser)
    @LoginModule.service_token_or_certificate_required
    def delete(self):
        args = delete_parser.parse_args()
        uuid_todel = args['uuid']

        test_type = TeraTestType.get_test_type_by_uuid(uuid_todel)

        if not test_type:
            return gettext('Missing arguments'), 400

        if test_type.id_service != current_service.id_service:
            return gettext('Test type not related to this service. Can\'t delete.'), 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraTestType.delete(id_todel=test_type.id_test_type)
        except exc.SQLAlchemyError as e:
            import sys
            print(sys.exc_info())
            self.module.logger.log_error(self.module.module_name,
                                         ServiceQueryTestTypes.__name__,
                                         'delete', 500, 'Database error', str(e))
            return gettext('Database error'), 500

        return '', 200
