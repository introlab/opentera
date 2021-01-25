# from flask import jsonify, session, send_file #send_from_directory
# from flask_restx import Resource, inputs
# from flask_babel import gettext
# from modules.LoginModule.LoginModule import user_multi_auth
# from modules.FlaskModule.FlaskModule import user_api_ns as api
# from opentera.db.models.TeraUser import TeraUser
# from opentera.db.models.TeraDeviceData import TeraDeviceData
# from sqlalchemy import exc
# from modules.DatabaseModule.DBManager import DBManager
# import zipfile
# from io import BytesIO
# from slugify import slugify
#
# # Parser definition(s)
# get_parser = api.parser()
# get_parser.add_argument('id_device_data', type=int, help='Specific ID of device data to request data.')
# get_parser.add_argument('id_device', type=int, help='ID of the device from which to request all data')
# get_parser.add_argument('id_session', type=int, help='ID of session from which to request all data')
# get_parser.add_argument('id_participant', type=int, help='ID of participant from which to request all data')
# get_parser.add_argument('download', type=inputs.boolean,
#                         help='If this flag is set, data will be downloaded instead of queried. '
#                         'In the case there\'s multiple files in the dataset, data will be '
#                         'zipped before the download process begins')
#
# delete_parser = api.parser()
# delete_parser.add_argument('id', type=int, help='Specific device data ID to delete', required=True)
#
#
# class UserQueryDeviceData(Resource):
#
#     def __init__(self, _api, *args, **kwargs):
#         Resource.__init__(self, _api, *args, **kwargs)
#         self.module = kwargs.get('flaskModule', None)
#
#     @user_multi_auth.login_required
#     @api.expect(get_parser)
#     @api.doc(description='Get device data information. Optionaly download the data. '
#                          'Only one of the ID parameter is supported at once',
#              responses={200: 'Success - returns list of datas or a downloadable file, if \'download\' parameter is '
#                              'specified',
#                         500: 'Required parameter is missing',
#                         403: 'Logged user doesn\'t have permission to access the requested data'})
#     def get(self):
#         current_user = TeraUser.get_user_by_uuid(session['_user_id'])
#         user_access = DBManager.userAccess(current_user)
#
#         args = get_parser.parse_args()
#
#         datas = []
#         # If we have no arguments, don't do anything!
#         if not any(args.values()):
#             return '', 500
#         elif args['id_device']:
#             if args['id_device'] not in user_access.get_accessible_devices_ids():
#                 return gettext('Device access denied'), 403
#             datas = TeraDeviceData.get_data_for_device(device_id=args['id_device'])
#         elif args['id_session']:
#             if not user_access.query_session(session_id=args['id_session']):
#                 return gettext('Session access denied'), 403
#             datas = TeraDeviceData.get_data_for_session(session_id=args['id_session'])
#         elif args['id_participant']:
#             if args['id_participant'] not in user_access.get_accessible_participants_ids():
#                 return gettext('Participant access denied'), 403
#             datas = TeraDeviceData.get_data_for_participant(part_id=args['id_participant'])
#         elif args['id_device_data']:
#             datas = [TeraDeviceData.get_data_by_id(args['id_device_data'])]
#             if datas[0] is not None:
#                 if datas[0].id_device not in user_access.get_accessible_devices_ids():
#                     return gettext('Permission denied'), 403
#                 if not user_access.query_session(session_id=datas[0].id_session):
#                     return gettext('Permission denied'), 403
#
#         if args['download'] is None:
#             data_list = []
#             for data in datas:
#                 if data is not None:
#                     data_json = data.to_json()
#                     data_json['device_name'] = data.devicedata_device.device_name
#                     data_list.append(data_json)
#
#             return jsonify(data_list)
#         else:
#             if not datas:
#                 return '', 200
#             # File transfer requested data
#             src_dir = self.module.config.server_config['upload_path']
#
#             if len(datas) > 1:
#                 # Zip contents
#                 # TODO: Check for large files VS available memory?
#                 zip_ram = BytesIO()
#                 zfile = zipfile.ZipFile(zip_ram, compression=zipfile.ZIP_DEFLATED, mode='w')
#
#                 for data in datas:
#                     archive_name = slugify(data.devicedata_session.session_name) + '/' + \
#                                    data.devicedata_original_filename
#                     zfile.write(src_dir + '/' + str(data.devicedata_uuid), arcname=archive_name)
#                 zfile.close()
#                 zip_ram.seek(0)
#
#                 file_name = 'download'
#                 if args['id_session']:
#                     file_name = slugify(data.devicedata_session.session_name)
#                 elif args['id_participant']:
#                     from opentera.db.models.TeraParticipant import TeraParticipant
#                     file_name = slugify(TeraParticipant.get_participant_by_id(part_id=args['id_participant'])
#                                         .participant_name)
#
#                 response = send_file(zip_ram, as_attachment=True, attachment_filename=file_name + '.zip',
#                                      mimetype='application/octet-stream')
#                 # response.headers.extend({
#                 #   'Content-Length': zip_ram.getbuffer().nbytes
#                 # })
#                 return response
#             else:
#                 # filename = tmp_dir + '/' + datas[0].devicedata_original_filename
#                 filename = datas[0].devicedata_original_filename
#                 return send_file(src_dir + '/' + str(datas[0].devicedata_uuid), as_attachment=True,
#                                  attachment_filename=filename)
#
#     # @user_multi_auth.login_required
#     # def post(self):
#     #     parser = reqparse.RequestParser()
#     #     parser.add_argument('device_data', type=str, location='json', help='Device to create / update', required=True)
#     #     #
#     #     # current_user = TeraUser.get_user_by_uuid(session['_user_id'])
#     #     # user_access = DBManager.userAccess(current_user)
#     #     # # Using request.json instead of parser, since parser messes up the json!
#     #     # json_device = request.json['device']
#     #     #
#     #     # # Validate if we have an id
#     #     # if 'id_device' not in json_device:
#     #     #     return '', 400
#     #     #
#     #     # # Check if current user can modify the posted device
#     #     # if json_device['id_site'] not in user_access.get_accessible_sites_ids(admin_only=True) and \
#     #     #         json_device['id_site'] > 0:
#     #     #     return '', 403
#     #     #
#     #     # # Devices without a site can only be modified by super admins
#     #     # if json_device['id_site'] == 0:
#     #     #     if not current_user.user_superadmin:
#     #     #         return '', 403
#     #     #     json_device['id_site'] = None
#     #     #
#     #     # # Do the update!
#     #     # if json_device['id_device'] > 0:
#     #     #     # Already existing
#     #     #     try:
#     #     #         TeraDevice.update_device(json_device['id_device'], json_device)
#     #     #     except exc.SQLAlchemyError:
#     #     #         import sys
#     #     #         print(sys.exc_info())
#     #     #         return '', 500
#     #     # else:
#     #     #     # New
#     #     #     try:
#     #     #         new_device = TeraDevice()
#     #     #         new_device.from_json(json_device)
#     #     #         TeraDevice.insert_device(new_device)
#     #     #         # Update ID for further use
#     #     #         json_device['id_device'] = new_device.id_device
#     #     #     except exc.SQLAlchemyError:
#     #     #         import sys
#     #     #         print(sys.exc_info())
#     #     #         return '', 500
#     #     #
#     #     # # TODO: Publish update to everyone who is subscribed to devices update...
#     #     # update_device = TeraDevice.get_device_by_id(json_device['id_device'])
#     #     #
#     #     # return jsonify([update_device.to_json()])
#     #
#     #     return '', 501
#
#     @user_multi_auth.login_required
#     @api.doc(description='Delete device data, including all related files.',
#              responses={200: 'Success - device data and all related files deleted',
#                         500: 'Database or file deletion error occurred',
#                         403: 'Logged user doesn\'t have permission to delete the requested data'})
#     @api.expect(delete_parser)
#     def delete(self):
#         parser = delete_parser
#         current_user = TeraUser.get_user_by_uuid(session['_user_id'])
#         user_access = DBManager.userAccess(current_user)
#
#         args = parser.parse_args()
#         id_todel = args['id']
#
#         # Get data in itself to validate we can delete it
#         data = TeraDeviceData.get_data_by_id(id_todel)
#
#         # Check if current user can delete
#         if data.id_device not in user_access.get_accessible_devices_ids(admin_only=True):
#             return gettext('Device access denied'), 403
#
#         # If we are here, we are allowed to delete. Do so.
#         try:
#             data.delete()
#         except exc.SQLAlchemyError:
#             import sys
#             print(sys.exc_info())
#             return gettext('Database error'), 500
#
#         return '', 200
#
