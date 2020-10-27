from flask import jsonify, session, request
from flask_restx import Resource, reqparse, inputs
from sqlalchemy import exc
from modules.LoginModule.LoginModule import user_multi_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraUserUserGroup import TeraUserUserGroup
from flask_babel import gettext
from modules.DatabaseModule.DBManager import DBManager

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_user_group', type=int, help='ID of the user group to query')
get_parser.add_argument('id_user', type=int, help='ID of the user to get all user groups')
get_parser.add_argument('list', type=inputs.boolean, help='Flag that limits the returned data to minimal information')
get_parser.add_argument('with_empty', type=inputs.boolean, help="Used with id_user, also returns users groups that the "
                                                                "user is not part of. Used with id_user_group, also "
                                                                "returns users not part of that user group.")

# post_parser = reqparse.RequestParser()
# post_parser.add_argument('user_group', type=str, location='json', help='User group to create / update', required=True)
post_schema = api.schema_model('user_user_group', {'properties': TeraUserUserGroup.get_json_schema(),
                                                   'type': 'object',
                                                   'location': 'json'})

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='User - User group relationship ID to delete', required=True)


class UserQueryUserUserGroups(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @user_multi_auth.login_required
    @api.expect(get_parser)
    @api.doc(description='Get user - user group information. At least one "id" field must be specified',
             responses={200: 'Success',
                        500: 'Database error'})
    def get(self):
        parser = get_parser

        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        args = parser.parse_args()

        user_access = DBManager.userAccess(current_user)

        user_user_groups = []

        if args['id_user_group']:
            user_user_groups = user_access.query_users_usergroups_for_usergroup(user_group_id=args['id_user_group'],
                                                                                include_other_users=args['with_empty'])

        elif args['id_user']:
            user_user_groups = user_access.query_users_usergroups_for_user(user_id=args['id_user'],
                                                                           include_other_user_groups=args['with_empty'])
        else:
            # No argument
            return gettext('At least one id must be specified'), 400

        user_user_groups_list = []
        if user_user_groups:
            for uug in user_user_groups:
                uug_json = uug.to_json(minimal=args['list'])

                if not args['list']:
                    if uug.id_user:
                        uug_json['user_fullname'] = uug.user_user_group_user.get_fullname()
                    else:
                        uug_json['user_fullname'] = None
                    if uug.id_user_group:
                        uug_json['user_group_name'] = uug.user_user_group_user_group.user_group_name
                    else:
                        uug_json['user_group_name'] = None
                user_user_groups_list.append(uug_json)
        return user_user_groups_list

    @user_multi_auth.login_required
    # @api.expect(post_parser)
    @api.expect(post_schema)
    @api.doc(description='Create / update user - user group relationship, creating it if it doesn\'t exist, updating it'
                         ' otherwise.',
             responses={200: 'Success',
                        403: 'Logged user can\'t create/update the specified user group',
                        400: 'Badly formed JSON or missing field(id_user_group) in the JSON body',
                        500: 'Internal error when saving user group'})
    def post(self):
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])

        user_access = DBManager.userAccess(current_user)

        # Using request.json instead of parser, since parser messes up the json!
        json_user_groups = request.json['user_user_group']

        if not isinstance(json_user_groups, list):
            json_user_groups = [json_user_groups]

        for json_user_group in json_user_groups:
            # Validate if we have every ids
            if 'id_user' not in json_user_group:
                return gettext('Missing id_user'), 400
            if 'id_user_group' not in json_user_group:
                return gettext('Missing id_user_group'), 400

            # Check if current user has admin right to the user and the user_group
            if json_user_group['id_user'] not in user_access.get_accessible_users_ids(admin_only=True):
                return gettext('No access to specified user'), 403
            if json_user_group['id_user_group'] not in user_access.get_accessible_users_groups_ids(admin_only=True):
                return gettext('No access to specified user group'), 403

            # Check if target user is super admin. If so, don't add!
            target_user = TeraUser.get_user_by_id(json_user_group['id_user'])
            if target_user.user_superadmin:
                return gettext('Super admins can\'t be associated to an user group'), 400

        for json_user_group in json_user_groups:
            # Check if the relationship already exists or not
            uug = TeraUserUserGroup.query_user_user_group_for_user_user_group(user_id=json_user_group['id_user'],
                                                                              user_group_id=
                                                                              json_user_group['id_user_group']
                                                                              )
            if uug:
                # Already existing user - user group relationship, just append the id
                json_user_group['id_user_user_group'] = uug.id_user_user_group
            else:
                # Creates a new relationship
                try:
                    new_uug = TeraUserUserGroup()
                    new_uug.from_json(json_user_group)
                    TeraUserUserGroup.insert(new_uug)
                    # Update ID User Group for further use
                    json_user_group['id_user_user_group'] = new_uug.id_user_user_group
                except exc.SQLAlchemyError as e:
                    import sys
                    print(sys.exc_info())
                    self.module.logger.log_error(self.module.module_name,
                                                 UserQueryUserUserGroups.__name__,
                                                 'post', 500, 'Database error', str(e))
                    return gettext('Database error'), 500

        return json_user_groups

    @user_multi_auth.login_required
    @api.expect(delete_parser)
    @api.doc(description='Delete a specific user - user group relationship',
             responses={200: 'Success',
                        403: 'Logged user can\'t delete user group (only a site admin that includes that user group in '
                             'their site can delete)',
                        500: 'Database error.'})
    def delete(self):
        parser = delete_parser
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        args = parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        uug = TeraUserUserGroup.get_user_user_group_by_id(id_todel)
        if not uug:
            return gettext('Can\'t delete specified relationship'), 400

        if uug.id_user not in user_access.get_accessible_users_ids(admin_only=True):
            return gettext('No access to relationship\'s user'), 403
        if uug.id_user_group not in user_access.get_accessible_users_groups_ids(admin_only=True):
            return gettext('No access to relationship\'s user group'), 403

        # If we are here, we are allowed to delete that relationship. Do so.
        try:
            TeraUserUserGroup.delete(id_todel=id_todel)
        except exc.SQLAlchemyError as e:
            import sys
            print(sys.exc_info())
            self.module.logger.log_error(self.module.module_name,
                                         UserQueryUserUserGroups.__name__,
                                         'delete', 500, 'Database error', str(e))
            return gettext('Database error'), 500

        return '', 200

