import psycopg2
from requests import get, post
import pytz
from datetime import datetime

opentera_url = '127.0.0.1'
opentera_user = 'admin'
opentera_password = 'admin'
opentera_port = 40075
opentera_videorehab_service_id = None


def generate_password(length: int):
    import secrets
    import string

    password = ''
    for i in range(0, length):
        password = password + secrets.choice(string.ascii_uppercase + string.ascii_lowercase +
                                            string.digits + string.punctuation)
    return password


def _make_url(endpoint):
    return 'https://' + opentera_url + ':' + str(opentera_port) + endpoint


def query_opentera_videorehab_service_id():
    global opentera_videorehab_service_id
    if opentera_videorehab_service_id is None:
        url = _make_url('/api/user/services')
        params = {'key': 'VideoRehabService'}
        try:
            response = get(url=url, params=params, verify=False, auth=(opentera_user, opentera_password))
        except Exception as e:
            print(e)
            return

        if response.status_code == 200:
            if response.json():
                service = response.json().pop()
                if service:
                    opentera_videorehab_service_id = service['id_service']
                    return
        else:
            import inspect
            print('Error in ' + inspect.currentframe().f_code.co_name + ': Code=' + str(response.status_code) +
                  ', Message=' + response.content.decode())
            return


def create_project(name: str, site_id: int):

    url = _make_url('/api/user/projects')

    # Check if project already exists for that site
    params = {'name': name, 'id_site': site_id}
    try:
        response = get(url=url, params=params, verify=False, auth=(opentera_user, opentera_password))
    except Exception as e:
        print(e)
        return None

    if response.status_code == 200:
        if response.json():
            project = response.json().pop()
            if project:
                print("---- Project '" + name + "' already existing for site, skipping creation.")
                return project
    else:
        import inspect
        print('Error in ' + inspect.currentframe().f_code.co_name + ': Code=' + str(response.status_code) +
              ', Message=' + response.content.decode())
        return None

    # Create project
    project_dict = {'project': {'id_project': 0,
                                'project_name': name,
                                'id_site': site_id}
                    }
    try:
        response = post(url=url, json=project_dict, verify=False, auth=(opentera_user, opentera_password))
    except Exception as e:
        print(e)
        return {}

    if response.status_code == 200:
        return response.json().pop()
    import inspect
    print('Error in ' + inspect.currentframe().f_code.co_name + ': Code=' + str(response.status_code) + ', Message=' +
          response.content.decode())
    return {}


def create_project_usergroup(project_name: str, project_id: int, site_id: int):

    url = _make_url('/api/user/usergroups')
    usergroup_name = project_name + ' - Administrateurs'

    # Check if project already exists for that site
    params = {'id_site': site_id}
    try:
        response = get(url=url, params=params, verify=False, auth=(opentera_user, opentera_password))
    except Exception as e:
        print(e)
        return None

    if response.status_code == 200:
        if response.json():
            for group in response.json():
                if group['user_group_name'] == usergroup_name:
                    print("---- Usergroup '" + usergroup_name + "' already existing for site, skipping creation.")
                    return group
    else:
        import inspect
        print('Error in ' + inspect.currentframe().f_code.co_name + ': Code=' + str(response.status_code) +
              ', Message=' + response.content.decode())
        return None

    # Create group
    ugroup_dict = {'user_group': {'id_user_group': 0,
                                  'user_group_name': usergroup_name,
                                  'user_group_projects_access': [{
                                      'id_project': project_id,
                                      'project_access_role': 'admin'}]
                                  }
                   }
    try:
        response = post(url=url, json=ugroup_dict, verify=False, auth=(opentera_user, opentera_password))
    except Exception as e:
        print(e)
        return {}

    if response.status_code == 200:
        return response.json().pop()
    import inspect
    print('Error in ' + inspect.currentframe().f_code.co_name + ': Code=' + str(response.status_code) + ', Message=' +
          response.content.decode())
    return {}


def create_user(user_dict: dict):

    url = _make_url('/api/user/users')

    # Check if user already exists
    params = {'username': user_dict['user_username']}
    try:
        response = get(url=url, params=params, verify=False, auth=(opentera_user, opentera_password))
    except Exception as e:
        print(e)
        return None

    if response.status_code == 200:
        if response.json():
            reply_user = response.json().pop()
            if reply_user:
                print("---- User '" + user_dict['user_username'] + "' already existing, skipping creation.")
                return reply_user
    else:
        import inspect
        print('Error in ' + inspect.currentframe().f_code.co_name + ': Code=' + str(response.status_code) +
              ', Message=' + response.content.decode())
        return None

    # Create user
    user_dict = {'user': user_dict}
    try:
        response = post(url=url, json=user_dict, verify=False, auth=(opentera_user, opentera_password))
    except Exception as e:
        print(e)
        return {}

    if response.status_code == 200:
        return response.json().pop()
    import inspect
    print('Error in ' + inspect.currentframe().f_code.co_name + ': Code=' + str(response.status_code) + ', Message=' +
          response.content.decode())
    return {}


def create_session_type(name: str, online: bool, color: str, id_project: int):

    url = _make_url('/api/user/sessiontypes')

    # Check if sessiontype already exists
    # params = {'id_project': id_project}
    params = []
    try:
        response = get(url=url, params=params, verify=False, auth=(opentera_user, opentera_password))
    except Exception as e:
        print(e)
        return None

    if response.status_code == 200:
        if response.json():
            for ses_type in response.json():
                if ses_type['session_type_name'] == name \
                        and ses_type['session_type_service_key'] == 'VideoRehabService':
                    print("---- Session type '" + name + "' already existing, skipping creation.")

                    # Check if already assigned to the project
                    url = _make_url('/api/user/sessiontypeprojects')
                    params = {'id_session_type': ses_type['id_session_type']}
                    try:
                        response = get(url=url, params=params, verify=False, auth=(opentera_user, opentera_password))
                    except Exception as e:
                        print(e)
                        return None

                    if response.status_code == 200:
                        if response.json():
                            for ses_type_proj in response.json():
                                if ses_type_proj['id_project'] == id_project:
                                    # Ok, association already there!
                                    return ses_type

                        # Here, we have no association... create it!
                        params = {'session_type_project': {'id_project': id_project,
                                  'id_session_type': ses_type['id_session_type'], 'id_session_type_project': 0}
                                  }
                        try:
                            response = post(url=url, json=params, verify=False,
                                            auth=(opentera_user, opentera_password))
                        except Exception as e:
                            print(e)
                            return {}
                        if response.status_code == 200:
                            return ses_type

                        return {}
    else:
        import inspect
        print('Error in ' + inspect.currentframe().f_code.co_name + ': Code=' + str(response.status_code) +
              ', Message=' + response.content.decode())
        return None

    # Query VideoRehabService id
    query_opentera_videorehab_service_id()

    # Create session_type
    project_dict = {'session_type': {'id_session_type': 0,
                                     'id_service': opentera_videorehab_service_id,
                                     'session_type_category': 1,    # Service category
                                     'session_type_color': color,
                                     'session_type_name': name,
                                     'session_type_online': online,
                                     'session_type_projects': [{'id_project': id_project}]}
                    }
    try:
        response = post(url=url, json=project_dict, verify=False, auth=(opentera_user, opentera_password))
    except Exception as e:
        print(e)
        return {}

    if response.status_code == 200:
        return response.json().pop()
    import inspect
    print('Error in ' + inspect.currentframe().f_code.co_name + ': Code=' + str(response.status_code) + ', Message=' +
          response.content.decode())
    return {}


def create_participant(name: str, active: bool, project_id: int):

    url = _make_url('/api/user/participants')

    # Check if project already exists for that site
    params = {'id_project': project_id}
    try:
        response = get(url=url, params=params, verify=False, auth=(opentera_user, opentera_password))
    except Exception as e:
        print(e)
        return None

    if response.status_code == 200:
        if response.json():
            for part in response.json():
                if part['participant_name'] == name:
                    print("---- Participant '" + name + "' already existing, skipping creation.")
                    return part
    else:
        import inspect
        print('Error in ' + inspect.currentframe().f_code.co_name + ': Code=' + str(response.status_code) +
              ', Message=' + response.content.decode())
        return None

    # Create participant
    part_dict = {'participant': {'id_participant': 0,
                                 'id_project': project_id,
                                 'participant_name': name,
                                 'participant_token_enabled': active,
                                 'participant_enabled': active
                                 }
                 }
    try:
        response = post(url=url, json=part_dict, verify=False, auth=(opentera_user, opentera_password))
    except Exception as e:
        print(e)
        return {}

    if response.status_code == 200:
        return response.json().pop()
    import inspect
    print('Error in ' + inspect.currentframe().f_code.co_name + ': Code=' + str(response.status_code) + ', Message=' +
          response.content.decode())
    return {}


def create_session(session_dict: dict, participant_id: int):

    url = _make_url('/api/user/sessions')

    # Check if session already exists
    params = {'id_participant': participant_id}
    try:
        response = get(url=url, params=params, verify=False, auth=(opentera_user, opentera_password))
    except Exception as e:
        print(e)
        return None

    if response.status_code == 200:
        if response.json():
            if response.json():
                for ses in response.json():
                    if datetime.fromisoformat(ses['session_start_datetime']) \
                            == datetime.fromisoformat(session_dict['session_start_datetime']):
                        print("---- Session '" + session_dict['session_name'] + "' already existing, "
                                                                                "skipping creation.")
                        return ses
    else:
        import inspect
        print('Error in ' + inspect.currentframe().f_code.co_name + ': Code=' + str(response.status_code) +
              ', Message=' + response.content.decode())
        return None

    # Create session
    session_dict['session_participants_ids'] = [participant_id]
    session_dict = {'session': session_dict}
    try:
        response = post(url=url, json=session_dict, verify=False, auth=(opentera_user, opentera_password))
    except Exception as e:
        print(e)
        return {}

    if response.status_code == 200:
        return response.json().pop()
    import inspect
    print('Error in ' + inspect.currentframe().f_code.co_name + ': Code=' + str(response.status_code) + ', Message=' +
          response.content.decode())
    return {}


def create_session_event(event_date: datetime, event_type: int, event_text: str, session_id: int):

    url = _make_url('/api/user/sessions/events')

    # Check if session already exists
    params = {'id_session': session_id}
    try:
        response = get(url=url, params=params, verify=False, auth=(opentera_user, opentera_password))
    except Exception as e:
        print(e)
        return None

    if response.status_code == 200:
        if response.json():
            if response.json():
                for event in response.json():
                    if datetime.fromisoformat(event['session_event_datetime']) == event_date:
                        print("---- Session Event '" + event_text + "' on " + event_date.isoformat() +
                              " already existing, skipping creation.")
                        return event
    else:
        import inspect
        print('Error in ' + inspect.currentframe().f_code.co_name + ': Code=' + str(response.status_code) +
              ', Message=' + response.content.decode())
        return None

    # Create session
    event_dict = {'session_event': {
        'id_session_event': 0,
        'id_session': session_id,
        'id_session_event_type': event_type,
        'session_event_context': 'TeraPlus',
        'session_event_datetime': event_date.isoformat(),
        'session_event_text': event_text
        }
    }
    try:
        response = post(url=url, json=event_dict, verify=False, auth=(opentera_user, opentera_password))
    except Exception as e:
        print(e)
        return {}

    if response.status_code == 200:
        return response.json().pop()
    import inspect
    print('Error in ' + inspect.currentframe().f_code.co_name + ': Code=' + str(response.status_code) + ', Message=' +
          response.content.decode())
    return {}


if __name__ == '__main__':

    # VARIABLES FOR THAT OPERATION
    opentera_id_site = 3    # OpenTera ID Site target
    teraplus_id_group = 34  # TeraPlus participant group to export as project in the selected site in OpenTera

    # Local variables
    teraplus_usergroups = []

    opentera_id_project = None
    opentera_id_user_group = None

    tera_open_session_type_map = {}
    tera_open_users_map = {}
    tera_open_participants_map = {}

    timezone = pytz.timezone('US/Eastern')

    # Open connections to TeraPlus databases
    tera_conn = None
    tera_cursor = None
    try:
        tera_conn = psycopg2.connect(host="localhost", database="tera", user="postgres", password="admin")
        tera_cursor = tera_conn.cursor()
    except psycopg2.DatabaseError as e:
        print("Unable to connect to Tera database:" + e.args[0])
        exit(1)

    exas_conn = None
    exas_cursor = None
    try:
        exas_conn = psycopg2.connect(host="localhost", database="ExAS", user="postgres", password="admin")
        exas_cursor = exas_conn.cursor()
    except psycopg2.DatabaseError as e:
        print("Unable to connect to ExAS database:" + e.args[0])
        exit(1)

    # Create project in the site based on the selected participant group
    query = "SELECT * FROM t_groups WHERE id_group=%s"
    try:
        tera_cursor.execute(query, [teraplus_id_group])
    except(Exception, psycopg2.Error) as error:
        print("SQL error: " + error.args[0])
        exit(1)

    teraplus_group = tera_cursor.fetchone()

    print("--> Creating project '" + teraplus_group[1] + "'...")
    # Call project API to create project and store returned id
    rval = create_project(teraplus_group[1], opentera_id_site)
    if not rval:
        exit(1)
    opentera_id_project = rval['id_project']

    # Create "admin" access for that project and store usergroup id
    rval = create_project_usergroup(teraplus_group[1], opentera_id_project, opentera_id_site)
    if not rval:
        exit(1)
    opentera_id_user_group = rval['id_user_group']

    # Query for users for the specified participant group
    print("** CREATING USERS **")
    query = "SELECT t_users.id_user, firstname, lastname, id_userid, t_users.id_usergroup FROM t_users " \
            "INNER JOIN t_users_groups ON t_users.id_usergroup = " \
            "t_users_groups.id_usergroup INNER JOIN t_user_group_access ON t_user_group_access.id_usergroup = " \
            "t_users_groups.id_usergroup WHERE id_group=%s and t_users.id_usergroup >1"
    try:
        tera_cursor.execute(query, [teraplus_id_group])
    except(Exception, psycopg2.Error) as error:
        print("SQL error: " + error.args[0])
        exit(1)

    users = tera_cursor.fetchall()
    for user in users:
        user_id = user[0]
        user_uuid = user[3]
        user_usergroup = user[4]
        if user_usergroup not in teraplus_usergroups:
            teraplus_usergroups.append(user_usergroup)

        # Query username (pseudo) from exas database
        query = "SELECT user_pseudo, user_email FROM t_account WHERE user_uuid=%s"
        try:
            exas_cursor.execute(query, [user_uuid])
        except(Exception, psycopg2.Error) as error:
            print("SQL error: " + error.args[0])
            exit(1)
        account = exas_cursor.fetchone()
        if not account:
            print("No valid account for user " + user[1] + " " + user[2])
            exit(1)
        user_name = account[0]
        user_email = account[1]

        user_info = {'id_user': 0,
                     'user_firstname': user[1],
                     'user_lastname': user[2],
                     'user_username': account[0],
                     'user_email': account[1],
                     'user_enabled': True,
                     'user_profile': {},
                     'user_notes': 'Importé de TeraPlus',
                     'user_user_groups': [{'id_user_group': opentera_id_user_group}],
                     'user_password': generate_password(10)
                     }

        print("--> Creating user '" + user_info['user_firstname'] + " " + user_info['user_lastname']
              + " (" + user_info['user_username'] + ")' with PASSWORD = " + user_info['user_password'] + " ...")
        # Create user in OpenTera, if not already there
        rval = create_user(user_info)
        if not rval:
            exit(1)
        tera_open_users_map[user_id] = rval['id_user']

    # Query for sessions types
    print("** CREATING SESSION TYPES **")
    query = "SELECT * FROM t_sessions_types INNER JOIN t_session_type_access ON " \
            "t_sessions_types.id_ses_type = t_session_type_access.id_session_type WHERE " \
            "id_usergroup IN(%s)"
    try:
        tera_cursor.execute(query, teraplus_usergroups)
    except(Exception, psycopg2.Error) as error:
        print("SQL error: " + error.args[0])
        exit(1)

    sessions_types = tera_cursor.fetchall()

    for session_type in sessions_types:
        session_type_id = session_type[0]
        if session_type_id not in tera_open_session_type_map:
            session_type_name = session_type[1]
            session_type_online = session_type[5]
            session_type_color = session_type[6]
            print("--> Creating session type '" + session_type_name + "' (online: " + str(session_type_online) + ")...")
            # Create session type
            opentera_session_type = create_session_type(session_type_name, session_type_online, session_type_color,
                                                        opentera_id_project)
            tera_open_session_type_map[session_type_id] = opentera_session_type['id_session_type']

    # Query for participants in the specified participant group
    print("** CREATING PARTICIPANTS **")
    query = "SELECT * FROM t_patients WHERE id_group=%s"
    try:
        tera_cursor.execute(query, [teraplus_id_group])
    except(Exception, psycopg2.Error) as error:
        print("SQL error: " + error.args[0])
        exit(1)

    participants = tera_cursor.fetchall()
    for participant in participants:
        part_id = participant[0]
        part_name = participant[1]
        # part_create_date = participant[2]
        part_active = (participant[5] is not None)

        print("--> Creating participant '" + part_name + "' (active: " + str(part_active) + ")...")
        rval = create_participant(part_name, part_active, opentera_id_project)
        if not rval:
            exit(1)
        opentera_id_participant = rval['id_participant']

        # Query for sessions for current participant
        query = "SELECT * FROM t_sessions INNER JOIN t_sessions_dates ON t_sessions.id_session_date = " \
                "t_sessions_dates.id_session_date INNER JOIN v_sessions_duration ON t_sessions.id_session = " \
                "v_sessions_duration.id_session WHERE id_patient = %s"
        try:
            tera_cursor.execute(query, [part_id])
        except(Exception, psycopg2.Error) as error:
            print("SQL error: " + error.args[0])
            exit(1)

        sessions = tera_cursor.fetchall()
        for session in sessions:
            session_id = session[0]
            ses_info = {'id_session': 0,
                        'session_name': session[1],
                        'session_start_datetime': timezone.localize(session[2]).isoformat(),
                        'session_status': session[3],  # Status code are the same between TeraPlus and OpenTera!
                        'id_session_type': tera_open_session_type_map[session[4]],
                        'id_creator_user': tera_open_users_map[session[5]],
                        'session_comments': session[6],
                        'session_duration': session[13].total_seconds()
                        }
            print("---> Creating session '" + ses_info['session_name']
                  + "' (" + ses_info['session_start_datetime'] + ")...")
            rval = create_session(ses_info, opentera_id_participant)
            if not rval:
                exit(1)
            opentera_id_session = rval['id_session']

            # Query sessions logs for that session
            query = "SELECT * FROM t_sessions_logs WHERE id_session = %s"
            try:
                tera_cursor.execute(query, [session_id])
            except(Exception, psycopg2.Error) as error:
                print("SQL error: " + error.args[0])
                exit(1)

            sessions_logs = tera_cursor.fetchall()
            for log in sessions_logs:
                session_log_date = timezone.localize(log[3])
                session_log_text = log[4]
                session_log_type = log[2]
                # Convert logtype to SessionEventType
                # SESSIONLOG_NONE=0 --> GENERAL_ERROR=0
                # SESSIONLOG_START=1 --> SESSION_START = 3
                # SESSIONLOG_STOP=2 --> SESSION_STOP = 4
                # SESSIONLOG_DISCONNECT=3 --> SESSION_STOP = 4
                # SESSIONLOG_PAUSE=4 --> SESSION_STOP = 4
                # SESSIONLOG_NEWTEST=5 --> GENERAL_INFO = 1
                # SESSIONLOG_DELETETEST=6 --> GENERAL_INFO = 1
                # SESSIONLOG_EDITTEST=7 --> GENERAL_INFO = 1
                # SESSIONLOG_LOCKTEST=8 --> GENERAL_INFO = 1
                # SESSIONLOG_UNLOCKTEST=9 --> GENERAL_INFO = 1
                # SESSIONLOG_DELETEDATA=10 --> GENERAL_INFO = 1
                if session_log_type == 1:
                    session_log_type = 3
                elif session_log_type == 2 or session_log_type == 3 or session_log_type == 4:
                    session_log_type = 4
                else:
                    session_log_type = 1

                # TODO: Create session event
                print("----> Creating session event '" + session_log_text + "' (" + session_log_date.isoformat() +
                      ")...")
                rval = create_session_event(session_log_date, session_log_type, session_log_text, opentera_id_session)
                if not rval:
                    exit(1)

    tera_cursor.close()
    exas_cursor.close()
    tera_conn.close()
    exas_conn.close()
    exit(0)
