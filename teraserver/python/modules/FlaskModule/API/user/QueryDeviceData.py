from flask import jsonify, session, request, send_file #send_from_directory
from flask_restful import Resource, reqparse, inputs
from modules.Globals import auth
from modules.FlaskModule.FlaskModule import flask_app
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraDeviceData import TeraDeviceData
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc
from libtera.db.DBManager import DBManager
import zipfile
from io import BytesIO
from slugify import slugify


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
        parser.add_argument('id_participant', type=int)
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
        elif args['id_participant']:
            if args['id_participant'] not in user_access.get_accessible_participants_ids():
                return '', 403
            datas = TeraDeviceData.get_data_for_participant(part_id=args['id_participant'])
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
                    data_json['device_name'] = data.devicedata_device.device_name
                    data_list.append(data_json)

            return jsonify(data_list)
        else:
            if not datas:
                return '', 200
            # File transfer requested data
            src_dir = self.module.config.server_config['upload_path']

            if len(datas) > 1:
                # Zip contents
                # TODO: Check for large files VS available memory?
                zip_ram = BytesIO()
                zfile = zipfile.ZipFile(zip_ram, compression=zipfile.ZIP_LZMA, mode='w')

                for data in datas:
                    archive_name = slugify(data.devicedata_session.session_name) + '/' + \
                                   data.devicedata_original_filename
                    zfile.write(src_dir + '/' + str(data.devicedata_uuid), arcname=archive_name)
                zfile.close()
                zip_ram.seek(0)

                file_name = 'download'
                if args['id_session']:
                    file_name = slugify(data.devicedata_session.session_name)
                elif args['id_participant']:
                    from libtera.db.models.TeraParticipant import TeraParticipant
                    file_name = slugify(TeraParticipant.get_participant_by_id(part_id=args['id_participant'])
                                        .participant_name)

                response = send_file(zip_ram, as_attachment=True, attachment_filename=file_name + '.zip',
                                     mimetype='application/octet-stream')
                response.headers.extend({
                  'Content-Length': zip_ram.getbuffer().nbytes
                })
                return response
            else:
                # filename = tmp_dir + '/' + datas[0].devicedata_original_filename
                filename = datas[0].devicedata_original_filename
                return send_file(src_dir + '/' + str(datas[0].devicedata_uuid), as_attachment=True,
                                 attachment_filename=filename)

    @auth.login_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('device_data', type=str, location='json', help='Device to create / update', required=True)
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
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, help='ID to delete', required=True)
        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        user_access = DBManager.userAccess(current_user)

        args = parser.parse_args()
        id_todel = args['id']

        # Get data in itself to validate we can delete it
        data = TeraDeviceData.get_data_by_id(id_todel)

        # Check if current user can delete
        if data.id_device not in user_access.get_accessible_devices_ids(admin_only=True):
            return '', 403

        # If we are here, we are allowed to delete. Do so.
        try:
            data.delete()
        except exc.SQLAlchemyError:
            import sys
            print(sys.exc_info())
            return 'Database error', 500

        return '', 200

