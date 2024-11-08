from services.EmailService.API.EmailResource import EmailResource
from flask_babel import gettext

from services.EmailService.FlaskModule import email_api_ns as api
from opentera.services.ServiceAccessManager import (ServiceAccessManager, current_user_client, current_login_type,
                                                    LoginType)
from opentera.services.TeraUserClient import TeraUserClient
from services.EmailService.libemailservice.db.models.EmailTemplate import EmailTemplate
import services.EmailService.Globals as Globals


# Parser definition(s)
# GET
get_parser = api.parser()
get_parser.add_argument('id_template', type=int, help='Specific template ID to query')
get_parser.add_argument('key', type=str, help='Specific email template key to query')
get_parser.add_argument('id_site', type=int, help='Specific site ID to query templates for')
get_parser.add_argument('id_project', type=int, help='Specific project ID to query templates for')
get_parser.add_argument('lang', type=str, default='en', help='Language code (ex. \'en\' to get template')


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
