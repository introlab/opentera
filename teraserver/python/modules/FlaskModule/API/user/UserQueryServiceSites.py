from flask import jsonify, request
from flask_restx import Resource, reqparse, inputs
from modules.LoginModule.LoginModule import user_multi_auth, current_user
from modules.FlaskModule.FlaskModule import user_api_ns as api
from opentera.db.models.TeraServiceSite import TeraServiceSite
from opentera.db.models.TeraServiceRole import TeraServiceRole
from opentera.db.models.TeraService import TeraService
from opentera.db.models.TeraSite import TeraSite
from modules.DatabaseModule.DBManager import DBManager
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc, inspect
from flask_babel import gettext

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_site', type=int, help='Site ID to query associated services')
get_parser.add_argument('id_service', type=int, help='Service ID to query associated projects from')
get_parser.add_argument('list', type=inputs.boolean, help='Flag that limits the returned data to minimal information '
                                                          '(ids only)')
get_parser.add_argument('with_sites', type=inputs.boolean, help='Used with id_service. Also return sites that '
                                                                'don\'t have any association with that service')
get_parser.add_argument('with_services', type=inputs.boolean, help='Used with id_site. Also return services that '
                                                                   'don\'t have any association with that site')
get_parser.add_argument('with_roles', type=inputs.boolean, help='Used with id_site. Returns detailled information on'
                                                                'each role for this service.')

# post_parser = reqparse.RequestParser()
# post_parser.add_argument('service_project', type=str, location='json',
#                          help='Service - project association to create / update', required=True)
post_schema = api.schema_model('service_site', {'properties': TeraServiceSite.get_json_schema(),
                                                'type': 'object',
                                                'location': 'json'})

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='Specific service - site association ID to delete. '
                                                'Be careful: this is not the service or site ID, but the ID'
                                                ' of the association itself!', required=True)


class UserQueryServiceSites(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @user_multi_auth.login_required
    @api.expect(get_parser)
    @api.doc(description='Get services that are associated with a site. Only one "ID" parameter required and '
                         'supported at once.',
             responses={200: 'Success - returns list of services - sites association',
                        400: 'Required parameter is missing (must have at least one id)',
                        500: 'Error when getting association'})
    def get(self):
        user_access = DBManager.userAccess(current_user)

        parser = get_parser

        args = parser.parse_args()

        service_sites = []
        # If we have no arguments, return error
        if not any(args.values()):
            return gettext('Missing arguments'), 400

        if args['id_site']:
            if args['id_site'] in user_access.get_accessible_sites_ids():
                service_sites = user_access.query_services_sites_for_site(site_id=args['id_site'],
                                                                          include_other_services=args['with_services'])
        else:
            if args['id_service']:
                if args['id_service'] in user_access.get_accessible_services_ids():
                    service_sites = user_access.query_sites_for_service(service_id=args['id_service'],
                                                                        include_other_sites=
                                                                        args['with_sites'])
        try:
            ss_list = []
            for ss in service_sites:
                json_ss = ss.to_json()
                if args['list'] is None:
                    obj_type = inspect(ss)
                    if not obj_type.transient:
                        json_ss['service_name'] = ss.service_site_service.service_name
                        json_ss['service_key'] = ss.service_site_service.service_key
                        json_ss['service_system'] = ss.service_site_service.service_system
                        json_ss['site_name'] = ss.service_site_site.site_name
                    else:
                        # Temporary object, a not-committed object, result of listing sites not associated in a
                        # service.
                        if ss.id_service:
                            service = TeraService.get_service_by_id(ss.id_service)
                            json_ss['service_name'] = service.service_name
                            json_ss['service_key'] = service.service_key
                            json_ss['service_system'] = service.service_system
                        else:
                            json_ss['service_name'] = None
                            json_ss['service_key'] = None
                            json_ss['service_system'] = None
                        if ss.id_site:
                            json_ss['site_name'] = TeraSite.get_site_by_id(ss.id_site).site_name
                        else:
                            json_ss['site_name'] = None
                if args['with_roles']:
                    service_roles = TeraServiceRole.get_service_roles(ss.id_service)
                    json_roles = []
                    for role in service_roles:
                        json_roles.append(role.to_json(ignore_fields=['id_service']))
                    json_ss['service_roles'] = json_roles
                ss_list.append(json_ss)
            return ss_list

        except InvalidRequestError as e:
            self.module.logger.log_error(self.module.module_name,
                                         UserQueryServiceSites.__name__,
                                         'get', 500, 'InvalidRequestError', str(e))
            return gettext('Invalid request'), 500

    @user_multi_auth.login_required
    @api.expect(post_schema)
    @api.doc(description='Create/update service - site association. If a "service" json is received, the list of '
                         '"sites" is replaced. If a "site" json is received, the list of "services" is replaced.'
                         'If a "service_site" is received, each of the item in the list is added.',
             responses={200: 'Success',
                        403: 'Logged user can\'t modify association (only super admin can modify association)',
                        400: 'Badly formed JSON or missing fields(id_project or id_service) in the JSON body',
                        500: 'Internal error occured when saving association'})
    def post(self):
        # parser = post_parser
        user_access = DBManager.userAccess(current_user)

        # Only super admins can change service - site associations
        if not current_user.user_superadmin:
            return gettext('Forbidden'), 403

        if 'service' in request.json:
            # We have a service. Get list of items
            if 'id_service' not in request.json['service']:
                return gettext('Missing id_service'), 400
            if 'sites' not in request.json['service']:
                return gettext('Missing sites'), 400
            id_service = request.json['service']['id_service']

            # Get all current association for service
            current_sites = TeraServiceSite.get_sites_for_service(id_service=id_service)
            current_sites_ids = [site.id_site for site in current_sites]
            received_sites_ids = [site['id_site'] for site in request.json['service']['sites']]
            # Difference - we must delete sites not anymore in the list
            todel_ids = set(current_sites_ids).difference(received_sites_ids)
            # Also filter sites already there
            received_sites_ids = set(received_sites_ids).difference(current_sites_ids)
            for site_id in todel_ids:
                TeraServiceSite.delete_with_ids(service_id=id_service, site_id=site_id)
            # Build projects association to add
            json_sss = [{'id_service': id_service, 'id_site': site_id} for site_id in received_sites_ids]
        elif 'site' in request.json:
            # We have a project. Get list of items
            if 'id_site' not in request.json['site']:
                return gettext('Missing site ID'), 400
            if 'services' not in request.json['site']:
                return gettext('Missing services'), 400
            id_site = request.json['site']['id_site']

            # Get all current association for site
            current_services = TeraServiceSite.get_services_for_site(id_site=id_site)
            current_services_ids = [service.id_service for service in current_services]
            received_services_ids = [service['id_service'] for service in request.json['site']['services']]
            # Difference - we must delete services not anymore in the list
            todel_ids = set(current_services_ids).difference(received_services_ids)
            # Also filter services already there
            received_services_ids = set(received_services_ids).difference(current_services_ids)
            for service_id in todel_ids:
                TeraServiceSite.delete_with_ids(service_id=service_id, site_id=id_site)
            # Build sites association to add
            json_sss = [{'id_service': service_id, 'id_site': id_site} for service_id in received_services_ids]
        elif 'service_site' in request.json:
            json_sss = request.json['service_site']
            if not isinstance(json_sss, list):
                json_sss = [json_sss]
        else:
            return '', 400

        # Validate if we have an id and access
        for json_ss in json_sss:
            if 'service_uuid' in json_ss:
                # Get id for that uuid
                from opentera.db.models.TeraService import TeraService
                json_ss['id_service'] = TeraService.get_service_by_uuid(json_ss['service_uuid']).id_service
                del json_ss['service_uuid']

            if 'id_service' not in json_ss or 'id_site' not in json_ss:
                return gettext('Badly formatted request'), 400

            if 'id_service_site' not in json_ss:
                # Check if already exists
                ss = TeraServiceSite.get_service_site_for_service_site(site_id=int(json_ss['id_site']),
                                                                       service_id=int(json_ss['id_service']))
                if ss:
                    json_ss['id_service_site'] = ss.id_service_site
                else:
                    json_ss['id_service_site'] = 0

            # Do the update!
            if int(json_ss['id_service_site']) > 0:
                # Already existing
                try:
                    TeraServiceSite.update(int(json_ss['id_service_site']), json_ss)
                except exc.SQLAlchemyError as e:
                    import sys
                    print(sys.exc_info())
                    self.module.logger.log_error(self.module.module_name,
                                                 UserQueryServiceSites.__name__,
                                                 'post', 500, 'Database error', str(e))
                    return gettext('Database error'), 500
            else:
                try:
                    new_ss = TeraServiceSite()
                    new_ss.from_json(json_ss)
                    TeraServiceSite.insert(new_ss)
                    # Update ID for further use
                    json_ss['id_service_site'] = new_ss.id_service_site
                except exc.SQLAlchemyError as e:
                    import sys
                    print(sys.exc_info())
                    self.module.logger.log_error(self.module.module_name,
                                                 UserQueryServiceSites.__name__,
                                                 'post', 500, 'Database error', str(e))
                    return gettext('Database error'), 500

        return json_sss

    @user_multi_auth.login_required
    @api.expect(delete_parser)
    @api.doc(description='Delete a specific service - site association.',
             responses={200: 'Success',
                        403: 'Logged user can\'t delete association (only super admins can)',
                        500: 'Association not found or database error.'})
    def delete(self):
        parser = delete_parser
        user_access = DBManager.userAccess(current_user)

        if not current_user.user_superadmin:
            return gettext('Forbidden'), 403

        args = parser.parse_args()
        id_todel = args['id']

        ss = TeraServiceSite.get_service_site_by_id(id_todel)
        if not ss:
            return gettext('Not found'), 400

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraServiceSite.delete(id_todel=id_todel)
        except exc.SQLAlchemyError as e:
            import sys
            print(sys.exc_info())
            self.module.logger.log_error(self.module.module_name,
                                         UserQueryServiceSites.__name__,
                                         'delete', 500, 'Database error', str(e))
            return gettext('Database error'), 500

        return '', 200
