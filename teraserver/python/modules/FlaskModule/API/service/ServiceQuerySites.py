from flask_restx import Resource
from flask_babel import gettext
from modules.LoginModule.LoginModule import LoginModule, current_service
from modules.FlaskModule.FlaskModule import service_api_ns as api
from modules.DatabaseModule.DBManager import DBManager
from opentera.db.models.TeraSite import TeraSite

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_site', type=int, help='ID of the site to query')
get_parser.add_argument('id_user', type=int, help='ID of the user to query sites for')


class ServiceQuerySites(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Return sites information.',
             responses={200: 'Success',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Service doesn\'t have permission to access the requested data'},
             params={'token': 'Access token'})
    @api.expect(get_parser)
    @LoginModule.service_token_or_certificate_required
    def get(self):
        """
        Get sites
        """
        args = get_parser.parse_args(strict=True)
        service_access = DBManager.serviceAccess(current_service)

        sites = []
        if args['id_site']:
            if args['id_site'] not in service_access.get_accessibles_sites_ids():
                return gettext('Forbidden'), 403
            sites = [TeraSite.get_site_by_id(args['id_site'])]
        elif args['id_user']:
            sites = service_access.query_sites_for_user(user_id=args['id_user'])
        else:
            sites = service_access.get_accessibles_sites()

        sites_list = [site.to_json(minimal=True) for site in sites]
        return sites_list
