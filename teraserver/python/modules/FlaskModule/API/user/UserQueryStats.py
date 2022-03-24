from flask_restx import Resource, inputs
from modules.LoginModule.LoginModule import user_multi_auth, current_user
from modules.FlaskModule.FlaskModule import user_api_ns as api
from opentera.db.models.TeraParticipant import TeraParticipant
from flask_babel import gettext
from modules.DatabaseModule.DBManager import DBManager, DBManagerTeraUserAccess

import datetime


# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_user_group', type=int, help='ID of the user group to query stats for.')
get_parser.add_argument('id_user', type=int, help='ID of the user to query stats for.')
get_parser.add_argument('id_site', type=int, help='ID of the site to query stats for.')
get_parser.add_argument('id_project', type=int, help='ID of the project to query stats for.')
get_parser.add_argument('id_group', type=int, help='ID of the participant group to query stats for.')
get_parser.add_argument('id_session', type=int, help='ID of the session to query stats for.')
get_parser.add_argument('id_participant', type=int, help='ID of the participant to query stats for.')
get_parser.add_argument('id_device', type=int, help='ID of the device to query stats for.')
get_parser.add_argument('with_participants', type=inputs.boolean, help='Also includes related participants stats. Can '
                                                                       'not be used with "id_participant", '
                                                                       '"id_user_group", "id_session", "id_user" or '
                                                                       '"id_device".')
get_parser.add_argument('with_warnings', type=inputs.boolean, help='Also include warning information such as a '
                                                                   'participant not having sessions for some time or '
                                                                   'users not having logged on for some time. Can only '
                                                                   'be used with "id_site" for now.')


class UserQueryUserStats(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @user_multi_auth.login_required
    @api.expect(get_parser)
    @api.doc(description='Get stats for the specified item.',
             responses={200: 'Success',
                        400: 'Missing parameter - one id must be specified.',
                        500: 'Database error'})
    def get(self):
        parser = get_parser

        args = parser.parse_args()

        user_access = DBManager.userAccess(current_user)

        if args['id_user_group']:
            if not args['id_user_group'] in user_access.get_accessible_users_groups_ids():
                return gettext('Forbidden'), 403
            return UserQueryUserStats.get_user_group_stats(user_access, args['id_user_group'])

        if args['id_user']:
            if not args['id_user'] in user_access.get_accessible_users_ids():
                return gettext('Forbidden'), 403
            return UserQueryUserStats.get_user_stats(user_access, args['id_user'])

        if args['id_site']:
            if not args['id_site'] in user_access.get_accessible_sites_ids():
                return gettext('Forbidden'), 403
            return UserQueryUserStats.get_site_stats(user_access, args['id_site'], args['with_participants'],
                                                     args['with_warnings'])

        if args['id_project']:
            if not args['id_project'] in user_access.get_accessible_projects_ids():
                return gettext('Forbidden'), 403
            return UserQueryUserStats.get_project_stats(user_access, args['id_project'], args['with_participants'])

        if args['id_group']:
            if not args['id_group'] in user_access.get_accessible_groups_ids():
                return gettext('Forbidden'), 403
            return UserQueryUserStats.get_participant_group_stats(user_access, args['id_group'],
                                                                  args['with_participants'])

        if args['id_session']:
            # if not args['id_session'] in user_access.get_accessible_sessions_ids():
            #     return gettext('Forbidden'), 403
            if not user_access.query_session(session_id=args['id_session']):
                return gettext('Forbidden'), 403
            return UserQueryUserStats.get_session_stats(user_access, args['id_session'])

        if args['id_participant']:
            if not args['id_participant'] in user_access.get_accessible_participants_ids():
                return gettext('Forbidden'), 403
            return UserQueryUserStats.get_participant_stats(user_access, args['id_participant'])

        if args['id_device']:
            if not args['id_device'] in user_access.get_accessible_devices_ids():
                return gettext('Forbidden'), 403
            return UserQueryUserStats.get_device_stats(user_access, args['id_device'])

        return gettext('Missing id argument'), 400

    @staticmethod
    def get_user_group_stats(user_access: DBManagerTeraUserAccess, item_id: int) -> dict:
        stats = {'users_total_count': len(user_access.query_users_for_usergroup(user_group_id=item_id)),
                 'users_enabled_count': len(user_access.query_users_for_usergroup(user_group_id=item_id,
                                                                                  enabled_only=True)),
                 'projects_total_count': len(user_access.query_project_access_for_user_group(user_group_id=item_id)),
                 'projects_admin_count': len(user_access.query_project_access_for_user_group(user_group_id=item_id,
                                                                                             admin_only=True)),
                 'sites_total_count': len(user_access.query_site_access_for_user_group(user_group_id=item_id)),
                 'sites_admin_count': len(user_access.query_site_access_for_user_group(user_group_id=item_id,
                                                                                       admin_only=True))}
        return stats

    @staticmethod
    def get_user_stats(user_access: DBManagerTeraUserAccess, item_id: int) -> dict:
        from opentera.db.models.TeraSession import TeraSession
        total_created_sessions = TeraSession.count_with_filters({'id_creator_user': item_id})
        user_sessions = TeraSession.get_sessions_for_user(item_id)
        sessions_participants = set()
        for ses in user_sessions:
            sessions_participants = sessions_participants.union(
                set([participant for participant in ses.session_participants]))
        enabled_participants = [participant for participant in sessions_participants if participant.participant_enabled]

        stats = {'sessions_created_total_count': total_created_sessions,
                 'sessions_total_count': len(user_sessions),
                 'participants_total_count': len(sessions_participants),
                 'participants_enabled_count': len(enabled_participants)
                 }
        return stats

    @staticmethod
    def get_site_stats(user_access: DBManagerTeraUserAccess, item_id: int, with_parts: bool, with_warnings: bool) \
            -> dict:
        from opentera.db.models.TeraSessionParticipants import TeraSessionParticipants
        from opentera.db.models.TeraParticipantGroup import TeraParticipantGroup
        from opentera.db.models.TeraParticipant import TeraParticipant
        from opentera.db.models.TeraDeviceSite import TeraDeviceSite
        site_projects = user_access.query_projects_for_site(item_id)
        site_users = user_access.query_users_for_site(site_id=item_id)
        site_users_enabled = [user for user in site_users if user.user_enabled]
        # site_users_enabled = user_access.query_users_for_site(site_id=item_id, enabled_only=True)
        site_groups_total = 0
        participants_total = 0
        participants_enabled = 0
        sessions_total = 0
        # devices = []
        for project in site_projects:
            site_groups_total += TeraParticipantGroup.count_with_filters({'id_project': project.id_project})
            participants_total += TeraParticipant.count_with_filters({'id_project': project.id_project})
            participants_enabled += TeraParticipant.count_with_filters({'id_project': project.id_project,
                                                                        'participant_enabled': True})

            for part in project.project_participants:
                sessions_total += TeraSessionParticipants.get_session_count_for_participant(
                    id_participant=part.id_participant)

        # devices = set(devices)  # Remove duplicates
        stats = {'users_total_count': len(site_users),
                 'users_enabled_count': len(site_users_enabled),
                 'projects_count': len(site_projects),
                 'participants_groups_count': site_groups_total,
                 'participants_total_count': participants_total,
                 'participants_enabled_count': participants_enabled,
                 'sessions_total_count': sessions_total,
                 'devices_total_count': TeraDeviceSite.count_with_filters({'id_site': item_id})
                 }
        # Add participants information?
        participants = []
        if with_parts:
            participants = user_access.query_all_participants_for_site(item_id)
            part_stats = [UserQueryUserStats.get_participant_list_stats(part) for part in participants]
            stats['participants'] = part_stats

        # Add warnings information?
        if with_warnings:
            today = datetime.datetime.now().date()

            # Participants
            if len(participants) == 0:
                participants = user_access.query_all_participants_for_site(item_id)
            # Keep only enabled participants and with last session within the last 6 months
            participants = [part for part in participants if part.participant_enabled]

            warning_parts = []
            no_session_parts = []
            for part in participants:
                last_session = part.get_last_session()
                if last_session:
                    diff_month = UserQueryUserStats.diff_month(today, last_session.session_start_datetime)
                    if diff_month >= 6:
                        warning_parts.append({'id_participant': part.id_participant,
                                              'participant_name': part.participant_name,
                                              'project_name': part.participant_project.project_name,
                                              'last_session': last_session.session_start_datetime.isoformat(),
                                              'months': diff_month})
                else:
                    updated_date = datetime.datetime.fromtimestamp(part.version_id/1000)
                    diff_month = UserQueryUserStats.diff_month(today, updated_date)
                    if diff_month >= 1:
                        no_session_parts.append({'id_participant': part.id_participant,
                                                 'participant_name': part.participant_name,
                                                 'project_name': part.participant_project.project_name,
                                                 'last_updated': updated_date.isoformat(),
                                                 'months': diff_month})
            stats['warning_participants_count'] = len(warning_parts)
            stats['warning_participants'] = warning_parts

            stats['warning_nosession_participants_count'] = len(no_session_parts)
            stats['warning_nosession_participants'] = no_session_parts

            # Users
            users = user_access.query_users_for_site(item_id)
            # Keep only enabled users
            users = [user for user in users if user.user_enabled and not user.user_superadmin]

            warning_users = []
            warning_neverlogged_users = []
            for user in users:
                if user.user_lastonline:
                    diff_month = UserQueryUserStats.diff_month(today, user.user_lastonline)
                    if diff_month >= 3:
                        warning_users.append({'id_user': user.id_user,
                                              'user_fullname': user.get_fullname(),
                                              'user_lastonline': user.user_lastonline.isoformat(),
                                              'months': diff_month})
                else:
                    updated_date = datetime.datetime.fromtimestamp(user.version_id/1000)
                    diff_month = UserQueryUserStats.diff_month(today, updated_date)
                    if diff_month >= 1:
                        warning_neverlogged_users.append({'id_user': user.id_user,
                                                          'user_fullname': user.get_fullname(),
                                                          'last_updated': updated_date.isoformat(),
                                                          'months': diff_month})
            stats['warning_users_count'] = len(warning_users)
            stats['warning_users'] = warning_users
            stats['warning_neverlogged_users_count'] = len(warning_neverlogged_users)
            stats['warning_neverlogged_users'] = warning_neverlogged_users

            # TODO: Old assets

        return stats

    @staticmethod
    def get_project_stats(user_access: DBManagerTeraUserAccess, item_id: int, with_parts: bool) -> dict:
        from opentera.db.models.TeraSessionParticipants import TeraSessionParticipants
        from opentera.db.models.TeraProject import TeraProject
        project_users = user_access.query_users_for_project(project_id=item_id)
        project_users_enabled = user_access.query_users_for_project(project_id=item_id, enabled_only=True)
        project = TeraProject.get_project_by_id(item_id)
        project_groups_total = len(project.project_participants_groups)
        participants_total = len(project.project_participants)
        participants_enabled = len([part for part in project.project_participants if part.participant_enabled])
        sessions_total = 0
        for part in project.project_participants:
            sessions_total += TeraSessionParticipants.get_session_count_for_participant(
                    id_participant=part.id_participant)

        stats = {'users_total_count': len(project_users),
                 'users_enabled_count': len(project_users_enabled),
                 'participants_groups_count': project_groups_total,
                 'participants_total_count': participants_total,
                 'participants_enabled_count': participants_enabled,
                 'sessions_total_count': sessions_total
                 }

        # Add participants information?
        if with_parts:
            participants = user_access.query_all_participants_for_project(item_id)
            part_stats = [UserQueryUserStats.get_participant_list_stats(part) for part in participants]
            stats['participants'] = part_stats

        return stats

    @staticmethod
    def get_participant_group_stats(user_access: DBManagerTeraUserAccess, item_id: int, with_parts: bool) -> dict:
        # from opentera.db.models.TeraParticipantGroup import TeraParticipantGroup
        from opentera.db.models.TeraSessionParticipants import TeraSessionParticipants
        # group = TeraParticipantGroup.get_participant_group_by_id(item_id)
        participants = user_access.query_participants_for_group(item_id)
        participants_total = len(participants)

        participants_enabled = len([part for part in participants if part.participant_enabled])
        sessions_total = 0
        for part in participants:
            sessions_total += TeraSessionParticipants.get_session_count_for_participant(
                    id_participant=part.id_participant)
            # len(TeraSession.get_sessions_for_participant(part.id_participant))

        stats = {'participants_total_count': participants_total,
                 'participants_enabled_count': participants_enabled,
                 'sessions_total_count': sessions_total
                 }

        # Add participants information?
        if with_parts:
            part_stats = [UserQueryUserStats.get_participant_list_stats(part) for part in participants]
            stats['participants'] = part_stats

        return stats

    @staticmethod
    def get_session_stats(user_access: DBManagerTeraUserAccess, item_id: int) -> dict:
        from opentera.db.models.TeraSession import TeraSession
        ses = TeraSession.get_session_by_id(item_id)

        stats = {'users_total_count': len(ses.session_users),
                 'participants_total_count': len(ses.session_participants),
                 'devices_total_count': len(ses.session_devices),
                 'assets_total_count': len(ses.session_assets),
                 'events_total_count': len(ses.session_events),
                 'tests_total_count': 0
                 }
        return stats

    @staticmethod
    def get_participant_stats(user_access: DBManagerTeraUserAccess, item_id: int) -> dict:
        from opentera.db.models.TeraParticipant import TeraParticipant
        from opentera.db.models.TeraSession import TeraSessionStatus
        from opentera.db.models.TeraAsset import TeraAsset
        participant = TeraParticipant.get_participant_by_id(item_id)
        sessions_total_time = sum([ses.session_duration for ses in participant.participant_sessions])
        if len(participant.participant_sessions) > 0:
            sessions_mean_time = sessions_total_time / len(participant.participant_sessions)
        else:
            sessions_mean_time = 0
        sessions_assets_total = len(TeraAsset.get_assets_for_participant(item_id))
        # sum([len(ses.session_assets) for ses in participant.participant_sessions])
        # users_involved = set()
        # for ses in participant.participant_sessions:
        #     users_involved = users_involved.union(set([user for user in ses.session_users]))

        stats = {'sessions_total_count': len(participant.participant_sessions),
                 'sessions_total_time': sessions_total_time,
                 'sessions_mean_time': sessions_mean_time,
                 'sessions_planned_count': len([ses.id_session for ses in participant.participant_sessions
                                                if ses.session_status == TeraSessionStatus.STATUS_NOTSTARTED.value]),
                 'sessions_completed_count': len([ses.id_session for ses in participant.participant_sessions
                                                  if ses.session_status == TeraSessionStatus.STATUS_COMPLETED.value]),
                 'sessions_inprogress_count': len([ses.id_session for ses in participant.participant_sessions
                                                   if ses.session_status == TeraSessionStatus.STATUS_INPROGRESS.value]),
                 'sessions_cancelled_count': len([ses.id_session for ses in participant.participant_sessions
                                                  if ses.session_status == TeraSessionStatus.STATUS_CANCELLED.value]),
                 'sessions_terminated_count': len([ses.id_session for ses in participant.participant_sessions
                                                  if ses.session_status == TeraSessionStatus.STATUS_TERMINATED.value]),
                 # 'users_total_count': len(users_involved),
                 'assets_total_count': sessions_assets_total,
                 'tests_total_count': 0}
        return stats

    @staticmethod
    def get_device_stats(user_access: DBManagerTeraUserAccess, item_id: int) -> dict:
        from opentera.db.models.TeraDevice import TeraDevice
        device = TeraDevice.get_device_by_id(item_id)
        stats = {'assets_total_count': len(device.device_assets),
                 'projects_total_count': len(device.device_projects),
                 'participants_total_count': len(device.device_participants),
                 }
        return stats

    @staticmethod
    def get_participant_list_stats(participant: TeraParticipant):
        first_session = participant.get_first_session()
        first_session_date = None
        if first_session:
            first_session_date = first_session.session_start_datetime.isoformat()

        last_session = participant.get_last_session()
        last_session_date = None
        if last_session:
            last_session_date = last_session.session_start_datetime.isoformat()

        last_online = participant.participant_lastonline
        last_online_date = None
        if last_online:
            last_online_date = last_online.isoformat()

        stats = {'id_participant': participant.id_participant,
                 'participant_name': participant.participant_name,
                 'participant_enabled': participant.participant_enabled,
                 'participant_sessions_count': len(participant.participant_sessions),
                 'participant_first_session': first_session_date,
                 'participant_last_session': last_session_date,
                 'participant_last_online': last_online_date
                 }
        return stats

    @staticmethod
    def diff_month(d1: datetime, d2: datetime):
        return (d1.year - d2.year) * 12 + d1.month - d2.month
