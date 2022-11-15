from flask import request
from ua_parser import user_agent_parser


class UserAgentParser:
    @staticmethod
    def parse_request_for_login_infos(http_request: request) -> dict:
        infos = {'client_name': '',
                 'client_version': '',
                 'os_name': '',
                 'os_version': '',
                 'server_endpoint': http_request.endpoint,
                 'client_ip': http_request.remote_addr
                 }

        if 'USER_AGENT' in http_request.headers:
            user_agent = user_agent_parser.Parse(http_request.headers['USER_AGENT'])
            infos['client_name'] = ''
            if user_agent['device']['brand']:
                infos['client_name'] = user_agent['device']['brand'] + ' - '
            if user_agent['device']['family']:
                infos['client_name'] += user_agent['device']['family'] + ' - '

            infos['client_name'] += user_agent['user_agent']['family']

            if user_agent['user_agent']['major']:
                infos['client_version'] = user_agent['user_agent']['major']
            else:
                infos['client_version'] = 'x'
            infos['client_version'] += '.'
            if user_agent['user_agent']['minor']:
                infos['client_version'] += user_agent['user_agent']['minor']
            else:
                infos['client_version'] += 'x'
            infos['client_version'] += '.'
            if user_agent['user_agent']['patch']:
                infos['client_version'] += user_agent['user_agent']['patch']
            else:
                infos['client_version'] += 'x'

            infos['os_name'] = user_agent['os']['family']

            if user_agent['os']['major']:
                infos['os_version'] = user_agent['os']['major']
            else:
                infos['os_version'] = 'x'
            infos['os_version'] += '.'
            if user_agent['os']['minor']:
                infos['os_version'] += user_agent['os']['minor']
            else:
                infos['os_version'] += 'x'
            infos['os_version'] += '.'
            if user_agent['os']['patch']:
                infos['os_version'] += user_agent['os']['patch']
            else:
                infos['os_version'] += 'x'

        if 'X-Client-Name' in http_request.headers:
            infos['client_name'] = http_request.headers['X-Client-Name']
        if 'X-Client_Version' in http_request.headers:
            infos['client_version'] = http_request.headers['X-Client-Version']

        if 'X-Script-Name' in http_request.headers:
            infos['server_endpoint'] = http_request.headers['X-Script-Name']

        return infos