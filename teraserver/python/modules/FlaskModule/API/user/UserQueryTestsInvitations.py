import sys

from flask import request
from flask_restx import Resource
from flask_babel import gettext

from sqlalchemy import exc
from sqlalchemy import and_

from jsonschema.exceptions import SchemaError, ValidationError

from modules.LoginModule.LoginModule import user_multi_auth, current_user
from modules.FlaskModule.FlaskModule import user_api_ns as api
from modules.DatabaseModule.DBManager import DBManager
from modules.DatabaseModule.DBManagerTeraUserAccess import DBManagerTeraUserAccess
from opentera.db.models.TeraTestInvitation import TeraTestInvitation
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraSession import TeraSession
from opentera.db.models.TeraTestType import TeraTestType
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraProject import TeraProject
from opentera.db.models.TeraService import TeraService


# Parser definition(s)
# GET
get_parser = api.parser()

# By test invation ID or key
get_parser.add_argument('id_test_invitation',
                        type=int, help='Specific ID of test invitation to query information.',
                        default=None)
get_parser.add_argument('test_invitation_key',
                        type=str, help='Specific key of test invitation to query information.',
                        default=None)

# By user, participant or device
get_parser.add_argument('id_user', type=int,
                        help='ID of the user from which to request all test invitations',
                        default=None)
get_parser.add_argument('user_uuid', type=str,
                        help='UUID of the user from which to request all test invitations',
                        default=None)
get_parser.add_argument('id_participant', type=int,
                        help='ID of the participant from which to request all test invitations',
                        default=None)
get_parser.add_argument('participant_uuid', type=str,
                        help='UUID of the participant from which to request all test invitations',
                        default=None)
get_parser.add_argument('id_device', type=int,
                        help='ID of the device from which to request all test invitations',
                        default=None)
get_parser.add_argument('device_uuid', type=str,
                        help='UUID of the device from which to request all test invitations',
                        default=None)

# By session
get_parser.add_argument('id_session', type=int,
                        help='ID of session from which to request all test invitations',
                        default=None)
get_parser.add_argument('session_uuid', type=str,
                        help='UUID of session from which to request all test invitations',
                        default=None)

# By test type
get_parser.add_argument('id_test_type', type=int,
                        help='ID of test type from which to request all test invitations',
                        default=None)
get_parser.add_argument('test_type_uuid', type=str,
                        help='UUID of test type from which to request all test invitations',
                        default=None)

# By project
get_parser.add_argument('id_project', type=int,
                        help='ID of project from which to request all test invitations',
                        default=None)

# Additional parameters
get_parser.add_argument('full', type=bool, help="Include more information in invitations with user, participant, device, test_type and session.",
                        default=False)
get_parser.add_argument('with_urls', type=bool, help="Include URLs in results", default=False)

post_parser = api.parser()


post_parser = api.parser()

# Post schema should require a list of TestInvitations
post_schema = api.schema_model('postSchema',
    {
        'type': 'object',
        'properties': {
            'tests_invitations':
                {'type': 'array',
                'items': TeraTestInvitation.get_json_schema()['test_invitation'],
                'minItems': 1,
                'uniqueItems': True}
        },
        'required': ['tests_invitations'],
        'additionalProperties': False
    })


delete_parser = api.parser()
delete_parser.add_argument('id', type=int, help='Test type ID to delete', required=True)


class UserQueryTestsInvitations(Resource):
    """
    UserQueryTestsInvitations Resource.
    """
    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

        self.server_hostname = self.module.config.server_config['hostname']
        self.server_port = self.module.config.server_config['port']
        if 'X_EXTERNALSERVER' in request.headers:
            self.server_hostname = request.headers['X_EXTERNALSERVER']

        if 'X_EXTERNALPORT' in request.headers:
            self.server_port = request.headers['X_EXTERNALPORT']


    @api.doc(description='Get tests invitations information.',
             responses={200: 'Success - returns list of invitations',
                        400: 'Required parameter is missing',
                        403: 'Logged user doesn\'t have permission to access the requested data'})
    @api.expect(get_parser)
    @user_multi_auth.login_required
    def get(self):
        """
        Get tests invitations information. Witout any parameters, this will return all accessible invitations.
        Otherwise, you can filter by:
        - id_test_invitation
        - test_invitation_key
        - id_user
        - user_uuid
        - id_participant
        - participant_uuid
        - id_device
        - device_uuid
        - id_session
        - session_uuid
        - id_test_type
        - test_type_uuid
        """
        user_access : DBManagerTeraUserAccess = DBManager.userAccess(current_user)
        args = get_parser.parse_args(strict=True)

        # Get all accessible invitations
        accessible_invitations : list[TeraTestInvitation] = user_access.get_accessible_tests_invitations()
        accessible_invitations_ids : list[int] = [invitation.id_test_invitation for invitation in accessible_invitations]

        # Results will be stored here
        invitations : list[dict] = []

        # No arguments means we return all accessible invitations
        if all(args[arg] is None or arg in ['full', 'with_urls'] for arg in args):
            for invitation in accessible_invitations:
                invitations.append(invitation.to_json(minimal=not args['full']))
        else:
            # Go through all args and get the requested information
            if args['id_test_invitation'] is not None:
                for invitation in TeraTestInvitation.query.filter(
                    TeraTestInvitation.id_test_invitation.in_(accessible_invitations_ids)).filter_by(
                    id_test_invitation=args['id_test_invitation']).all():
                    invitations.append(invitation.to_json(minimal=not args['full']))
            if args['test_invitation_key'] is not None:
                for invitation in TeraTestInvitation.query.filter(
                    TeraTestInvitation.id_test_invitation.in_(accessible_invitations_ids)).filter_by(
                    test_invitation_key=args['test_invitation_key']).all():
                    invitations.append(invitation.to_json(minimal=not args['full']))
            if args['user_uuid'] is not None:
                user : TeraUser = TeraUser.get_user_by_uuid(args['user_uuid'])
                if user:
                    args['id_user'] = user.id_user
            if args['id_user'] is not None:
                for invitation in TeraTestInvitation.query.filter(and_(
                        TeraTestInvitation.id_test_invitation.in_(accessible_invitations_ids),
                        TeraTestInvitation.id_user == args['id_user'])).all():
                    invitations.append(invitation.to_json(minimal=not args['full']))
            if args['participant_uuid'] is not None:
                participant : TeraParticipant = TeraParticipant.get_participant_by_uuid(args['participant_uuid'])
                if participant:
                    args['id_participant'] = participant.id_participant
            if args['id_participant'] is not None:
                for invitation in TeraTestInvitation.query.filter(and_(
                        TeraTestInvitation.id_test_invitation.in_(accessible_invitations_ids),
                        TeraTestInvitation.id_participant == args['id_participant'])).all():
                    invitations.append(invitation.to_json(minimal=not args['full']))
            if args['device_uuid'] is not None:
                device : TeraDevice = TeraDevice.get_device_by_uuid(args['device_uuid'])
                if device:
                    args['id_device'] = device.id_device
            if args['id_device'] is not None:
                for invitation in TeraTestInvitation.query.filter(and_(
                        TeraTestInvitation.id_test_invitation.in_(accessible_invitations_ids),
                        TeraTestInvitation.id_device == args['id_device'])).all():
                    invitations.append(invitation.to_json(minimal=not args['full']))
            if args['session_uuid'] is not None:
                session : TeraSession = TeraSession.get_session_by_uuid(args['session_uuid'])
                if session:
                    args['id_session'] = session.id_session
            if args['id_session'] is not None:
                for invitation in TeraTestInvitation.query.filter(and_(
                        TeraTestInvitation.id_test_invitation.in_(accessible_invitations_ids),
                        TeraTestInvitation.id_session == args['id_session'])).all():
                    invitations.append(invitation.to_json(minimal=not args['full']))
            if args['test_type_uuid'] is not None:
                test_type : TeraTestType = TeraTestType.get_test_type_by_uuid(args['test_type_uuid'])
                if test_type:
                    args['id_test_type'] = test_type.id_test_type
            if args['id_test_type'] is not None:
                for invitation in TeraTestInvitation.query.filter(and_(
                        TeraTestInvitation.id_test_invitation.in_(accessible_invitations_ids),
                        TeraTestInvitation.id_test_type == args['id_test_type'])).all():
                    invitations.append(invitation.to_json(minimal=not args['full']))
            if args['id_project'] is not None:
                for invitation in TeraTestInvitation.query.filter(and_(
                        TeraTestInvitation.id_test_invitation.in_(accessible_invitations_ids),
                        TeraTestInvitation.id_project == args['id_project'])).all():
                    invitations.append(invitation.to_json(minimal=not args['full']))
                # project : TeraProject = TeraProject.get_project_by_id(args['id_project'])
                # if project and project.id_project in user_access.get_accessible_projects_ids():
                #     for invitation in  TeraTestInvitation.query.join(TeraParticipant,
                #             TeraParticipant.id_participant == TeraTestInvitation.id_participant).filter(
                #         TeraTestInvitation.id_test_invitation.in_(accessible_invitations_ids),
                #         TeraParticipant.id_project == project.id_project).all():

                        # invitations.append(invitation.to_json(minimal=not args['full']))

        if args['with_urls']:
            invitations = self._insert_urls_to_invitations(invitations)

        return invitations

    @api.doc(description='Update/Create test invitation.',
             responses={501: 'Unable to update test from here - use service!'})
    @api.expect(post_schema)
    @user_multi_auth.login_required
    def post(self):
        """
        Create / update test invitation
        """
        try:
            # args = post_parser.parse_args(strict=True)

            # Validate JSON schema, will raise BadRequest if not valid
            post_schema.validate(request.json)
            user_access : DBManagerTeraUserAccess = DBManager.userAccess(current_user)

            all_invitations = request.json['tests_invitations']

            response_data = []

            # Go through all invitations and verify access and validity
            for invitation in all_invitations:
                if invitation['id_test_invitation'] == 0:
                    # New invitation
                    if 'id_user' in invitation and invitation['id_user'] not in user_access.get_accessible_users_ids():
                        return gettext('Forbidden'), 403
                    if 'id_participant' in invitation and invitation['id_participant'] not in user_access.get_accessible_participants_ids():
                        return gettext('Forbidden'), 403
                    if 'id_device' in invitation and invitation['id_device'] not in user_access.get_accessible_devices_ids():
                        return gettext('Forbidden'), 403
                    if 'id_project' in invitation and invitation['id_project'] not in user_access.get_accessible_projects_ids():
                        return gettext('Forbidden'), 403
                    if 'id_session' in invitation and invitation['id_session'] not in user_access.get_accessible_sessions_ids():
                        return gettext('Forbidden'), 403
                    if 'id_test_type' in invitation and invitation['id_test_type'] not in user_access.get_accessible_tests_types_ids():
                        return gettext('Forbidden'), 403
                    if 'id_test_type' not in invitation:
                        return gettext('Missing id_test_type'), 400
                    if 'id_project' not in invitation:
                        return gettext('Missing id_project'), 400
                    if 'test_invitation_expiration_date' not in invitation:
                        return gettext('Missing test_invitation_expiration_date'), 400
                    if 'test_invitation_key' in invitation:
                        return gettext('Do not set test_invitation_key'), 400

                    # Verify that we have only one of user, participant or device
                    if len([key for key in invitation.keys() if key in ['id_user', 'id_participant', 'id_device']]) != 1:
                        return gettext('You must specify one of id_user, id_participant or id_device'), 400
                else:
                    if invitation['id_test_invitation'] not in user_access.get_accessible_tests_invitations_ids():
                        return gettext('Forbidden'), 403

                    # Only allow update of count, max_count and expiration
                    if 'test_invitation_count' in invitation or 'test_invitation_max_count' in invitation or 'test_invitation_expiration_date' in invitation:
                        continue
                    else:
                        return gettext('You can only update test_invitation_count'), 400

            # Let's  do the insert/update
            for invitation in all_invitations:
                try:
                    if invitation['id_test_invitation'] == 0:
                        # create new invitation
                        new_invitation = TeraTestInvitation()
                        new_invitation.from_json(invitation)
                        TeraTestInvitation.insert(new_invitation)
                        response_data.append(new_invitation.to_json(minimal=False))
                    else:
                        # Update existing invitation (only count)
                        existing_invitation : TeraTestInvitation = TeraTestInvitation.get_test_invitation_by_id(test_invitation_id=invitation['id_test_invitation'])
                        if existing_invitation:
                            update_values = {}
                            if 'test_invitation_count' in invitation:
                                update_values['test_invitation_count'] = invitation['test_invitation_count']
                            if 'test_invitation_max_count' in invitation:
                                update_values['test_invitation_max_count'] = invitation['test_invitation_max_count']
                            if 'test_invitation_expiration_date' in invitation:
                                update_values['test_invitation_expiration_date'] = invitation['test_invitation_expiration_date']

                            TeraTestInvitation.update(existing_invitation.id_test_invitation, update_values)
                            response_data.append(existing_invitation.to_json(minimal=False))

                except KeyError:
                    return gettext('Required parameter is missing'), 400

                except exc.SQLAlchemyError as e:
                    self.module.logger.log_error(self.module.module_name,
                                            UserQueryTestsInvitations.__name__,
                                            'post', 500, 'Database error', str(e))
                    continue

        except ValidationError as e:
            return gettext('Invalid JSON structure') + str(e), 400
        except SchemaError as e:
            return gettext('Invalid JSON schema') + str(e), 400

        return self._insert_urls_to_invitations(response_data), 200

    @api.doc(description='Delete a specific test invitation',
             responses={200: 'Success',
                        403: 'Logged user can\'t delete test',
                        500: 'Database error.'},
             params={'token': 'Secret token'})
    @api.expect(delete_parser)
    @user_multi_auth.login_required
    def delete(self):
        """
        Delete test invitation
        """
        user_access : DBManagerTeraUserAccess = DBManager.userAccess(current_user)
        args = delete_parser.parse_args(strict=True)
        id_todel = args['id']

        # Check if current user can delete
        if id_todel not in user_access.get_accessible_tests_invitations_ids():
            return gettext('Forbidden'), 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraTestInvitation.delete(id_todel=id_todel)
        except exc.SQLAlchemyError as e:
            print(sys.exc_info())
            self.module.logger.log_error(self.module.module_name,
                                         UserQueryTestsInvitations.__name__,
                                         'delete', 500, 'Database error', e)
            return gettext('Database error'), 500

        return '', 200

    def _insert_urls_to_invitations(self, invitations : list[dict]) -> list[dict]:
        """
        Add URLs to invitations
        """
        for invitation in invitations:
            test_type : TeraTestType  = TeraTestType.get_test_type_by_id(invitation['id_test_type'])

            urls = test_type.get_service_urls(self.server_hostname, self.server_port)

            if test_type and urls['test_type_web_url'] is not None:
                service : TeraService = TeraService.get_service_by_id(test_type.id_service)
                if service:
                    invitation['test_invitation_url'] = f"{urls['test_type_web_url']}?invitation_key={invitation['test_invitation_key']}"
                else:
                    invitation['test_invitation_url'] = None

        return invitations
