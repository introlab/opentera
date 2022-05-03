from flask import request
from flask_restx import Resource, reqparse, inputs
from modules.LoginModule.LoginModule import user_multi_auth, current_user
from modules.FlaskModule.FlaskModule import user_api_ns as api
from opentera.db.models.TeraTestType import TeraTestType
from opentera.db.models.TeraSite import TeraSite
from opentera.db.models.TeraTestTypeSite import TeraTestTypeSite
from modules.DatabaseModule.DBManager import DBManager
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc, inspect
from flask_babel import gettext

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_test_type', type=int, help='ID of the test type from which to request all associated '
                                                       'sites')
get_parser.add_argument('id_site', type=int, help='ID of the site from which to get all associated test types')
get_parser.add_argument('list', type=inputs.boolean, help='Flag that limits the returned data to minimal information '
                                                          '(ids only)')
get_parser.add_argument('with_test_types', type=inputs.boolean, help='Used with id_test_type. Also return test '
                                                                     'types that don\'t have any association with '
                                                                     'that site')
get_parser.add_argument('with_sites', type=inputs.boolean, help='Used with id_site. Also return site information '
                                                                'of the returned test types.')

post_schema = api.schema_model('user_test_type_site', {'properties': TeraTestTypeSite.get_json_schema(),
                                                       'type': 'object',
                                                       'location': 'json'})

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='Specific test type-site association ID to delete. Be careful: this'
                                                ' is not the test type or the site ID, but the ID of the '
                                                'association itself!', required=True)


class UserQueryTestTypeSites(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

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

        tts_sites = []
        # If we have no arguments, return error
        if not any(args.values()):
            return gettext('Missing arguments'), 400

        if args['id_test_type']:
            if args['id_test_type'] in user_access.get_accessible_test_types_ids():
                tts_sites = user_access.query_test_types_sites_for_session_type(test_type_id=args['id_test_type'],
                                                                                include_other_sites=args['with_sites'])
        elif args['id_site']:
            if args['id_site'] in user_access.get_accessible_sites_ids():
                tts_sites = user_access.query_test_types_sites_for_site(site_id=args['id_site'],
                                                                        include_other_test_types=args['with_test_types']
                                                                        )
        try:
            tts_list = []
            for tts in tts_sites:
                json_tts = tts.to_json()
                if args['list'] is None:
                    obj_type = inspect(tts)
                    if not obj_type.transient:
                        json_tts['test_type_name'] = tts.test_type_site_test_type.test_type_name
                        json_tts['site_name'] = tts.test_type_site_site.site_name
                    else:
                        # Temporary object, a not-committed object, result of listing sites not associated to a
                        # test type.
                        if tts.id_test_type:
                            tt: TeraTestType = TeraTestType.get_test_type_by_id(tts.id_test_type)
                            json_tts['test_type_name'] = tt.test_type_name
                        else:
                            json_tts['test_type_name'] = None
                        if tts.id_site:
                            json_tts['site_name'] = TeraSite.get_site_by_id(tts.id_site).site_name
                        else:
                            json_tts['site_name'] = None
                tts_list.append(json_tts)
            return tts_list

        except InvalidRequestError as e:
            self.module.logger.log_error(self.module.module_name,
                                         UserQueryTestTypeSites.__name__,
                                         'get', 500, 'InvalidRequestError', str(e))
            return gettext('Invalid request'), 500

    @user_multi_auth.login_required
    @api.expect(post_schema)
    @api.doc(description='Create/update test types associated with a site.',
             responses={200: 'Success',
                        403: 'Logged user can\'t modify association',
                        400: 'Badly formed JSON or missing fields(id_site or id_test_type) in the JSON body',
                        500: 'Internal error occured when saving device association'})
    def post(self):
        # parser = post_parser
        user_access = DBManager.userAccess(current_user)

        # Only super admins can change session type - site associations
        # if not current_user.user_superadmin:
        #     return gettext('Forbidden'), 403
        accessible_sites_ids = user_access.get_accessible_sites_ids(admin_only=True)
        if 'test_type' in request.json:
            # We have a test type. Get list of items
            if 'id_test_type' not in request.json['test_type']:
                return gettext('Missing id_test_type'), 400
            if 'sites' not in request.json['test_type']:
                return gettext('Missing sites'), 400
            id_test_type = request.json['test_type']['id_test_type']

            if id_test_type not in user_access.get_accessible_test_types_ids(admin_only=True):
                return gettext("Access denied"), 403

            # Get all current association for session type
            current_sites = TeraTestTypeSite.get_sites_for_test_type(test_type_id=id_test_type)
            current_sites_ids = [site.id_site for site in current_sites]
            received_sites_ids = [site['id_site'] for site in request.json['test_type']['sites']]
            # Difference - we must delete sites not anymore in the list
            todel_ids = set(current_sites_ids).difference(received_sites_ids)
            # Also filter sites already there
            received_sites_ids = set(received_sites_ids).difference(current_sites_ids)
            for site_id in todel_ids:
                if site_id in accessible_sites_ids:  # Don't remove from the list if not site admin for that site!
                    TeraTestTypeSite.delete_with_ids(test_type_id=id_test_type, site_id=site_id)
            # Build sites association to add
            json_tts = [{'id_test_type': id_test_type, 'id_site': site_id} for site_id in received_sites_ids]
        elif 'site' in request.json:
            # We have a project. Get list of items
            if 'id_site' not in request.json['site']:
                return gettext('Missing site ID'), 400
            if 'testtypes' not in request.json['site']:
                return gettext('Missing test types'), 400
            id_site = request.json['site']['id_site']

            # Check if admin for that site
            if user_access.get_site_role(site_id=id_site) != 'admin':
                return gettext('Access denied'), 403

            # Get all current association for site
            current_test_types = TeraTestTypeSite.get_tests_types_for_site(site_id=id_site)
            current_test_types_ids = [tt.id_test_type for tt in current_test_types]
            received_tt_ids = [st['id_test_type'] for st in request.json['site']['testtypes']]
            # Difference - we must delete devices not anymore in the list
            todel_ids = set(current_test_types_ids).difference(received_tt_ids)
            # Also filter types already there
            received_tt_ids = set(received_tt_ids).difference(current_test_types_ids)
            for tts_id in todel_ids:
                TeraTestTypeSite.delete_with_ids(test_type_id=tts_id, site_id=id_site)
            # Build sites association to add
            json_tts = [{'id_test_type': tts_id, 'id_site': id_site} for tts_id in received_tt_ids]
        elif 'test_type_site' in request.json:
            json_tts = request.json['test_type_site']
            if not isinstance(json_tts, list):
                json_tts = [json_tts]
        else:
            return '', 400

        # Validate if we have an id and access
        for json_tt in json_tts:
            if 'id_test_type' not in json_tt or 'id_site' not in json_tt:
                return gettext('Badly formatted request'), 400

            if json_tt['id_site'] not in accessible_sites_ids:
                return gettext('Forbidden'), 403

        for json_tt in json_tts:
            if 'id_test_type_site' not in json_tt:
                # Check if already exists
                tt = TeraTestTypeSite.get_test_type_site_for_test_type_and_site(site_id=int(json_tt['id_site']),
                                                                                test_type_id=int(json_tt['id_test_type']
                                                                                                 )
                                                                                )
                if tt:
                    json_tt['id_test_type_site'] = tt.id_test_type_site
                else:
                    json_tt['id_test_type_site'] = 0

            # Do the update!
            if int(json_tt['id_test_type_site']) > 0:
                # Already existing
                try:
                    TeraTestTypeSite.update(int(json_tt['id_test_type_site']), json_tt)
                except exc.SQLAlchemyError as e:
                    import sys
                    print(sys.exc_info())
                    self.module.logger.log_error(self.module.module_name,
                                                 UserQueryTestTypeSites.__name__,
                                                 'post', 500, 'Database error', str(e))
                    return gettext('Database error'), 500
            else:
                try:
                    new_tts = TeraTestTypeSite()
                    new_tts.from_json(json_tt)
                    TeraTestTypeSite.insert(new_tts)
                    # Update ID for further use
                    json_tt['id_test_type_site'] = new_tts.id_test_type_site
                except exc.SQLAlchemyError as e:
                    import sys
                    print(sys.exc_info())
                    self.module.logger.log_error(self.module.module_name,
                                                 UserQueryTestTypeSites.__name__,
                                                 'post', 500, 'Database error', str(e))
                    return gettext('Database error'), 500

        return json_tts

    @user_multi_auth.login_required
    @api.expect(delete_parser)
    @api.doc(description='Delete a specific test type-site association.',
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
        test_type_site = TeraTestTypeSite.get_test_type_site_by_id(id_todel)
        if not test_type_site:
            return gettext('Bad parameter'), 400

        accessible_sites = user_access.get_accessible_sites_ids(admin_only=True)
        if test_type_site.id_site not in accessible_sites:
            return gettext('Forbidden'), 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraTestTypeSite.delete(id_todel=id_todel)
        except exc.SQLAlchemyError as e:
            import sys
            print(sys.exc_info())
            self.module.logger.log_error(self.module.module_name,
                                         UserQueryTestTypeSites.__name__,
                                         'delete', 500, 'Database error', str(e))
            return gettext('Database error'), 500

        return '', 200
