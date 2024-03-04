from flask import request
from flask_restx import Resource
from flask_babel import gettext
from sqlalchemy import exc

from modules.DatabaseModule.DBManager import DBManager
from modules.LoginModule.LoginModule import LoginModule, current_service
from modules.FlaskModule.FlaskModule import service_api_ns as api
from opentera.db.models.TeraParticipantGroup import TeraParticipantGroup

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_participant_group', type=int, help='ID to query')
get_parser.add_argument('id_project', type=int, help='ID project to query information')

post_parser = api.parser()

post_schema = api.schema_model('participant_group', {'properties': TeraParticipantGroup.get_json_schema(),
                                                     'type': 'object', 'location': 'json'})

delete_parser = api.parser()
delete_parser.add_argument('id', type=int, help='ID to delete')


class ServiceQueryParticipantGroups(Resource):

    # Handle auth
    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Return participant group information.',
             responses={200: 'Success',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Service doesn\'t have permission to access the requested data'},
             params={'token': 'Secret token'})
    @api.expect(get_parser)
    @LoginModule.service_token_or_certificate_required
    def get(self):
        # Get service access manager, that allows to check for access
        service_access = DBManager.serviceAccess(current_service)

        # Parse arguments
        args = get_parser.parse_args()

        # Check if 'id_participant_group' is specified in args
        if args['id_participant_group']:
            # Check if service has access to the specified participant group
            if args['id_participant_group'] not in service_access.get_accessible_participants_groups_ids():
                return gettext('Forbidden'), 403
            # Retrieve participant group by ID
            participant_group = TeraParticipantGroup.get_participant_group_by_id(args['id_participant_group'])
            # If participant group is found, check if 'id_project' matches
            if participant_group:
                # Check if the 'id_project' and 'id_participant_group' is matching
                if args['id_project'] and args['id_project'] != participant_group.id_project:
                    # Check if user has access to the specified project
                    if args['id_project'] not in service_access.get_accessible_projects_ids():
                        return gettext('Forbidden'), 403
                    return gettext('No group matching the provided id_participant_group and id_project was found'), 404

                # Return the JSON representation of the participant group
                return participant_group.to_json(minimal=True)

        # Check if 'id_project' is specified in args
        if args['id_project']:
            # Check if user has access to the specified project
            if args['id_project'] not in service_access.get_accessible_projects_ids():
                return gettext('Forbidden'), 403
            # Retrieve participant groups by id_project
            participant_groups = TeraParticipantGroup.get_participant_group_for_project(args['id_project'])
            # If at least one participant group is found, convert result to JSON
            if participant_groups:
                # Convert result to JSON
                participant_group_json = [group.to_json(minimal=True) for group in participant_groups]
                return participant_group_json

        # Return error message for missing arguments
        return gettext('Missing arguments'), 400

    @api.doc(description='Update participant group',
             responses={200: 'Success - To be documented',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Logged user doesn\'t have permission to access the requested data'},
             params={'token': 'Secret token'})
    @api.expect(post_schema)
    @LoginModule.service_token_or_certificate_required
    def post(self):
        # Parse arguments
        args = post_parser.parse_args()

        # Get service access manager, that allows to check for access
        service_access = DBManager.serviceAccess(current_service)

        # Check if 'participant_group' is present in the JSON request
        if 'participant_group' not in request.json:
            return gettext('Missing participant_group'), 400

        # Extract participant group information from the JSON request
        participant_group_info = request.json['participant_group']

        # Check if 'id_participant_group' is missing
        if 'id_participant_group' not in participant_group_info:
            return gettext('Missing id_participant_group'), 400

        # Check if creating a new participant group and 'id_project' is missing
        if participant_group_info['id_participant_group'] == 0 and ('id_project' not in participant_group_info
                                                                    or participant_group_info['id_project'] is None):
            return gettext('Missing id_project'), 400

        # Check if creating a new participant group and 'participant_group_name' is missing
        if (participant_group_info['id_participant_group'] == 0 and ('participant_group_name'
                                                                     not in participant_group_info or
                                                                     participant_group_info[
                                                                         'participant_group_name'] is None)):
            return gettext('Missing group name'), 400

        # Check if it's a new participant group or an update
        if participant_group_info['id_participant_group'] == 0:
            verif = service_access.get_accessible_projects_ids()
            # Check if the project ID is valid
            if ('id_project' in participant_group_info and participant_group_info['id_project']
                    not in service_access.get_accessible_projects_ids()):
                return gettext('Forbidden'), 403

            # Create participant group
            participant_group = TeraParticipantGroup()
            participant_group.participant_group_name = participant_group_info['participant_group_name']
            participant_group.id_project = participant_group_info['id_project']

            try:
                TeraParticipantGroup.insert(participant_group)
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             ServiceQueryParticipantGroups.__name__,
                                             'post', 500, 'Database error', str(e))
                return gettext('Database error'), 500
        else:
            # Update existing participant group
            try:
                # Check if updating an existing participant group

                if (participant_group_info['id_participant_group']
                        not in service_access.get_accessible_participants_groups_ids()):
                    return gettext('Forbidden'), 403

                TeraParticipantGroup.update(participant_group_info['id_participant_group'], participant_group_info)
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             ServiceQueryParticipantGroups.__name__,
                                             'post', 500, 'Database error', str(e))
                return gettext('Database error'), 500

            # Retrieve the updated participant group
            participant_group = TeraParticipantGroup.get_participant_group_by_id(participant_group_info
                                                                                 ['id_participant_group'])

        # Return the JSON representation of the participant group
        return participant_group.to_json(minimal=False)

    @api.doc(description='Delete a specific participant group.',
             responses={200: 'Success',
                        403: 'Logged user doesn\'t have permission to access the requested data',
                        500: 'Database error.'},
             params={'token': 'Secret token'})
    @api.expect(delete_parser)
    @LoginModule.service_token_or_certificate_required
    def delete(self):
        # Parse arguments
        args = delete_parser.parse_args()
        id_todel = args['id']

        # Get service access manager, that allows to check for access
        service_access = DBManager.serviceAccess(current_service)

        # Check if the user has access to delete participant groups
        if id_todel not in service_access.get_accessible_participants_groups_ids():
            return gettext('Forbidden'), 403

        # If the participant group with the given ID is not found, return an error
        group_to_del = TeraParticipantGroup.get_participant_group_by_id(id_todel)
        if group_to_del is None:
            return gettext('The id_participant_group given was not found'), 400

        # Check deletion integrity
        deletion_integrity = group_to_del.delete_check_integrity()
        # Check if deletion is possible without violating integrity constraints
        if deletion_integrity is not None:
            return gettext('Deletion impossible: Participant group still has participant(s)'), 500

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraParticipantGroup.delete(id_todel=id_todel)
        except exc.SQLAlchemyError as e:
            import sys
            print(sys.exc_info())
            self.module.logger.log_error(self.module.module_name,
                                         ServiceQueryParticipantGroups.__name__,
                                         'delete', 500, 'Database error', str(e))
            return gettext('Database error'), 500

        return '', 200
