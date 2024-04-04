from flask import session, request, Response
from flask_restx import Resource, inputs
from flask_babel import gettext
from modules.LoginModule.LoginModule import user_multi_auth, current_user
from modules.FlaskModule.FlaskModule import user_api_ns as api
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraAsset import TeraAsset
from opentera.db.models.TeraService import TeraService
from opentera.db.models.TeraProject import TeraProject
from opentera.db.models.TeraSession import TeraSession
from opentera.db.models.TeraParticipant import TeraParticipant
import zipfile
from io import BytesIO
import requests

from modules.DatabaseModule.DBManager import DBManager
from opentera.redis.RedisVars import RedisVars

# Parser definition(s)
# GET
get_parser = api.parser()


class UserQueryAssetsArchive(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Get asset information. Only one of the ID parameter is supported at once',
             responses={200: 'Success - returns list of assets',
                        400: 'Required parameter is missing',
                        403: 'Logged user doesn\'t have permission to access the requested data'},
             params={'token': 'Secret token'})
    @api.expect(get_parser)
    @user_multi_auth.login_required
    def get(self):
        user_access = DBManager.userAccess(current_user)

        service_key = self.module.redisGet(RedisVars.RedisVar_ServiceTokenAPIKey)
        servername = self.module.config.server_config['hostname']
        port = self.module.config.server_config['port']
        if 'X_EXTERNALSERVER' in request.headers:
            servername = request.headers['X_EXTERNALSERVER']

        if 'X_EXTERNALPORT' in request.headers:
            port = request.headers['X_EXTERNALPORT']

        # Load all enabled services
        services_infos = {service.service_uuid: service.service_clientendpoint
                          for service in TeraService.query_with_filters({'service_enabled': True})}

        # Create an in-memory binary stream to store the zip file
        zip_buffer = BytesIO()

        # Create a ZipFile object to write to the in-memory stream
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:

            project: TeraProject = TeraProject.get_project_by_id(1)
            site = project.project_site

            # Already filtered with accessible participants
            participants: list[TeraParticipant] = user_access.query_all_participants_for_project(project.id_project)

            for participant in participants:
                # Get all assets from participant
                sessions: list[TeraSession] = TeraSession.get_sessions_for_participant(participant.id_participant)

                for sess in sessions:
                    assets: list[TeraAsset] = TeraAsset.get_assets_for_session(sess.id_session)
                    for asset in assets:

                        # Verify if service is enabled
                        if asset.asset_service_uuid in services_infos and asset.asset_service_owner:

                            # Get the file (from the service that created the file)
                            service = asset.asset_service_owner
                            service_token = service.get_token(service_key)

                            # Generate access token
                            access_token = asset.get_access_token([asset.asset_uuid], service_key,
                                                                  service.service_uuid)

                            # What to do with duplicated names ?
                            filepath = site.site_name + '/' + project.project_name + '/' + participant.participant_name \
                                       + '/' + sess.session_name + '/' + asset.asset_name

                            # Generate URL to fetch asset
                            params = {'access_token': access_token, 'asset_uuid': asset.asset_uuid}
                            url = 'https://' + servername + ':' + str(port) \
                                  + services_infos[asset.asset_service_uuid] + '/api/assets'

                            headers = {'Authorization': 'OpenTera ' + service_token}
                            response = requests.get(url=url, params=params, headers=headers, verify=False)

                            if response.status_code == 200:
                                zip_file.writestr(filepath, response.content)

        # Set the BytesIO object's position to the beginning
        zip_buffer.seek(0)

        # Create a Flask response with the zip file as the data
        response = Response(zip_buffer.getvalue(), mimetype='application/zip')

        # Set appropriate content-disposition headers
        response.headers['Content-Disposition'] = 'attachment; filename=data.zip'

        return response

    @api.doc(description='Create asset archive.',
             responses={501: 'Unable to create asset information from here'},
             params={'token': 'Secret token'})
    @user_multi_auth.login_required
    def post(self):
        pass



