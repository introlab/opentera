from flask_restx import Resource
from flask import request
from werkzeug.exceptions import UnsupportedMediaType, BadRequest
from flask_babel import gettext
from jsonschema import validate, ValidationError
from jsonschema.exceptions import SchemaError
from sqlalchemy import exc
from modules.LoginModule.LoginModule import LoginModule, current_service
from modules.FlaskModule.FlaskModule import service_api_ns as api
from modules.DatabaseModule.DBManager import DBManager
from opentera.db.models.TeraSessionTypeProject import TeraSessionTypeProject
from opentera.db.models.TeraSessionTypeSite import TeraSessionTypeSite
from opentera.db.models.TeraSessionType import TeraSessionType
from opentera.db.models.TeraParticipant import TeraParticipant

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_site', type=int, help='ID of the site to query session types for')
get_parser.add_argument('id_project', type=int, help='ID of the project to query session types for')
get_parser.add_argument('id_participant', type=int, help='ID of the participant to query types for')
get_parser.add_argument('id_session_type', type=int, help='ID of the session type to query')

post_parser = api.parser()
'''
    id_service = Column(Integer, ForeignKey('t_services.id_service', ondelete='cascade'), nullable=True)
    session_type_name = Column(String, nullable=False, unique=False)
    session_type_online = Column(Boolean, nullable=False)
    session_type_config = Column(String, nullable=True)
    session_type_color = Column(String(7), nullable=False)
    session_type_category = Column(Integer, nullable=False)
'''
post_schema = api.schema_model(name='service_session_type_schema', schema={
        'properties' : {
            'service_session_type' : {
                'properties': {
                    'id_sites': {'type': 'array', 'items': {'type': 'integer'}, 'default': []},
                    'id_projects': {'type': 'array', 'items': {'type': 'integer'}, 'default': []},
                    'id_participants': {'type': 'array', 'items': {'type': 'integer'}, 'default': []},
                    'session_type': {
                        'type': 'object',
                        'properties': { 'id_session_type': {'type': 'integer'},
                                        'id_service': {'type': 'integer'},
                                        'session_type_name': {'type': 'string'},
                                        'session_type_online': {'type': 'boolean'},
                                        'session_type_config': {'type': 'string'},
                                        'session_type_color': {'type': 'string'},
                                        'session_type_category': {'type': 'integer'}
                                       },
                        'required': ['id_session_type'],
                        'additionalProperties': False
                        }
                    },
                'type': 'object',
                'required': ['session_type'],
                'additionalProperties': False
            }
        },
        'type': 'object',
        'required': ['service_session_type'],
        'additionalProperties': False
    })

class ServiceQuerySessionTypes(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Return session types information for the current service',
             responses={200: 'Success',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Service doesn\'t have permission to access the requested data'},
             params={'token': 'Access token'})
    @api.expect(get_parser)
    @LoginModule.service_token_or_certificate_required
    def get(self):
        """
        Get session types associated to that service
        """
        args = get_parser.parse_args()
        service_access = DBManager.serviceAccess(current_service)

        session_types = []
        if args['id_site']:
            if args['id_site'] in service_access.get_accessibles_sites_ids():
                session_types = [st.session_type_site_session_type for st in
                                 TeraSessionTypeSite.get_sessions_types_for_site(args['id_site'])]
        elif args['id_project']:
            if args['id_project'] in service_access.get_accessible_projects_ids():
                session_types = [st.session_type_project_session_type for st in
                                 TeraSessionTypeProject.get_sessions_types_for_project(args['id_project'])]
        elif args['id_participant']:
            if args['id_participant'] in service_access.get_accessible_participants_ids():
                part_info = TeraParticipant.get_participant_by_id(args['id_participant'])
                session_types = [st.session_type_project_session_type for st in
                                 TeraSessionTypeProject.get_sessions_types_for_project(part_info.id_project)]
        elif args['id_session_type']:
            if args['id_session_type'] in service_access.get_accessible_sessions_types_ids():
                session_types = [TeraSessionType.get_session_type_by_id(args['id_session_type'])]
        else:
            session_types = service_access.get_accessible_sessions_types()

        return [st.to_json() for st in session_types]

    @api.doc(description='Manage session types information for the current service',
             responses={200: 'Success',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Service doesn\'t have permission to access the requested data'},
             params={'token': 'Access token'})
    @api.expect(post_schema)
    @LoginModule.service_token_or_certificate_required
    def post(self):
        """
        Manage session types associated to that service with sites, projects, participants.
        """
        # Create session from db
        db_session = TeraSessionType.db().session

        try:
            # Validate schema first
            post_schema.validate(request.json)
            service_access = DBManager.serviceAccess(current_service)

            # Get data structures
            service_session_type_info = request.json['service_session_type']
            session_type_info = service_session_type_info['session_type']

            # STEP 1) Verify access before doing anything
            if ('id_sites' in service_session_type_info
                    and type(service_session_type_info['id_sites']) is list):
                accessible_sites = service_access.get_accessibles_sites_ids()
                for id_site in service_session_type_info['id_sites']:
                    if id_site not in accessible_sites:
                        return gettext('Service doesn\'t have access to all listed sites'), 403
            if ('id_projects' in service_session_type_info
                    and type(service_session_type_info['id_projects']) is list):
                accessible_projects = service_access.get_accessible_projects_ids()
                for id_project in service_session_type_info['id_projects']:
                    if id_project not in accessible_projects:
                        return gettext('Service doesn\'t have access to all listed projects'), 403
            if ('id_participants' in service_session_type_info
                    and type(service_session_type_info['id_participants']) is list):
                accessible_participants = service_access.get_accessible_participants_ids()
                for id_participant in service_session_type_info['id_participants']:
                    if id_participant not in accessible_participants:
                        return gettext('Service doesn\'t have access to all listed participants'), 403

            # STEP 2) Handle session type
            if session_type_info['id_session_type'] == 0:
                # New session type
                session_type = TeraSessionType()
                session_type.from_json(session_type_info)
                session_type.id_session_type = None
                # Make sure id_service is set to the current service
                session_type.id_service = current_service.id_service
                # Add object to be commited
                db_session.add(session_type)
            else:
                if session_type_info['id_session_type'] not in service_access.get_accessible_sessions_types_ids():
                    return gettext('Service doesn\'t have access to this session type'), 403

                session_type = TeraSessionType.get_session_type_by_id(session_type_info['id_session_type'])
                if session_type is None:
                    return gettext('Session type not found'), 404

            # STEP 3) Handle sites
            if 'id_sites' in service_session_type_info and type(service_session_type_info['id_sites']) is list:
                # Permissions already verified at step 1
                for id_site in service_session_type_info['id_sites']:
                    # Adding new relation session_type - site
                    session_type_site = TeraSessionTypeSite()
                    session_type_site.session_type_site_session_type = session_type
                    session_type_site.id_site = id_site
                    # Add object to be commited
                    db_session.add(session_type_site)

            # STEP 4) Handle projects
            if 'id_projects' in service_session_type_info and type(service_session_type_info['id_projects']) is list:
                # Permissions already verified at step 1
                for id_project in service_session_type_info['id_projects']:
                    session_type_project = TeraSessionTypeProject()
                    session_type_project.session_type_project_session_type = session_type
                    session_type_project.id_project = id_project
                    # Add object to be commited
                    db_session.add(session_type_project)

            # STEP 5) Handle participants
            if 'id_participants' in service_session_type_info and type(service_session_type_info['id_participants']) is list:
                # Permissions already verified at step 1
                for id_participant in service_session_type_info['id_participants']:
                    participant = TeraParticipant.get_participant_by_id(id_participant)
                    session_type_project = TeraSessionTypeProject()
                    session_type_project.session_type_project_session_type = session_type
                    session_type_project.id_project = participant.id_project
                    # Add object to be commited
                    db_session.add(session_type_project)

            # We are done, commit change
            db_session.commit()

        except KeyError as e:
            return gettext('Missing arguments'), 400
        except ValidationError as e:
            return gettext('Invalid arguments'), 400
        except SchemaError as e:
            return gettext('Invalid schema'), 400
        except UnsupportedMediaType as e:
            # If content type is not application/json
            return gettext('Unsupported Media Type'), 415
        except BadRequest as e:
            return gettext('Bad Request'), 400
        except exc.IntegrityError as e:
            db_session.rollback()
            return gettext('Integrity error'), 400
        except exc.SQLAlchemyError as e:
            # rollback
            db_session.rollback()
            return gettext('Database error'), 500


        # Return created session type
        return session_type.to_json(), 200