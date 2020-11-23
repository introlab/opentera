from flask import jsonify, session, request
from flask_restx import Resource, reqparse, inputs
from modules.FlaskModule.FlaskModule import user_api_ns as api
from modules.LoginModule.LoginModule import user_multi_auth
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraParticipant import TeraParticipant
from libtera.db.models.TeraSession import TeraSession
from modules.DatabaseModule.DBManager import DBManager
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc
from flask_babel import gettext
from libtera.redis.RedisRPCClient import RedisRPCClient
from modules.BaseModule import ModuleNames

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_participant', type=int, help='ID of the participant to query')
get_parser.add_argument('id', type=int, help='Alias for "id_participant"')
get_parser.add_argument('username', type=str, help='Username of the participant to query')
get_parser.add_argument('participant_uuid', type=str, help='Participant uuid of the participant to query')
get_parser.add_argument('uuid', type=str, help='Alias for "participant_uuid"')
get_parser.add_argument('id_site', type=int, help='ID of the site from which to get all participants')
get_parser.add_argument('id_project', type=int, help='ID of the project from which to get all participants')
get_parser.add_argument('id_group', type=int, help='ID of the participant groups from which to get all participants')
get_parser.add_argument('id_session', type=int, help='ID of the session from which to get all participants')
get_parser.add_argument('id_device', type=int, help='ID of the device from which to get all participants associated')
get_parser.add_argument('name', type=str, help='Name of the participant to query')
get_parser.add_argument('enabled', type=inputs.boolean, help='Flag that limits the returned data to the enabled '
                                                             'participants')
get_parser.add_argument('list', type=inputs.boolean, help='Flag that limits the returned data to minimal information')
get_parser.add_argument('full', type=inputs.boolean, help='Flag that expands the returned data to include all '
                                                          'information')
get_parser.add_argument('no_group', type=inputs.boolean,
                        help='Flag that limits the returned data with only participants without a group')
# get_parser.add_argument('with_status', type=inputs.boolean, help='Include status information - offline, online, busy '
#                                                                  'for each participant')

# post_parser = reqparse.RequestParser()
post_schema = api.schema_model('user_participant', {'properties': TeraParticipant.get_json_schema(),
                                                    'type': 'object',
                                                    'location': 'json'})

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='Participant ID to delete', required=True)


class UserQueryParticipants(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @user_multi_auth.login_required
    @api.expect(get_parser)
    @api.doc(description='Get participants information. Only one of the ID parameter is supported and required at once',
             responses={200: 'Success - returns list of participants',
                        400: 'No parameters specified at least one id must be used',
                        500: 'Database error'})
    def get(self):
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        parser = get_parser

        args = parser.parse_args()

        participants = []
        if args['id']:
            args['id_participant'] = args['id']
        if args['uuid']:
            args['participant_uuid'] = args['uuid']

        # If we have no arguments, return nothing
        if not any(args.values()):
            return gettext('Missing arguments'), 400
        elif args['id_participant']:
            if args['id_participant'] in user_access.get_accessible_participants_ids():
                participants = [TeraParticipant.get_participant_by_id(args['id_participant'])]
        elif args['username'] is not None:
            participants = [TeraParticipant.get_participant_by_username(args['username'])]
        elif args['participant_uuid'] is not None:
            participant = TeraParticipant.get_participant_by_uuid(args['participant_uuid'])
            if participant:
                if participant.id_participant in user_access.get_accessible_participants_ids():
                    participants = [participant]
        elif args['id_site']:
            if args['enabled'] is not None:
                participants = user_access.query_enabled_participants_for_site(args['id_site'])
            else:
                participants = user_access.query_all_participants_for_site(args['id_site'])
        elif args['id_project']:
            if args['enabled'] is not None:
                participants = user_access.query_enabled_participants_for_project(args['id_project'])
            else:
                participants = user_access.query_all_participants_for_project(args['id_project'])
        elif args['id_group']:
            participants = user_access.query_participants_for_group(args['id_group'])
        elif args['id_device']:
            participants = user_access.query_participants_for_device(args['id_device'])
        elif args['id_session']:
            part_session = TeraSession.get_session_by_id(args['id_session'])
            participants = []
            accessibles_parts = user_access.get_accessible_participants_ids()
            for part in part_session.session_participants:
                if part.id_participant in accessibles_parts:
                    participants.append(part)
        elif args['name']:
            participants = [TeraParticipant.get_participant_by_name(args['name'])]
            for participant in participants:
                if not participant and len(participants) == 1:
                    participants = []
                    break
                if participant.id_participant not in user_access.get_accessible_participants_ids():
                    participants = []
        try:
            if participants:
                participant_list = []
                status_participants = {}

                # Query status
                rpc = RedisRPCClient(self.module.config.redis_config)
                status_participants = rpc.call(ModuleNames.USER_MANAGER_MODULE_NAME.value, 'status_participants')

                for participant in participants:
                    if args['enabled'] is not None:
                        if participant.participant_enabled != args['enabled']:
                            continue

                    if participant is not None:
                        # No group flag
                        if args['no_group'] is not None:
                            if participant.id_participant_group is not None:
                                continue
                        # List
                        participant_json = participant.to_json(minimal=args['list'])
                        if args['list'] is None:

                            if args['id_participant']:
                                # Adds project information to participant
                                # participant_json['id_project'] = participant.participant_project.id_project
                                # Adds site information do participant
                                participant_json['id_site'] = participant.participant_project.id_site
                            if args['id_group'] or args['id_participant']:
                                # Adds last session information to participant
                                participant_sessions = TeraSession.get_sessions_for_participant(
                                    part_id=participant.id_participant)
                                if participant_sessions:
                                    participant_json['participant_lastsession'] = \
                                        participant_sessions[-1].session_start_datetime.isoformat()
                                else:
                                    participant_json['participant_lastsession'] = None

                            if args['full'] is not None:
                                if participant.id_participant_group is not None:
                                    participant_json[
                                        'participant_participant_group'] = participant.participant_participant_group.to_json()
                                devices = []
                                for device in participant.participant_devices:
                                    devices.append(device.to_json())
                                participant_json['participant_devices'] = devices
                                participant_json['participant_project'] = participant.participant_project.to_json()

                        # Update participants status
                        if participant.participant_uuid in status_participants:
                            participant_json['participant_busy'] = \
                                status_participants[participant.participant_uuid]['busy']
                            participant_json['participant_online'] = \
                                status_participants[participant.participant_uuid]['online']
                        else:
                            participant_json['participant_busy'] = False
                            participant_json['participant_online'] = False

                        participant_list.append(participant_json)

                return jsonify(participant_list)

        except InvalidRequestError as e:
            self.module.logger.log_error(self.module.module_name,
                                         UserQueryParticipants.__name__,
                                         'get', 500, 'Database error', str(e))
            return '', 500

    @user_multi_auth.login_required
    @api.expect(post_schema)
    @api.doc(description='Create / update participants. id_participant must be set to "0" to create a new '
                         'participant. A participant can be created/modified if the user has admin rights to the '
                         'project.',
             responses={200: 'Success',
                        403: 'Logged user can\'t create/update the specified participant',
                        400: 'Badly formed JSON or missing fields(id_participant or id_project/id_group [only one of '
                             'them]) in the JSON body, or mismatch between id_project and participant group project',
                        500: 'Internal error when saving device'})
    def post(self):
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)
        # Using request.json instead of parser, since parser messes up the json!
        if 'participant' not in request.json:
            return gettext('Missing participant'), 400

        json_participant = request.json['participant']

        # Validate if we have an id
        if 'id_participant' not in json_participant or ('id_project' not in json_participant
                                                        and 'id_participant_group' not in json_participant):
            return gettext('Missing id_participant, id_project or id_participant_group'), 400

        # User can modify or add a participant if it has admin to that project
        if 'id_project' in json_participant:
            if json_participant['id_project'] > 0 and \
                    json_participant['id_project'] not in user_access.get_accessible_projects_ids(admin_only=False):
                return gettext('No admin access to project'), 403

        # Check if current user can modify the posted group
        if 'id_participant_group' in json_participant:
            if json_participant['id_participant_group'] is not None and \
                    json_participant['id_participant_group'] > 0 and \
                    json_participant['id_participant_group'] not in \
                    user_access.get_accessible_groups_ids(admin_only=False):
                return gettext('No admin access to group'), 403

        # If we have both an id_group and an id_project, make sure that the id_project in the group matches
        if 'id_project' in json_participant and 'id_participant_group' in json_participant:
            if json_participant['id_participant_group'] is not None and json_participant['id_participant_group'] > 0:
                from libtera.db.models.TeraParticipantGroup import TeraParticipantGroup
                participant_group = TeraParticipantGroup.get_participant_group_by_id(
                    json_participant['id_participant_group'])
                if participant_group is None:
                    return gettext('Participant group not found.'), 400
                if participant_group.id_project != json_participant['id_project'] \
                        and json_participant['id_project'] > 0:
                    return gettext('Mismatch between id_project and group\'s project'), 400
                # Force id_project to group project.
                json_participant['id_project'] = participant_group.id_project

        # If participant group = 0, set it to none
        if 'id_participant_group' in json_participant:
            if json_participant['id_participant_group'] == 0:
                json_participant['id_participant_group'] = None

        # Do the update!
        if json_participant['id_participant'] > 0:
            # Already existing
            try:
                TeraParticipant.update(json_participant['id_participant'], json_participant)
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             UserQueryParticipants.__name__,
                                             'post', 500, 'Database error', str(e))
                return e.args, 500
            except NameError as e:
                self.module.logger.log_error(self.module.module_name,
                                             UserQueryParticipants.__name__,
                                             'post', 500, 'Database error', str(e))
                return e.args, 500
        else:
            # New
            try:
                new_part = TeraParticipant()
                new_part.from_json(json_participant)
                TeraParticipant.insert(new_part)
                # Update ID for further use
                json_participant['id_participant'] = new_part.id_participant
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             UserQueryParticipants.__name__,
                                             'post', 500, 'Database error', str(e))
                return e.args, 500
            except NameError as e:
                self.module.logger.log_error(self.module.module_name,
                                             UserQueryParticipants.__name__,
                                             'post', 500, 'Database error', str(e))
                return e.args, 500

        update_participant = TeraParticipant.get_participant_by_id(json_participant['id_participant'])
        update_participant_json = update_participant.to_json()

        # Query status
        rpc = RedisRPCClient(self.module.config.redis_config)
        status_participants = rpc.call(ModuleNames.USER_MANAGER_MODULE_NAME.value, 'status_participants')
        if update_participant.participant_uuid in status_participants:
            update_participant_json['participant_busy'] = \
                status_participants[update_participant.participant_uuid]['busy']
            update_participant_json['participant_online'] = \
                status_participants[update_participant.participant_uuid]['online']
        else:
            update_participant_json['participant_busy'] = False
            update_participant_json['participant_online'] = False

        return jsonify([update_participant_json])

    @user_multi_auth.login_required
    @api.expect(delete_parser)
    @api.doc(description='Delete a specific participant',
             responses={200: 'Success',
                        403: 'Logged user can\'t delete participant (only project admin can delete)',
                        500: 'Database error.'})
    def delete(self):
        parser = delete_parser

        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        args = parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        # Only project admins can delete a participant
        part = TeraParticipant.get_participant_by_id(id_todel)

        if user_access.get_project_role(part.participant_project.id_project) != 'admin':
            return gettext('Forbidden'), 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraParticipant.delete(id_todel=id_todel)
        except exc.IntegrityError as e:
            # Causes that could make an integrity error when deleting a participant:
            # - Associated sessions
            # - Sessions from which the participant is the creator
            # - Assets by that participant
            # In all case, deleting associated sessions will clear that all, since a participant cannot create sessions
            # or assets not for itself.
            self.module.logger.log_error(self.module.module_name,
                                         UserQueryParticipants.__name__,
                                         'delete', 500, 'Database error', str(e))
            return gettext('Can\'t delete participant: please delete all sessions before deleting.'), 500
        except exc.SQLAlchemyError as e:
            import sys
            print(sys.exc_info())
            self.module.logger.log_error(self.module.module_name,
                                         UserQueryParticipants.__name__,
                                         'delete', 500, 'Database error', str(e))
            return gettext('Database Error'), 500

        return '', 200
