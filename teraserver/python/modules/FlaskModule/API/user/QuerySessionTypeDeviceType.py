from flask import jsonify, session, request
from flask_restful import Resource, reqparse
from modules.Globals import auth
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraSessionTypeDeviceType import TeraSessionTypeDeviceType
from libtera.db.DBManager import DBManager
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc
from flask_babel import gettext


class QuerySessionTypeDeviceType(Resource):

    def __init__(self, flaskModule=None):
        Resource.__init__(self)
        self.module = flaskModule

    @auth.login_required
    def get(self):
        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        user_access = DBManager.userAccess(current_user)

        parser = reqparse.RequestParser()
        parser.add_argument('id_device_type', type=int)
        parser.add_argument('id_session_type', type=int)
        parser.add_argument('list', type=bool)

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
            return '', 400

    @auth.login_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('session_type_device_type', type=str, location='json',
                            help='Session type device type to create / update', required=True)

        current_user = TeraUser.get_user_by_uuid(session['user_id'])
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

    @auth.login_required
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, help='ID to delete', required=True)
        current_user = TeraUser.get_user_by_uuid(session['user_id'])
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
