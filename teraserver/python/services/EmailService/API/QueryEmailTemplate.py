from services.EmailService.API.EmailResource import EmailResource
from flask_babel import gettext
from flask import request
from sqlalchemy import exc

from services.EmailService.FlaskModule import email_api_ns as api
from opentera.services.ServiceAccessManager import (ServiceAccessManager, current_user_client, current_login_type,
                                                    LoginType)
from services.EmailService.libemailservice.db.models.EmailTemplate import EmailTemplate


# Parser definition(s)
# GET
get_parser = api.parser()
get_parser.add_argument('id_template', type=int, help='Specific template ID to query')
get_parser.add_argument('key', type=str, help='Specific email template key to query')
get_parser.add_argument('id_site', type=int, help='Specific site ID to query templates for')
get_parser.add_argument('id_project', type=int, help='Specific project ID to query templates for')
get_parser.add_argument('lang', type=str, default='en', help='Language code (ex. \'en\' to get template')

# POST
post_parser = api.parser()
post_schema = api.schema_model('email_template', {'properties': EmailTemplate.get_json_schema(),
                                                  'type': 'object',
                                                  'location': 'json'})
# DELETE
delete_parser = api.parser()
delete_parser.add_argument('id', type=int, help='Email Template ID to delete', required=True)

class QueryEmailTemplate(EmailResource):

    def __init__(self, _api, *args, **kwargs):
        EmailResource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    def _can_access_template(self, template: EmailTemplate, updating: bool) -> bool:
        if template.id_project:
            return self._verify_project_access(template.id_project, requires_admin=updating)

        if template.id_site:
            return self._verify_site_access(template.id_site, requires_admin=updating)

        # Global template
        if not updating:
            return True

        return current_user_client.user_superadmin

    @api.doc(description='Get email template. Can only use id_site or id_project, but not both.',
             responses={200: 'Success - returns template(s)',
                        400: 'Required parameter is missing',
                        403: 'Logged user doesn\'t have permission to access the requested data'})
    @api.expect(get_parser)
    @ServiceAccessManager.token_required()
    def get(self):
        if current_login_type != LoginType.USER_LOGIN:
            return gettext('Only users can use this API.'), 401

        args = get_parser.parse_args()

        if args['id_template']:
            template = EmailTemplate.get_template_by_id(args['id_template'])
            if template:
                if not self._can_access_template(template, False):
                    return gettext('Forbidden'), 403
                templates = [template.to_json()]
            else:
                return gettext('Forbidden'), 403

        elif args['key']:
            template = EmailTemplate.get_template_by_key(args['key'], project_id=args['id_project'],
                                                          site_id=args['id_site'], lang=args['lang'])
            if template:
                if not self._can_access_template(template, False):
                    return gettext('Forbidden'), 403
                templates = [template.to_json()]
            else:
                return []

        elif args['id_site']:
            if not self._verify_site_access(args['id_site']):
                return gettext('Forbidden'), 403
            templates = [template.to_json()
                         for template in EmailTemplate.get_templates_for_site(args['id_site'], lang=args['lang'])]
        elif args['id_project']:
            if not self._verify_project_access(args['id_project']):
                return gettext('Forbidden'), 403
            templates = [template.to_json()
                         for template in EmailTemplate.get_templates_for_project(args['id_project'], lang=args['lang'])]
        else:
            return gettext('Missing identifying parameter'), 400

        return templates

    @api.doc(description='Create / update email template. id_email_template must be set to "0" to create a new '
                         'one.',
             responses={200: 'Success',
                        403: 'Logged user can\'t create/update the specified email template',
                        400: 'Badly formed JSON or missing fields in the JSON body',
                        500: 'Internal error when saving session'})
    @api.expect(post_schema)
    @ServiceAccessManager.token_required()
    def post(self):
        if current_login_type != LoginType.USER_LOGIN:
            return gettext('Only users can use this API.'), 401

        if 'email_template' not in request.json:
            return gettext('Missing template'), 400

        json_template = request.json['email_template']

        if 'id_email_template' not in json_template:
            return gettext('Missing id_email_template'), 400

        if 'id_site' in json_template and 'id_project' in json_template:
            return gettext('Can\'t specify both site and project for template'), 400

        if json_template['id_email_template'] > 0:  # Existing template
            # Check if have access to updatable template
            update_template = EmailTemplate.get_template_by_id(json_template['id_email_template'])
            if not update_template:
                return gettext('Forbidden'), 403

            if not self._can_access_template(update_template, True):
                return gettext('Forbidden'), 403

            # Update template
            try:
                EmailTemplate.update(json_template['id_email_template'], json_template)
            except exc.SQLAlchemyError:
                import sys
                print(sys.exc_info())
                return gettext('Invalid or missing data'), 400
        else:  # New template
            try:
                # Check if we have access or not to template
                template = EmailTemplate()
                template.from_json(json_template)

                if not self._can_access_template(template, True):
                    return gettext('Forbidden'), 403

                missing_fields = EmailTemplate.validate_required_fields(json_data=json_template)
                if missing_fields:
                    return gettext('Missing fields') + ': ' + str([field for field in missing_fields]), 400

                update_template = EmailTemplate()
                update_template.from_json(json_template)
                EmailTemplate.insert(update_template)
                # Update ID for further use
                json_template['id_email_template'] = update_template.id_email_template
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                return gettext('Database error'), 500

        return update_template.to_json()

    @api.doc(description='Delete a specific email template',
             responses={200: 'Success',
                        403: 'Logged user can\'t delete email template',
                        500: 'Database error.'})
    @api.expect(delete_parser)
    @ServiceAccessManager.token_required()
    def delete(self):
        if current_login_type != LoginType.USER_LOGIN:
            return gettext('Only users can use this API.'), 401

        args = delete_parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        template: EmailTemplate = EmailTemplate.get_template_by_id(id_todel)
        if not template:
            return gettext('Forbidden'), 403

        if not self._can_access_template(template, True):
            return gettext('Forbidden'), 403
        # If we are here, we are allowed to delete. Do so.
        try:
            EmailTemplate.delete(id_todel=id_todel)
        except exc.SQLAlchemyError as e:
            import sys
            print(sys.exc_info())
            return gettext('Database error'), 500

        return '', 200