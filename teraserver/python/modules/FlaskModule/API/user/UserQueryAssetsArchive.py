from flask import session, request, Response
from flask_restx import Resource, inputs
from flask_babel import gettext
from modules.LoginModule.LoginModule import user_multi_auth, current_user
from modules.FlaskModule.FlaskModule import user_api_ns as api
from modules.FlaskModule import FlaskModule
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraAsset import TeraAsset
from opentera.db.models.TeraService import TeraService
from opentera.db.models.TeraProject import TeraProject
from opentera.db.models.TeraSession import TeraSession
from opentera.db.models.TeraParticipant import TeraParticipant
import zipfile
from io import BytesIO
import requests
import sys
import subprocess
import json
from modules.DatabaseModule.DBManager import DBManager
from opentera.redis.RedisVars import RedisVars
import datetime

# Parser definition(s)
# GET
get_parser = api.parser()
get_parser.add_argument('id_participant', type=int, help='ID of the participant from which to request all associated '
                                                         'assets', default=None)
get_parser.add_argument('id_project', type=int, help='ID of the project from which to request all associated assets',
                        default=None)
get_parser.add_argument('id_session', type=int, help='ID of the session from which to request all associated assets',
                        default=None)


class UserQueryAssetsArchive(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module: FlaskModule = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Get asset archive. Only one of the ID parameter is supported at once.',
             responses={200: 'Success - returns list of assets',
                        400: 'Required parameter is missing',
                        403: 'Logged user doesn\'t have permission to access the requested data'},
             params={'token': 'Secret token'})
    @api.expect(get_parser)
    @user_multi_auth.login_required
    def get(self):
        # Get parameters
        args = get_parser.parse_args()
        user_access = DBManager.userAccess(current_user)

        asset_map_per_service = {}

        service_key = self.module.redisGet(RedisVars.RedisVar_ServiceTokenAPIKey)

        # Load all enabled services and store information
        for service in TeraService.query_with_filters({'service_enabled': True}):
            if service.service_key == 'OpenTeraServer':
                continue

            service_token = service.get_token(service_key)
            # Fill all required info for service
            asset_map_per_service[service.service_key] = {'service_uuid': service.service_uuid,
                                                          'service_assets': [],
                                                          'service_endpoint': service.service_clientendpoint,
                                                          'service_token': service_token}

        # Base server information
        service_key: bytes = self.module.redisGet(RedisVars.RedisVar_ServiceTokenAPIKey)
        server_name = self.module.config.server_config['hostname']
        port = self.module.config.server_config['port']

        if 'X_EXTERNALSERVER' in request.headers:
            server_name = request.headers['X_EXTERNALSERVER']

        if 'X_EXTERNALPORT' in request.headers:
            port = request.headers['X_EXTERNALPORT']

        # Verify if only one arg is set
        if sum(x is not None for x in [args['id_project'], args['id_participant'], args['id_session']]) != 1:
            return gettext('Only one of the ID parameter is supported at once'), 400

        def add_asset_to_list(asset: TeraAsset, path: str = ''):
            value = asset.to_json(minimal=False)
            value['path'] = f"{path}"
            current_service = TeraService.get_service_by_uuid(asset.asset_service_uuid)
            if current_service.service_key in asset_map_per_service:
                asset_map_per_service[current_service.service_key]['service_assets'].append(value)

        def get_assets_for_session(sess: TeraSession, path: str = ''):
            assets: list[TeraAsset] = TeraAsset.get_assets_for_session(sess.id_session)
            for asset in assets:
                add_asset_to_list(asset, path + f"/{sess.id_session}_{sess.session_name}")

        def get_assets_for_participant(participant: TeraParticipant, path: str = ''):
            sessions: list[TeraSession] = TeraSession.get_sessions_for_participant(participant.id_participant)
            for sess in sessions:
                get_assets_for_session(sess, path = path + f"/{participant.participant_name}")

        def get_assets_for_project(project: TeraProject, path: str = ''):
            participants: list[TeraParticipant] = user_access.query_all_participants_for_project(project.id_project)
            for participant in participants:
                get_assets_for_participant(participant, path + f"/{project.project_name}")

        # Check if we have a participant, project or session
        if args['id_project'] is not None:
            # Verify access to project
            if args['id_project'] not in user_access.get_accessible_projects_ids():
                return gettext('Forbidden'), 403

            p = TeraProject.get_project_by_id(args['id_project'])
            site = p.project_site
            get_assets_for_project(p, f"/{site.site_name}")

        elif args['id_participant'] is not None:
            # Get all assets for participant
            if args['id_participant'] not in user_access.get_accessible_participants_ids():
                return gettext('Forbidden'), 403

            participant = TeraParticipant.get_participant_by_id(args['id_participant'])
            project = participant.participant_project
            site = project.project_site
            get_assets_for_participant(participant,
                                       f"/{site.site_name}/{project.projet_name}")

        elif args['id_session'] is not None:
            # Get all assets for session
            if args['id_session'] not in user_access.get_accessible_sessions_ids():
                return gettext('Forbidden'), 403

            sess = TeraSession.get_session_by_id(args['id_session'])

            # Session is not related to a participant, get all assets with no path
            if len(sess.session_participants) == 0:
                get_assets_for_session(sess)
            else:
                for participant in sess.session_participants:
                    project = participant.participant_project
                    site = project.project_site
                    get_assets_for_session(sess,
                                           f"/{site.site_name}/{project.project_name}/{participant.participant_name}")

        else:
            return gettext('Missing required parameter'), 400

        # Create a job ID (will need a better way to generate ids)
        job_id = 'job.id.1'

        # Clean up unused service in asset map
        asset_map_per_service = {k: v for k, v in asset_map_per_service.items() if len(v['service_assets']) > 0}

        # Generate archive file name with current time
        # create a string with the current date and time
        archive_name = f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_archive.zip"

        job_info = {'job_id': job_id,
                    'server_name': server_name,
                    'port': port,
                    'service_key': service_key.decode('utf-8'),
                    'status': 'running',
                    'assets_map': asset_map_per_service,
                    'owner_uuid': current_user.user_uuid,
                    'archive_name': archive_name}

        # TODO set job information with expiration
        self.module.redisSet(job_id, json.dumps(job_info), ex=60)

        # Launch subprocess
        command = [sys.executable, 'workers/AssetsArchiveWorker.py', '--config', 'config/TeraServerConfig.ini',
                   '--job_id', job_id]
        process = subprocess.Popen(command)

        return asset_map_per_service

    @api.doc(description='Create asset archive.',
             responses={501: 'Unable to create asset information from here'},
             params={'token': 'Secret token'})
    @user_multi_auth.login_required
    def post(self):
        pass



