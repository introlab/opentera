from flask_restx import Resource, inputs
from flask import request
from flask_mail import Message
from services.EmailService.FlaskModule import email_api_ns as api
from opentera.services.ServiceAccessManager import (ServiceAccessManager, current_user_client, current_login_type,
                                                    LoginType)
from flask_babel import gettext
from string import Template

import services.EmailService.Globals as Globals

# Parser definition(s)
post_parser = api.parser()
post_schema = api.schema_model('email', {'properties':
    { 'user_uuid': {'type': 'array',
                    'uniqueItems': True,
                    'items': {
                        'type': 'string',
                        'format': 'uuid'
                    }, 'description': 'Users UUID to send email to'},
      'participant_uuid': {'type': 'array',
                    'uniqueItems': True,
                    'items': {
                        'type': 'string',
                        'format': 'uuid'
                    }, 'description': 'Participants UUID to send email to'},
      'id_template': {'type': 'integer', 'description': 'Template id to format email'},
      'subject': {'type': 'string', 'default': '(No Subject)', 'description': "Email subject"},
      'body': {'type': 'string', 'description': 'Email body, if template is not used'},
      'body_variables': {'type': 'array',
                         'items' :{
                                'type': 'object',
                                'properties':
                                 {
                                     'name': {'type': 'string', 'description': 'Variable name'},
                                     'value': {'type': 'string', 'description': 'Variable value'}
                                 }
                             }, 'description': 'Variables to fill the template with'
                         }
    },
                                         'type': 'object', 'location': 'json'})


class QuerySendEmail(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Send email to specific user / participant',
             responses={200: 'Email queued for sending',
                        400: 'Invalid format',
                        401: 'Unauthorized login type',
                        403: 'No access to target senders'})
    @api.expect(post_schema)
    @ServiceAccessManager.token_required()
    def post(self):
        if current_login_type != LoginType.USER_LOGIN:
            return gettext('Only users can use this API.'), 401

        # Check if we have at least one participant or user uuid
        json_email = request.json

        user_emails = []
        participant_emails = []

        if 'user_uuid' in json_email:
            user_uuids = json_email['user_uuid']
            if not isinstance(user_uuids, list):
                user_uuids = [user_uuids]
            # Validate access to uuids
            for user_uuid in user_uuids:
                # Do query as user to check if it has access to that user or not
                if self.test:
                    response = Globals.service.get_from_opentera('/api/user/users',
                                                                 params={'user_uuid': user_uuid},
                                                                 token=current_user_client.user_token)
                else:
                    response = current_user_client.do_get_request_to_backend('/api/user/users?user_uuid=' + user_uuid)
                response_json = response.json()
                if response.status_code != 200 or not response_json:
                    return gettext('At least one user is not accessible'), 403

                if 'user_email' in response_json[0] and response_json[0]['user_email']:
                    user_emails.append(response_json[0]['user_email'])


        if 'participant_uuid' in json_email:
            participant_uuids = json_email['participant_uuid']
            if not isinstance(participant_uuids, list):
                participant_uuids = [participant_uuids]
            # Validate access to uuids
            for participant_uuid in participant_uuids:
                # Do query as user to check if it has access to that participant or not
                if self.test:
                    response = Globals.service.get_from_opentera('/api/user/participants',
                                                                 params={'participant_uuid': participant_uuid},
                                                                 token=current_user_client.user_token)
                else:
                    response = current_user_client.do_get_request_to_backend('/api/user/participants?participant_uuid=' +
                                                                             participant_uuid)
                response_json = response.json()

                if response.status_code != 200 or not response_json:
                    return gettext('At least one participant is not accessible'), 403

                if 'participant_email' in response_json[0] and response_json[0]['participant_email']:
                    participant_emails.append(response_json[0]['participant_email'])

        if not user_emails and not participant_emails:
            return gettext('Missing user and/or participant_uuid'), 400

        if 'id_template' in json_email and 'body' in json_email:
            return gettext('Can\'t specify both a template and an email body'), 400

        email_body = ''
        if 'id_template' in json_email:
            # TODO: Load template from db
            # TODO: Validate access to template
            pass
        elif 'body' in json_email:
            email_body = json_email['body']
        else:
            return gettext('Missing template ID or body text'), 400

        email_subject = gettext('(No subject)')
        if 'subject' in json_email:
            email_subject = json_email['subject']

        if 'body_variables' in json_email:
            # Replace variables in body text
            template = Template(email_body)
            email_body = template.safe_substitute(json_email['body_variables'])

        # Send email!
        sender_email = None
        if self.test:
            response = Globals.service.get_from_opentera('/api/user/users',
                                                         params={'user_uuid': current_user_client.user_uuid},
                                                         token=current_user_client.user_token)
            if response.status_code == 200:
                response_json = response.json()
                if response_json:
                    sender_email = (current_user_client.user_fullname, response_json[0]['user_email'])
        else:
            sender_email = (current_user_client.user_fullname, current_user_client.get_user_info()['user_email'])
        if not sender_email:
            return gettext('User doesn\'t have any email address set'), 400

        email = Message(subject=email_subject, html=email_body, recipients=user_emails + participant_emails,
                        sender=sender_email, reply_to=sender_email)
        try:
            self.module.mail_man.send(email)
        except ConnectionRefusedError:
            return gettext('Can\'t connect to SMTP server'), 503
        except Exception as e:
            return str(e), 500

        return 200