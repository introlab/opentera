import sys
from requests import get, post, delete
import json
from datetime import datetime

from services.BureauActif.tools.sample_data_loader import load_data_from_path


class Config:
    hostname = 'localhost'
    port = 40075
    servicename = '/bureau'

    # User endpoints
    user_login_endpoint = '/api/user/login'
    user_participant_endpoint = '/api/user/participants'
    user_site_endpoint = '/api/user/sites'
    user_project_endpoint = '/api/user/projects'
    user_device_endpoint = '/api/user/devices'
    user_device_project_endpoint = '/api/user/deviceprojects'
    user_device_participant_endpoint = '/api/user/deviceparticipants'
    user_session_type_project = '/api/user/sessiontypeprojects'
    user_service_project = '/api/user/services/projects'

    # Device endpoints
    device_login_endpoint = '/api/device/login'
    device_session_endpoint = '/api/device/sessions'
    # device_session_data_endpoint = '/api/device/device_upload'
    device_session_data_endpoint = '/api/rawdata'

    service_info_endpoint = '/api/serviceinfos'

    # Super secure.
    username = 'admin'
    password = 'admin'


def _make_url(hostname, port, endpoint):
    return 'https://' + hostname + ':' + str(port) + endpoint


def login_user(config: Config):
    url = _make_url(config.hostname, config.port, config.user_login_endpoint)
    response = get(url=url, verify=False, auth=(config.username, config.password))
    if response.status_code == 200:
        return response.json()
    import inspect
    print('Error in ' + inspect.currentframe().f_code.co_name + ': Code=' + str(response.status_code) + ', Message=' +
          response.content.decode())
    return {}


def create_site(config: Config, name):
    url = _make_url(config.hostname, config.port, config.user_site_endpoint)

    site_dict = {'site': {'id_site': 0,
                          'site_name': name}
                 }
    try:
        response = post(url=url, json=site_dict, verify=False, auth=(config.username, config.password))
    except Exception as e:
        print(e)
        return {}

    if response.status_code == 200:
        return response.json().pop()
    import inspect
    print('Error in ' + inspect.currentframe().f_code.co_name + ': Code=' + str(response.status_code) + ', Message=' +
          response.content.decode())
    return {}


def get_site(config: Config, name: str):
    url = _make_url(config.hostname, config.port, config.user_site_endpoint)
    params = {'name': name}
    try:
        response = get(url=url, params=params, verify=False, auth=(config.username, config.password))
    except Exception as e:
        print(e)
        return {}

    if response.status_code == 200:
        if response.json():
            return response.json().pop()
        else:
            return None
    import inspect
    print('Error in ' + inspect.currentframe().f_code.co_name + ': Code=' + str(response.status_code) + ', Message=' +
          response.content.decode())
    return {}


def create_project(config: Config, name: str, site_id: int):

    url = _make_url(config.hostname, config.port, config.user_project_endpoint)

    project_dict = {'project': {'id_project': 0,
                                'project_name': name,
                                'id_site': site_id}
                    }
    try:
        response = post(url=url, json=project_dict, verify=False, auth=(config.username, config.password))
    except Exception as e:
        print(e)
        return {}

    if response.status_code == 200:
        return response.json().pop()
    import inspect
    print('Error in ' + inspect.currentframe().f_code.co_name + ': Code=' + str(response.status_code) + ', Message=' +
          response.content.decode())
    return {}


def get_project(config: Config, name: str):
    url = _make_url(config.hostname, config.port, config.user_project_endpoint)
    params = {'name': name}
    try:
        response = get(url=url, params=params, verify=False, auth=(config.username, config.password))
    except Exception as e:
        print(e)
        return {}

    if response.status_code == 200:
        if response.json():
            return response.json().pop()
        else:
            return None
    import inspect
    print('Error in ' + inspect.currentframe().f_code.co_name + ': Code=' + str(response.status_code) + ', Message=' +
          response.content.decode())
    return {}


def create_participant(config: Config, name: str, id_project: int):
    url = _make_url(config.hostname, config.port, config.user_participant_endpoint)

    try:

        participant_dict = {'participant': {'id_participant': 0,
                                            'id_project': id_project,
                                            'participant_name': name}}

        response = post(url=url, json=participant_dict, verify=False, auth=(config.username, config.password))

    except Exception as e:
        print(e)
        return {}

    if response.status_code == 200:
        return response.json().pop()
    import inspect
    print('Error in ' + inspect.currentframe().f_code.co_name + ': Code=' + str(response.status_code) + ', Message=' +
          response.content.decode())
    return {}


def get_participant(config: Config, name: str):
    url = _make_url(config.hostname, config.port, config.user_participant_endpoint)
    params = {'name': name}
    try:
        response = get(url=url, params=params, verify=False, auth=(config.username, config.password))
    except Exception as e:
        print(e)
        return {}

    if response.status_code == 200:
        if response.json():
            return response.json().pop()
        else:
            return None
    import inspect
    print('Error in ' + inspect.currentframe().f_code.co_name + ': Code=' + str(response.status_code) + ', Message=' +
          response.content.decode())
    return {}


def delete_participant(config: Config, id: int):
    url = _make_url(config.hostname, config.port, config.user_participant_endpoint)
    params = {'id': id}
    try:
        response = delete(url=url, params=params, verify=False, auth=(config.username, config.password))
    except Exception as e:
        print(e)
        return {}

    if response.status_code == 200 and response.json():
        return response.json().pop()

    if response.status_code != 200:
        import inspect
        print('Error in ' + inspect.currentframe().f_code.co_name + ': Code=' + str(response.status_code) +
              ', Message=' + response.content.decode())
    return {}


def create_device(config: Config, name: str):
    url = _make_url(config.hostname, config.port, config.user_device_endpoint)
    try:
        device_dict = {'device': {'id_device': 0, 'device_name': name, 'id_device_type': 4, 'device_enabled': True}}
        response = post(url=url, json=device_dict, verify=False, auth=(config.username, config.password))

    except Exception as e:
        print(e)
        return {}

    if response.status_code == 200:
        return response.json().pop()
    import inspect
    print('Error in ' + inspect.currentframe().f_code.co_name + ': Code=' + str(response.status_code) + ', Message=' +
          response.content.decode())
    return {}


def get_device(config: Config, name: str):
    url = _make_url(config.hostname, config.port, config.user_device_endpoint)
    params = {'name': name}
    try:
        response = get(url=url, params=params, verify=False, auth=(config.username, config.password))
    except Exception as e:
        print(e)
        return {}

    if response.status_code == 200:
        if response.json():
            return response.json().pop()
        else:
            return None
    import inspect
    print('Error in ' + inspect.currentframe().f_code.co_name + ': Code=' + str(response.status_code) + ', Message=' +
          response.content.decode())
    return {}


def add_device_project(config: Config, id_project: int, id_device: int):
    url = _make_url(config.hostname, config.port, config.user_device_project_endpoint)
    try:
        device_project_dict = {'device_project': {'id_device': id_device, 'id_project': id_project}}
        response = post(url=url, json=device_project_dict, verify=False, auth=(config.username, config.password))
    except Exception as e:
        print(e)
        return {}
    if response.status_code == 200:
        return response.json()
    import inspect
    print('Error in ' + inspect.currentframe().f_code.co_name + ': Code=' + str(response.status_code) + ', Message=' +
          response.content.decode())
    return {}


def add_device_participant(config: Config, id_participant: int, id_device: int):
    url = _make_url(config.hostname, config.port, config.user_device_participant_endpoint)
    try:
        device_participant_dict = {'device_participant': {'id_device': id_device, 'id_participant': id_participant}}
        response = post(url=url, json=device_participant_dict, verify=False, auth=(config.username, config.password))
    except Exception as e:
        print(e)
        return {}

    if response.status_code == 200:
        return response.json().pop()
    import inspect
    print('Error in ' + inspect.currentframe().f_code.co_name + ': Code=' + str(response.status_code) + ', Message=' +
          response.content.decode())
    return {}


def create_device_session(config: Config, token: str, session_name: str,
                          session_datetime: datetime, session_participants: list, id_session_type: int):
    url = _make_url(config.hostname, config.port, config.device_session_endpoint) + '?token=' + token
    try:
        session_dict = {'session': {'id_session': 0,
                                    'session_name': session_name,
                                    'session_start_datetime': str(session_datetime),
                                    'session_status': 2,  # Done...
                                    'id_session_type': id_session_type,
                                    'session_participants': session_participants}}

        response = post(url=url, json=session_dict, verify=False)
    except Exception as e:
        print(e)
        return {}

    if response.status_code == 200:
        return response.json()
    import inspect
    print('Error in ' + inspect.currentframe().f_code.co_name + ': Code=' + str(response.status_code) + ', Message=' +
          response.content.decode())
    return {}


def add_session_type_project(config: Config, id_project: int, id_session_type: int):

    url = _make_url(config.hostname, config.port, config.user_session_type_project)
    try:
        session_type_project_dict = {'session_type_project': {'id_project': id_project,
                                                              'id_session_type': id_session_type}}
        response = post(url=url, json=session_type_project_dict, verify=False, auth=(config.username, config.password))
    except Exception as e:
        print(e)
        return {}

    if response.status_code == 200:
        return response.json().pop()
    import inspect
    print('Error in ' + inspect.currentframe().f_code.co_name + ': Code=' + str(response.status_code) + ', Message=' +
          response.content.decode())
    return {}


def add_service_to_project(config: Config, id_project: int, s_uuid: str):

    url = _make_url(config.hostname, config.port, config.user_service_project)
    try:
        service_project_dict = {'service_project': {'id_project': id_project, 'service_uuid': s_uuid}}
        response = post(url=url, json=service_project_dict, verify=False, auth=(config.username, config.password))
    except Exception as e:
        print(e)
        return {}

    if response.status_code == 200:
        return response.json().pop()
    import inspect
    print('Error in ' + inspect.currentframe().f_code.co_name + ': Code=' + str(response.status_code) + ', Message=' +
          response.content.decode())
    return {}


def create_session_data(config: Config, token: str, filename: str, data, id_session: int,
                        date: datetime = datetime.now()):
    url = _make_url(config.hostname, config.port, config.servicename + '/' + config.device_session_data_endpoint) + \
          '?token=' + token

    # id_session = int(request.headers['X-Id-Session'])
    # filename = secure_filename(request.headers['X-Filename'])
    # creation_date = datetime.datetime.strptime(request.headers['X-Filedate'], '%Y-%m-%d %H:%M:%S')

    try:
        request_headers = {'X-Id-Session':  str(id_session),
                           'X-Filename': filename,
                           'X-Filedate': date.strftime('%Y-%m-%d %H:%M:%S'),
                           'Content-Type': 'application/octet-stream'}

        response = post(url=url, data=data, headers=request_headers, verify=False)
    except Exception as e:
        print(e)
        return {}

    if response.status_code == 200:
        return response.json()
    import inspect
    print('Error in ' + inspect.currentframe().f_code.co_name + ': Code=' + str(response.status_code) + ', Message=' +
          response.content.decode())
    return {}


def get_bureau_actif_service_uuid(config: Config, token: str) -> str:
    url = _make_url(config.hostname, config.port, config.servicename + config.service_info_endpoint)
    params = {'token': token}
    try:
        response = get(url=url, params=params, verify=False)
    except Exception as e:
        print(e)
        return ''

    if response.status_code == 200 and response.json():
        service_infos = response.json()
        return service_infos['service_uuid']
    import inspect
    print('Error in ' + inspect.currentframe().f_code.co_name + ': Code=' + str(response.status_code) + ', Message=' +
          response.content.decode())
    return ''


if __name__ == '__main__':

    base_config = Config()
    data_path = r''

    # Ignore insecure requests warning
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Get data from files
    result = load_data_from_path(data_path)

    # Login admin
    admin_info = login_user(base_config)

    # Bureau Actif service uuid
    service_uuid = get_bureau_actif_service_uuid(base_config, admin_info['user_token'])

    # create_participant(config1, 'PartBA_1')
    site_info = get_site(base_config, 'Bureau Actif Tests')

    if not site_info:
        site_info = create_site(base_config, 'Bureau Actif Tests')

    project_info = get_project(base_config, 'Donnees Tests')

    if not project_info:
        project_info = create_project(base_config, 'Donnees Tests', site_info['id_site'])
        # TODO get session types from server, hardcoded to 2 = SENSOR_DATA
        project_session_type_info = add_session_type_project(base_config, project_info['id_project'], 2)
        add_service_to_project(base_config, project_info['id_project'], service_uuid)

    import os
    participant_name = os.path.split(data_path)[-1]
    participant_info = get_participant(base_config, participant_name)

    if participant_info:
        # Delete that participant - we always start fresh!
        delete_participant(base_config, participant_info['id_participant'])

    participant_info = create_participant(base_config, participant_name, project_info['id_project'])

    device_name = 'Bureau - ' + participant_name
    device_info = get_device(base_config, device_name)

    if not device_info:
        device_info = create_device(base_config, device_name)
        device_project_info = add_device_project(base_config, project_info['id_project'], device_info['id_device'])

    device_participant_info = add_device_participant(base_config, participant_info['id_participant'],
                                                     device_info['id_device'])

    # Config from results, remove from dict
    device_config = result['config']
    del result['config']

    for key in result:
        print('Processing: ', key)

        # Put config in each datasets
        result[key]['config'] = device_config

        # Get time from key
        device_date = datetime.strptime(key, '%Y-%m-%d')

        # Create json data
        device_data = json.dumps(result[key])

        # Create session
        device_session_info = create_device_session(base_config,
                                                    device_info['device_token'], 'Session-' + key, device_date,
                                                    [participant_info['participant_uuid']], 2)

        # Send data
        create_session_data(base_config, device_info['device_token'], key + '.json', device_data.encode('utf-8'),
                            device_session_info['id_session'], device_date)


