from flask import session, request
from flask_restx import Resource, reqparse, inputs
from modules.LoginModule.LoginModule import user_multi_auth, current_user
from modules.FlaskModule.FlaskModule import user_api_ns as api
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraSessionType import TeraSessionType
from opentera.db.models.TeraSite import TeraSite
from opentera.db.models.TeraSessionTypeSite import TeraSessionTypeSite
from modules.DatabaseModule.DBManager import DBManager
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc, inspect
from flask_babel import gettext

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_session_type', type=int, help='ID of the session type from which to request all associated '
                                                          'sites')
get_parser.add_argument('id_site', type=int, help='ID of the site from which to get all associated session types')
get_parser.add_argument('list', type=inputs.boolean, help='Flag that limits the returned data to minimal information '
                                                          '(ids only)')
get_parser.add_argument('with_session_type', type=inputs.boolean, help='Used with id_session_type. Also return session '
                                                                       'types that don\'t have any association with '
                                                                       'that site')
get_parser.add_argument('with_sites', type=inputs.boolean, help='Used with id_service. Also return site information '
                                                                'of the returned projects.')

post_schema = api.schema_model('user_session_type_site', {'properties': TeraSessionTypeSite.get_json_schema(),
                                                          'type': 'object',
                                                          'location': 'json'})


delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='Specific session type-site association ID to delete. Be careful: this'
                                                ' is not the session type or the site ID, but the ID of the '
                                                'association itself!', required=True)


class UserQuerySessionTypeSites(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @user_multi_auth.login_required
    @api.expect(get_parser)
    @api.doc(description='Get session types that are related to a site. Only one "ID" parameter required and supported'
                         ' at once.',
             responses={200: 'Success - returns list of session types - sites association',
                        400: 'Required parameter is missing (must have at least one id)',
                        500: 'Error occured when loading devices for sites'})
    def get(self):
        user_access = DBManager.userAccess(current_user)

        parser = get_parser

        args = parser.parse_args()

        sts_sites = []
        # If we have no arguments, return error
        if not any(args.values()):
            return gettext('Missing arguments'), 400

        if args['id_session_type']:
            if args['id_session_type'] in user_access.get_accessible_session_types_ids():
                sts_sites = user_access.query_session_types_sites_for_session_type(session_type_id=
                                                                                   args['id_session_type'],
                                                                                   include_other_sites=
                                                                                   args['with_sites']
                                                                                   )
        elif args['id_site']:
            if args['id_site'] in user_access.get_accessible_sites_ids():
                sts_sites = user_access.query_session_types_sites_for_site(site_id=args['id_site'],
                                                                           include_other_session_types=
                                                                           args['with_session_type'])
        try:
            sts_list = []
            for sts in sts_sites:
                json_sts = sts.to_json()
                if args['list'] is None:
                    obj_type = inspect(sts)
                    if not obj_type.transient:
                        json_sts['session_type_name'] = sts.session_type_site_session_type.session_type_name
                        json_sts['site_name'] = sts.session_type_site_site.site_name
                    else:
                        # Temporary object, a not-committed object, result of listing sites not associated to a
                        # session type.
                        if sts.id_session_type:
                            st: TeraSessionType = TeraSessionType.get_session_type_by_id(sts.id_session_type)
                            json_sts['session_type_name'] = st.session_type_name
                        else:
                            json_sts['session_type_name'] = None
                        if sts.id_site:
                            json_sts['site_name'] = TeraSite.get_site_by_id(sts.id_site).site_name
                        else:
                            json_sts['site_name'] = None
                sts_list.append(json_sts)
            return sts_list

        except InvalidRequestError as e:
            self.module.logger.log_error(self.module.module_name,
                                         UserQuerySessionTypeSites.__name__,
                                         'get', 500, 'InvalidRequestError', str(e))
            return gettext('Invalid request'), 500

    @user_multi_auth.login_required
    @api.expect(post_schema)
    @api.doc(description='Create/update session types associated with a site.',
             responses={200: 'Success',
                        403: 'Logged user can\'t modify device association',
                        400: 'Badly formed JSON or missing fields(id_site or id_device) in the JSON body',
                        500: 'Internal error occured when saving device association'})
    def post(self):
        # parser = post_parser
        user_access = DBManager.userAccess(current_user)

        # Only super admins can change session type - site associations
        # if not current_user.user_superadmin:
        #     return gettext('Forbidden'), 403
        accessible_sites_ids = user_access.get_accessible_sites_ids(admin_only=True)
        if 'session_type' in request.json:
            # We have a device. Get list of items
            if 'id_session_type' not in request.json['session_type']:
                return gettext('Missing id_session_type'), 400
            if 'sites' not in request.json['session_type']:
                return gettext('Missing sites'), 400
            id_session_type = request.json['session_type']['id_session_type']

            if id_session_type not in user_access.get_accessible_session_types_ids(admin_only=True):
                return gettext("Access denied"), 403

            # Get all current association for session type
            current_sites = TeraSessionTypeSite.get_sites_for_session_type(session_type_id=id_session_type)
            current_sites_ids = [site.id_site for site in current_sites]
            received_sites_ids = [site['id_site'] for site in request.json['session_type']['sites']]
            # Difference - we must delete sites not anymore in the list
            todel_ids = set(current_sites_ids).difference(received_sites_ids)
            # Also filter sites already there
            received_sites_ids = set(received_sites_ids).difference(current_sites_ids)
            for site_id in todel_ids:
                if site_id in accessible_sites_ids:  # Don't remove from the list if not site admin for that site!
                    TeraSessionTypeSite.delete_with_ids(session_type_id=id_session_type, site_id=site_id)
            # Build sites association to add
            json_sts = [{'id_session_type': id_session_type, 'id_site': site_id} for site_id in received_sites_ids]
        elif 'site' in request.json:
            # We have a project. Get list of items
            if 'id_site' not in request.json['site']:
                return gettext('Missing site ID'), 400
            if 'sessiontypes' not in request.json['site']:
                return gettext('Missing session types'), 400
            id_site = request.json['site']['id_site']

            # Check if admin for that site
            if user_access.get_site_role(site_id=id_site) != 'admin':
                return gettext('Access denied'), 403

            # Get all current association for site
            current_session_types = TeraSessionTypeSite.get_sessions_types_for_site(site_id=id_site)
            current_session_types_ids = [st.id_session_type for st in current_session_types]
            received_st_ids = [st['id_session_type'] for st in request.json['site']['sessiontypes']]
            # Difference - we must delete devices not anymore in the list
            todel_ids = set(current_session_types_ids).difference(received_st_ids)
            # Also filter session types already there
            received_st_ids = set(received_st_ids).difference(current_session_types_ids)
            for sts_id in todel_ids:
                TeraSessionTypeSite.delete_with_ids(session_type_id=sts_id, site_id=id_site)
            # Build sites association to add
            json_sts = [{'id_session_type': sts_id, 'id_site': id_site} for sts_id in received_st_ids]
        elif 'session_type_site' in request.json:
            json_sts = request.json['session_type_site']
            if not isinstance(json_sts, list):
                json_sts = [json_sts]
        else:
            return '', 400

        # Validate if we have an id and access
        for json_st in json_sts:
            if 'id_session_type' not in json_st or 'id_site' not in json_st:
                return gettext('Badly formatted request'), 400

            if json_st['id_site'] not in accessible_sites_ids:
                return gettext('Forbidden'), 403

        for json_st in json_sts:
            if 'id_session_type_site' not in json_st:
                # Check if already exists
                st = TeraSessionTypeSite.get_session_type_site_for_session_type_and_site(site_id=
                                                                                         int(json_st['id_site']),
                                                                                         session_type_id=
                                                                                         int(json_st['id_session_type'])
                                                                                         )
                if st:
                    json_st['id_session_type_site'] = st.id_session_type_site
                else:
                    json_st['id_session_type_site'] = 0

            # Do the update!
            if int(json_st['id_session_type_site']) > 0:
                # Already existing
                try:
                    TeraSessionTypeSite.update(int(json_st['id_session_type_site']), json_st)
                except exc.SQLAlchemyError as e:
                    import sys
                    print(sys.exc_info())
                    self.module.logger.log_error(self.module.module_name,
                                                 UserQuerySessionTypeSites.__name__,
                                                 'post', 500, 'Database error', str(e))
                    return gettext('Database error'), 500
            else:
                try:
                    new_sts = TeraSessionTypeSite()
                    new_sts.from_json(json_st)
                    TeraSessionTypeSite.insert(new_sts)
                    # Update ID for further use
                    json_st['id_session_type_site'] = new_sts.id_session_type_site
                except exc.SQLAlchemyError as e:
                    import sys
                    print(sys.exc_info())
                    self.module.logger.log_error(self.module.module_name,
                                                 UserQuerySessionTypeSites.__name__,
                                                 'post', 500, 'Database error', str(e))
                    return gettext('Database error'), 500

        return json_sts

    @user_multi_auth.login_required
    @api.expect(delete_parser)
    @api.doc(description='Delete a specific session type-site association.',
             responses={200: 'Success',
                        403: 'Logged user can\'t delete association (no admin access to site)',
                        500: 'Session type - site association not found or database error.'})
    def delete(self):
        parser = delete_parser
        # current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        args = parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        session_type_site = TeraSessionTypeSite.get_session_type_site_by_id(id_todel)
        if not session_type_site:
            return gettext('Bad parameter'), 400

        accessible_sites = user_access.get_accessible_sites_ids(admin_only=True)
        if session_type_site.id_site not in accessible_sites:
            return gettext('Forbidden'), 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraSessionTypeSite.delete(id_todel=id_todel)
        except exc.SQLAlchemyError as e:
            import sys
            print(sys.exc_info())
            self.module.logger.log_error(self.module.module_name,
                                         UserQuerySessionTypeSites.__name__,
                                         'delete', 500, 'Database error', str(e))
            return gettext('Database error'), 500

        return '', 200

