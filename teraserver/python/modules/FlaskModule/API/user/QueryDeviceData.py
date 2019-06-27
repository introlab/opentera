from flask import jsonify, session, request, send_file #send_from_directory
from flask_restful import Resource, reqparse, inputs
from modules.Globals import auth
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraDeviceData import TeraDeviceData
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc
from libtera.db.DBManager import DBManager
import tempfile
from shutil import copy2
import zipfile


class QueryDeviceData(Resource):

    def __init__(self, flaskModule=None):
        Resource.__init__(self)
        self.module = flaskModule

    @auth.login_required
    def get(self):
        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        user_access = DBManager.userAccess(current_user)

        parser = reqparse.RequestParser()
        parser.add_argument('id_device_data', type=int)
        parser.add_argument('id_device', type=int, help='id_device')
        parser.add_argument('id_session', type=int)
        parser.add_argument('download')

        args = parser.parse_args()

        datas = []
        # If we have no arguments, don't do anything!
        if not any(args.values()):
            return '', 500
        elif args['id_device']:
            if args['id_device'] not in user_access.get_accessible_devices_ids():
                return '', 403
            datas = TeraDeviceData.get_data_for_device(device_id=args['id_device'])
        elif args['id_session']:
            if not user_access.query_session(session_id=args['id_session']):
                return '', 403
            datas = TeraDeviceData.get_data_for_session(session_id=args['id_session'])
        elif args['id_device_data']:
            datas = [TeraDeviceData.get_data_by_id(args['id_device_data'])]
            if datas[0] is not None:
                if datas[0].id_device not in user_access.get_accessible_devices_ids():
                    return '', 403
                if not user_access.query_session(session_id=datas[0].id_session):
                    return '', 403

        if args['download'] is None:
            data_list = []
            for data in datas:
                if data is not None:
                    data_json = data.to_json()
                    data_list.append(data_json)

            return jsonify(data_list)
        else:
            if not datas:
                return '', 200
            # File transfer requested data
            # Create temporary files
            # TODO: Clean the temporary folder sometimes...
            tmp_dir = tempfile.mkstemp(prefix='tera_')
            src_dir = self.module.config.server_config['upload_path']
            for data in datas:
                copy2(src_dir + '/' + data.devicedata_uuid, tmp_dir + '/' + data.devicedata_original_filename)

            if len(datas) > 1:
                # Zip contents
                zfile = zipfile.ZipFile(tmp_dir + '/download.zip', mode='w')
                for data in datas:
                    zfile.write(tmp_dir + '/' + data.devicedata_original_filename,
                                arcname=data.devicedata_original_filename)
                zfile.close()
                filename = zfile.filename
            else:
                filename = tmp_dir + '/' + datas[0].devicedata_original_filename
            # return send_from_directory(tmp_dir.name, filename)
            return send_file(filename, as_attachment=True)
        
    @auth.login_required
    def post(self):
        # parser = reqparse.RequestParser()
        # parser.add_argument('device', type=str, location='json', help='Device to create / update', required=True)
        #
        # current_user = TeraUser.get_user_by_uuid(session['user_id'])
        # user_access = DBManager.userAccess(current_user)
        # # Using request.json instead of parser, since parser messes up the json!
        # json_device = request.json['device']
        #
        # # Validate if we have an id
        # if 'id_device' not in json_device:
        #     return '', 400
        #
        # # Check if current user can modify the posted device
        # if json_device['id_site'] not in user_access.get_accessible_sites_ids(admin_only=True) and \
        #         json_device['id_site'] > 0:
        #     return '', 403
        #
        # # Devices without a site can only be modified by super admins
        # if json_device['id_site'] == 0:
        #     if not current_user.user_superadmin:
        #         return '', 403
        #     json_device['id_site'] = None
        #
        # # Do the update!
        # if json_device['id_device'] > 0:
        #     # Already existing
        #     try:
        #         TeraDevice.update_device(json_device['id_device'], json_device)
        #     except exc.SQLAlchemyError:
        #         import sys
        #         print(sys.exc_info())
        #         return '', 500
        # else:
        #     # New
        #     try:
        #         new_device = TeraDevice()
        #         new_device.from_json(json_device)
        #         TeraDevice.insert_device(new_device)
        #         # Update ID for further use
        #         json_device['id_device'] = new_device.id_device
        #     except exc.SQLAlchemyError:
        #         import sys
        #         print(sys.exc_info())
        #         return '', 500
        #
        # # TODO: Publish update to everyone who is subscribed to devices update...
        # update_device = TeraDevice.get_device_by_id(json_device['id_device'])
        #
        # return jsonify([update_device.to_json()])

        return '', 501

    @auth.login_required
    def delete(self):
        # parser = reqparse.RequestParser()
        # parser.add_argument('id', type=int, help='ID to delete', required=True)
        # current_user = TeraUser.get_user_by_uuid(session['user_id'])
        # user_access = DBManager.userAccess(current_user)
        #
        # args = parser.parse_args()
        # id_todel = args['id']
        #
        # # Check if current user can delete
        # if user_access.query_device_by_id(device_id=id_todel) is None:
        #     return '', 403
        #
        # # If we are here, we are allowed to delete. Do so.
        # try:
        #     TeraDevice.delete_device(id_device=id_todel)
        # except exc.SQLAlchemyError:
        #     import sys
        #     print(sys.exc_info())
        #     return 'Database error', 500
        #
        # return '', 200
        return '', 501
