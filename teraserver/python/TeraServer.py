"""
Project OpenTera (https://github.com/introlab/opentera)

Copyright (C) 2020
IntRoLab / ESTRAD, Université de Sherbrooke, Centre de Recherche sur le Vieillissement de Sherbrooke

Authors:

Simon Brière, ing., M.Sc.A. (simon.briere@usherbrooke.ca)
Dominic Létourneau, ing., M.Sc.A (dominic.letourneau@usherbrooke.ca)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import pathlib
import sys

from modules.LoginModule.LoginModule import LoginModule
from modules.FlaskModule.FlaskModule import FlaskModule
from modules.TwistedModule.TwistedModule import TwistedModule
from modules.ServiceLauncherModule.ServiceLauncherModule import ServiceLauncherModule

from libtera.ConfigManager import ConfigManager
from libtera.redis.RedisClient import RedisClient
import modules.Globals as Globals

from modules.UserManagerModule.UserManagerModule import UserManagerModule
from modules.DatabaseModule.DBManager import DBManager


import os

from sqlalchemy.exc import OperationalError
import libtera.crypto.crypto_utils as crypto
from libtera.utils.TeraVersions import TeraVersions


def generate_certificates(config: ConfigManager):
    """
        Will generate certificates and keys if they do not exist
    """
    site_certificate_path = config.server_config['ssl_path'] + '/' + config.server_config['site_certificate']
    site_key_path = config.server_config['ssl_path'] + '/' + config.server_config['site_private_key']
    ca_certificate_path = config.server_config['ssl_path'] + '/' + config.server_config['ca_certificate']
    ca_key_path = config.server_config['ssl_path'] + '/' + config.server_config['ca_private_key']

    if not os.path.exists(site_certificate_path) or not os.path.exists(site_key_path):
        print('Generating Site certificate and key')
        site_info = crypto.generate_local_certificate()
        # Save files
        crypto.write_private_key_and_certificate(site_info, keyfile=site_key_path, certfile=site_certificate_path)

    if not os.path.exists(ca_certificate_path) or not os.path.exists(ca_key_path):
        print('Generating Site certificate and key')
        ca_info = crypto.generate_ca_certificate(common_name='Local CA')
        # Save files
        crypto.write_private_key_and_certificate(ca_info, keyfile=ca_key_path, certfile=ca_certificate_path)


def verify_file_upload_directory(config: ConfigManager, create=True):
    file_upload_path = config.server_config['upload_path']

    if not os.path.exists(file_upload_path):
        if create:
            # TODO Change permissions?
            os.mkdir(file_upload_path, 0o700)
        else:
            return None
    return file_upload_path


def init_shared_variables(config):
    # Create user token
    from libtera.db.models.TeraServerSettings import TeraServerSettings

    # Dynamic key for users, updated at every restart (for now)
    # Server should rotate key every hour, day?
    user_token_key = TeraServerSettings.generate_token_key(32)
    participant_token_key = TeraServerSettings.generate_token_key(32)
    service_token_key = TeraServerSettings.generate_token_key(32)

    # Create redis client
    import redis

    redis_client = redis.Redis(host=config.redis_config['hostname'],
                               port=config.redis_config['port'],
                               db=config.redis_config['db'],
                               username=config.redis_config['username'],
                               password=config.redis_config['password'])

    # Set API Token Keys
    from modules.RedisVars import RedisVars
    # Set USER
    redis_client.set(RedisVars.RedisVar_UserTokenAPIKey, user_token_key)

    # Set SERVICE
    redis_client.set(RedisVars.RedisVar_ServiceTokenAPIKey, service_token_key)

    # Set DEVICE
    # TODO - Verify static / dynamic tokens for devices
    redis_client.set(RedisVars.RedisVar_DeviceTokenAPIKey, TeraServerSettings.get_server_setting_value(
        TeraServerSettings.ServerDeviceTokenKey))
    redis_client.set(RedisVars.RedisVar_DeviceStaticTokenAPIKey, TeraServerSettings.get_server_setting_value(
        TeraServerSettings.ServerDeviceTokenKey))

    # Set PARTICIPANT
    redis_client.set(RedisVars.RedisVar_ParticipantTokenAPIKey, participant_token_key)
    redis_client.set(RedisVars.RedisVar_ParticipantStaticTokenAPIKey, TeraServerSettings.get_server_setting_value(
                                      TeraServerSettings.ServerParticipantTokenKey))

    # Set versions
    versions = TeraVersions()

    # Will update clients versions (hard coded in TeraVersions)
    versions.load_from_db()
    versions.save_to_db()


def init_services(config: ConfigManager):
    print('Initializing services...')

    from libtera.db.models.TeraService import TeraService
    from modules.RedisVars import RedisVars
    import json
    # Create redis client
    import redis
    redis_client = redis.Redis(host=config.redis_config['hostname'],
                               port=config.redis_config['port'],
                               db=config.redis_config['db'],
                               username=config.redis_config['username'],
                               password=config.redis_config['password'])

    # Set python path to current folder so that import work from services
    tera_python_dir = pathlib.Path(__file__).parent.absolute()
    os.environ['PYTHONPATH'] = str(tera_python_dir)

    services = TeraService.query.all()
    for service in services:
        # Ignore special service TeraServer
        if service.service_key == 'OpenTeraServer':
            Globals.opentera_service_id = service.id_service
            continue
        if service.service_enabled:
            print('Activating service: ' + service.service_key)
            redis_client.set(RedisVars.RedisVar_ServicePrefixKey + service.service_key, json.dumps(service.to_json()))
        else:
            print('Skipping disabled service: ' + service.service_key)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='OpenTera Server')
    parser.add_argument('--enable_tests', help='Test mode for server.', default=False)
    args = parser.parse_args()

    config_man = ConfigManager()

    # SERVER CONFIG
    ###############
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle, the pyInstaller bootloader
        # extends the sys module by a flag frozen=True and sets the app
        # path into variable _MEIPASS'.
        application_path = sys._MEIPASS
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))

    config_file = None

    # Set environment variable for reading configuration file
    # Will be helpful for docker containers
    if os.environ.__contains__('OPENTERA_CONFIG_PATH'):
        config_file = str(os.environ['OPENTERA_CONFIG_PATH'])
    else:
        config_file = application_path + os.sep + 'config' + os.sep + 'TeraServerConfig.ini'

    print("Opening config file: ", config_file)

    # Load configuration file.
    config_man.load_config(config_file)

    # Generate certificate (if required)
    generate_certificates(config_man)

    # Verify file upload path, create if does not exist
    # TODO Remove this, not needed. Now handled by FileTransferService
    # verify_file_upload_directory(config_man, True)

    # DATABASE CONFIG AND OPENING
    #############################
    # POSTGRES = {
    #     'user': config_man.db_config['username'],
    #     'pw': config_man.db_config['password'],
    #     'db': config_man.db_config['name'],
    #     'host': config_man.db_config['url'],
    #     'port': config_man.db_config['port']
    # }
    Globals.db_man = DBManager(config_man)

    try:
        # Echo will be set by "debug_mode" flag
        if args.enable_tests:
            # In RAM SQLITE DB for tests
            Globals.db_man.open_local(None, echo=True, ram=True)

            # Create default values, if required
            Globals.db_man.create_defaults(config=config_man, test=True)
        else:
            Globals.db_man.open(config_man.server_config['debug_mode'])

            # Create minimal values, if required
            Globals.db_man.create_defaults(config=config_man, test=True)

    except OperationalError as e:
        print("Unable to connect to database - please check settings in config file!", e)
        quit()

    # Create Redis variables shared with services
    init_shared_variables(config=config_man)

    # Initialize enabled services
    init_services(config=config_man)

    # Main Flask module
    flask_module = FlaskModule(config_man)

    # LOGIN MANAGER, must be initialized after Flask
    #################################################
    login_module = LoginModule(config_man)

    # Twisted will run flask, must be initialized after Flask
    #########################################################
    twisted_module = TwistedModule(config_man)

    user_manager_module = UserManagerModule(config_man)

    service_launcher = ServiceLauncherModule(config_man)

    # This is blocking, running event loop
    twisted_module.run()

