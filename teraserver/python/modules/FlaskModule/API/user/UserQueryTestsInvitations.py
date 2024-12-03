import sys

from flask_restx import Resource
from flask_babel import gettext

from sqlalchemy import exc
from sqlalchemy import and_
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


post_parser = api.parser()

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

    @api.doc(description='Get tests invitations information.',
             responses={200: 'Success - returns list of invitations',
                        400: 'Required parameter is missing',
                        403: 'Logged user doesn\'t have permission to access the requested data'})
    @api.expect(get_parser)
    @user_multi_auth.login_required
    def get(self):
        """
        Get tests invitations information
        """
        user_access : DBManagerTeraUserAccess = DBManager.userAccess(current_user)
        args = get_parser.parse_args(strict=True)

        # At least one argument required
        if not any(args.values()):
            return gettext('No arguments specified'), 400

        invitations : list[dict] = []
        accessible_ids : list[int] = user_access.get_accessible_tests_invitations_ids()

        # Go through all args and get the requested information
        if args['id_test_invitation']:
            for invitation in TeraTestInvitation.query.filter(
                TeraTestInvitation.id_test_invitation.in_(accessible_ids)).filter_by(
                id_test_invitation=args['id_test_invitation']).all():
                invitations.append(invitation.to_json())
        if args['test_invitation_key']:
            for invitation in TeraTestInvitation.query.filter(
                TeraTestInvitation.id_test_invitation.in_(accessible_ids)).filter_by(
                test_invitation_key=args['test_invitation_key']).all():
                invitations.append(invitation.to_json())
        if args['user_uuid']:
            user : TeraUser = TeraUser.get_user_by_uuid(args['user_uuid'])
            if user:
                args['id_user'] = user.id_user
        if args['id_user']:
            for invitation in TeraTestInvitation.query.filter(and_(
                    TeraTestInvitation.id_test_invitation.in_(accessible_ids),
                    TeraTestInvitation.id_user == args['id_user'])).all():
                invitations.append(invitation.to_json())
        if args['participant_uuid']:
            participant : TeraParticipant = TeraParticipant.get_participant_by_uuid(args['participant_uuid'])
            if participant:
                args['id_participant'] = participant.id_participant
        if args['id_participant']:
            for invitation in TeraTestInvitation.query.filter(and_(
                    TeraTestInvitation.id_test_invitation.in_(accessible_ids),
                    TeraTestInvitation.id_participant == args['id_participant'])).all():
                invitations.append(invitation.to_json())
        if args['device_uuid']:
            device : TeraDevice = TeraDevice.get_device_by_uuid(args['device_uuid'])
            if device:
                args['id_device'] = device.id_device
        if args['id_device']:
            for invitation in TeraTestInvitation.query.filter(and_(
                    TeraTestInvitation.id_test_invitation.in_(accessible_ids),
                    TeraTestInvitation.id_device == args['id_device'])).all():
                invitations.append(invitation.to_json())
        if args['session_uuid']:
            session : TeraSession = TeraSession.get_session_by_uuid(args['session_uuid'])
            if session:
                args['id_session'] = session.id_session
        if args['id_session']:
            for invitation in TeraTestInvitation.query.filter(and_(
                    TeraTestInvitation.id_test_invitation.in_(accessible_ids),
                    TeraTestInvitation.id_session == args['id_session'])).all():
                invitations.append(invitation.to_json())
        if args['test_type_uuid']:
            test_type : TeraTestType = TeraTestType.get_test_type_by_uuid(args['test_type_uuid'])
            if test_type:
                args['id_test_type'] = test_type.id_test_type
        if args['id_test_type']:
            for invitation in TeraTestInvitation.query.filter(and_(
                    TeraTestInvitation.id_test_invitation.in_(accessible_ids),
                    TeraTestInvitation.id_test_type == args['id_test_type'])).all():
                invitations.append(invitation.to_json())

        return invitations

    @api.doc(description='Update/Create test invitation.',
             responses={501: 'Unable to update test from here - use service!'})
    @api.expect(post_parser)
    @user_multi_auth.login_required
    def post(self):
        """
        Create / update test invitation
        """
        return gettext('Test information update and creation must be done directly into a service (such as '
                       'Test service)'), 501

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
