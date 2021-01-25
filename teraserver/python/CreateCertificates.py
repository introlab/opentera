"""
Project OpenTera (https://github.com/introlab/opentera)

Copyright (C) 2019
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

import sys


from opentera.config.ConfigManager import ConfigManager

import os

import opentera.crypto.crypto_utils as crypto


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


if __name__ == '__main__':

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
