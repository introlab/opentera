from flask import jsonify, session, request
from flask_restx import Resource, reqparse, inputs
from modules.LoginModule.LoginModule import user_multi_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraSessionTypeDeviceType import TeraSessionTypeDeviceType
from modules.DatabaseModule.DBManager import DBManager
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc
from flask_babel import gettext

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_device_type', type=int, help='Device type ID to query associated session types from'
                        )
get_parser.add_argument('id_session_type', type=int, help='Session type ID to query associated device types from')
get_parser.add_argument('list', type=inputs.boolean, help='Flag that limits the returned data to minimal information '
                                                          '(ids only)')

# post_parser = reqparse.RequestParser()
# post_parser.add_argument('session_type_device_type', type=str, location='json',
#                          help='Device type - session type association to create / update', required=True)
post_schema = api.schema_model('user_session_type_device_type', {
    'properties': TeraSessionTypeDeviceType.get_json_schema(),
    'type': 'object',
    'location': 'json'})
delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='Specific device-type - session-type association ID to delete. '
                                                'Be careful: this is not the session-type or device-type ID, but the ID'
                                                ' of the association itself!', required=True)


class UserQuerySessionTypeDeviceType(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @user_multi_auth.login_required
    @api.expect(get_parser)
    @api.doc(description='Get devices types that are related to session types. Only one "ID" parameter required and '
                         'supported at once.',
             responses={200: 'Success - returns list of devices types - session types association',
                        400: 'Required parameter is missing (must have at least one id)',
                        500: 'Error when getting devices types - session types association'})
    def get(self):
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        parser = get_parser

        args = parser.parse_args()

        session_type_device_types = []
        # If we have no arguments, return error
        if not any(args.values()):
            return gettext('Arguments manquants'), 400

        if args['id_device_type']:
            session_type_device_types = user_access.query_session_types_for_device(
                device_type_id=args['id_device_type'])
        else:
            if args['id_session_type']:
                if args['id_session_type'] in user_access.get_accessible_session_types_ids():
                    session_type_device_types = TeraSessionTypeDeviceType.\
                        query_device_types_for_session_type(args['id_session_type'])
        try:
            stdt_list = []
            for stdt in session_type_device_types:
                json_stdt = stdt.to_json()
                if args['list'] is None:
                    json_stdt['session_type_name'] = stdt.session_type_device_session_type.session_type_name
                    json_stdt['device_type_name'] = gettext(stdt.session_type_device_device_type.get_name())
                stdt_list.append(json_stdt)

            return jsonify(stdt_list)

        except InvalidRequestError:
            return '', 500

    @user_multi_auth.login_required
    @api.expect(post_schema)
    @api.doc(description='Create/update session types - device type association.',
             responses={200: 'Success',
                        403: 'Logged user can\'t modify association (session type must be accessible from project '
                             'access)',
                        400: 'Badly formed JSON or missing fields(id_device_type or id_session_type) in the JSON body',
                        500: 'Internal error occured when saving association'})
    def post(self):
        # parser = post_parser

        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        # Using request.json instead of parser, since parser messes up the json!
        json_stdts = request.json['session_type_device_type']
        if not isinstance(json_stdts, list):
            json_stdts = [json_stdts]

        # Validate if we have an id
        for json_stdt in json_stdts:
            if 'id_session_type' not in json_stdt or 'id_device_type' not in json_stdt:
                return '', 400

            # Check if current user can modify the posted information
            if json_stdt['id_session_type'] not in user_access.get_accessible_session_types_ids(admin_only=True):
                return gettext('Accès refusé'), 403

            # Check if already exists
            stdt = TeraSessionTypeDeviceType.query_session_type_device_for_device_session_type(
                device_type_id=json_stdt['id_device_type'], session_type_id=json_stdt['id_session_type'])

            if stdt:
                json_stdt['id_session_type_device_type'] = stdt.id_session_type_device_type
            else:
                json_stdt['id_session_type_device_type'] = 0

            # Do the update!
            if json_stdt['id_session_type_device_type'] > 0:
                # Already existing
                try:
                    TeraSessionTypeDeviceType.update(json_stdt['id_session_type_device_type'], json_stdt)
                except exc.SQLAlchemyError:
                    import sys
                    print(sys.exc_info())
                    return '', 500
            else:
                try:
                    new_stdt = TeraSessionTypeDeviceType()
                    new_stdt.from_json(json_stdt)
                    TeraSessionTypeDeviceType.insert(new_stdt)
                    # Update ID for further use
                    json_stdt['id_session_type_device_type'] = new_stdt.id_session_type_device_type
                except exc.SQLAlchemyError:
                    import sys
                    print(sys.exc_info())
                    return '', 500

        # TODO: Publish update to everyone who is subscribed to devices update...
        update_stdt = json_stdts

        return jsonify(update_stdt)

    @user_multi_auth.login_required
    @api.expect(delete_parser)
    @api.doc(description='Delete a specific session-type - device-type association.',
             responses={200: 'Success',
                        403: 'Logged user can\'t delete association (no access to device-type or session-type)',
                        500: 'Association not found or database error.'})
    def delete(self):
        parser = delete_parser
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        args = parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        stdt = TeraSessionTypeDeviceType.get_session_type_device_type_by_id(id_todel)
        if not stdt:
            return gettext('Non-trouvé'), 500

        if stdt.id_session_type not in user_access.get_accessible_session_types_ids(admin_only=True):
            return gettext('Accès refusé'), 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraSessionTypeDeviceType.delete(id_todel=id_todel)
        except exc.SQLAlchemyError:
            import sys
            print(sys.exc_info())
            return gettext('Erreur base de données'), 500

        return '', 200