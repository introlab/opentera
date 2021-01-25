from flask import jsonify, session, request
from flask_restx import Resource, reqparse
from sqlalchemy import exc
from modules.LoginModule.LoginModule import user_multi_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api
from sqlalchemy.exc import InvalidRequestError
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraSite import TeraSite
from modules.DatabaseModule.DBManager import DBManager
from flask_babel import gettext

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_site', type=int, help='ID of the site to query')
get_parser.add_argument('id', type=int, help='Alias for "id_site"')
get_parser.add_argument('id_device', type=int, help='ID of the device from which to get all related sites')
get_parser.add_argument('user_uuid', type=str, help='User UUID from which to get all sites that are accessible')
get_parser.add_argument('name', type=str, help='Site name to query')

# post_parser = reqparse.RequestParser()
# post_parser.add_argument('site', type=str, location='json', help='Site to create / update', required=True)
post_schema = api.schema_model('user_site', {'properties': TeraSite.get_json_schema(),
                                             'type': 'object',
                                             'location': 'json'})

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='Site ID to delete', required=True)


class UserQuerySites(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @user_multi_auth.login_required
    @api.expect(get_parser)
    @api.doc(description='Get site information. Only one of the ID parameter is supported and required at once',
             responses={200: 'Success - returns list of sites',
                        500: 'Database error'})
    def get(self):
        parser = get_parser

        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)
        args = parser.parse_args()

        sites = []
        if args['id']:
            args['id_site'] = args['id']

        # If we have no arguments, return all accessible sites
        if not any(args.values()):
            sites = user_access.get_accessible_sites()
        # If we have a user_uuid, query for the site of that user
        elif args['user_uuid']:
            queried_user = TeraUser.get_user_by_uuid(args['user_uuid'])
            if queried_user is not None:
                current_sites = user_access.get_accessible_sites()
                user_access = DBManager.userAccess(queried_user)
                queried_sites = user_access.get_accessible_sites()
                # Match with accessible sites for the current user
                for site in queried_sites:
                    if site in current_sites:
                        sites.append(site)
        elif args['id_site']:
            if args['id_site'] in user_access.get_accessible_sites_ids():
                sites = [TeraSite.get_site_by_id(site_id=args['id_site'])]
        elif args['id_device']:
            sites = user_access.query_sites_for_device(args['id_device'])
        elif args['name']:
            sites = [TeraSite.get_site_by_sitename(sitename=args['name'])]
            for site in sites:
                if site is None and len(sites) == 1:
                    sites = None
                    break

                if site.id_site not in user_access.get_accessible_sites_ids():
                    # Current user doesn't have access to the requested site
                    sites = None

        if sites is None:
            sites = []

        try:
            sites_list = []
            for site in sites:
                if site is not None:
                    site_json = site.to_json()
                    site_json['site_role'] = user_access.get_site_role(site_json['id_site'])
                    if args['id_device']:
                        site_json['id_device'] = args['id_device']
                    sites_list.append(site_json)
            return jsonify(sites_list)
        except InvalidRequestError as e:
            self.module.logger.log_error(self.module.module_name,
                                         UserQuerySites.__name__,
                                         'get', 500, 'InvalidRequestError', str(e))
            return gettext('Invalid request'), 500

    @user_multi_auth.login_required
    @api.expect(post_schema)
    @api.doc(description='Create / update site. id_site must be set to "0" to create a new '
                         'site. A site can be created/modified if the user has admin rights to the site itself or is'
                         'superadmin.',
             responses={200: 'Success',
                        403: 'Logged user can\'t create/update the specified site',
                        400: 'Badly formed JSON or missing field(id_site) in the JSON body',
                        500: 'Internal error when saving site'})
    def post(self):
        # parser = reqparse.RequestParser()
        # parser.add_argument('site', type=str, location='json', help='Site to create / update', required=True)

        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)
        # Using request.json instead of parser, since parser messes up the json!
        json_site = request.json['site']

        # Validate if we have an id
        if 'id_site' not in json_site:
            return gettext('Missing id_site field'), 400

        # Check if current user can modify the posted site
        if json_site['id_site'] not in user_access.get_accessible_sites_ids(admin_only=True) and \
                json_site['id_site'] > 0:
            return gettext('Forbidden'), 403

        # Do the update!
        if json_site['id_site'] > 0:
            # Already existing
            try:
                TeraSite.update(json_site['id_site'], json_site)
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             UserQuerySites.__name__,
                                             'post', 500, 'Database error', str(e))
                return gettext('Database error'), 500
        else:
            # New
            try:
                new_site = TeraSite()
                new_site.from_json(json_site)
                TeraSite.insert(new_site)
                # Update ID for further use
                json_site['id_site'] = new_site.id_site
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             UserQuerySites.__name__,
                                             'post', 500, 'Database error', str(e))
                return gettext('Database error'), 500

        # TODO: Publish update to everyone who is subscribed to sites update...
        update_site = TeraSite.get_site_by_id(json_site['id_site'])

        return jsonify([update_site.to_json()])

    @user_multi_auth.login_required
    @api.expect(delete_parser)
    @api.doc(description='Delete a specific site',
             responses={200: 'Success',
                        403: 'Logged user can\'t delete site (only super admin can delete)',
                        500: 'Database error.'})
    def delete(self):
        parser = delete_parser

        current_user = TeraUser.get_user_by_uuid(session['_user_id'])

        args = parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        # Only superadmin can delete sites from here
        if not current_user.user_superadmin:
            return gettext('Forbidden'), 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraSite.delete(id_todel=id_todel)
        except exc.IntegrityError as e:
            # Causes that could make an integrity error when deleting:
            # - Associated projects with particiapnts with sessions
            # - Associated projects with participant groups with participants with sessions
            self.module.logger.log_error(self.module.module_name,
                                         UserQuerySites.__name__,
                                         'delete', 500, 'Database error', str(e))
            return gettext('Can\'t delete site: please delete all participants with sessions before deleting.'), 500
        except exc.SQLAlchemyError as e:
            import sys
            print(sys.exc_info())
            self.module.logger.log_error(self.module.module_name,
                                         UserQuerySites.__name__,
                                         'delete', 500, 'Database error', str(e))
            return gettext('Database error'), 500

        return '', 200
