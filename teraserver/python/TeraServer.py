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

from modules.LoginModule.LoginModule import LoginModule
from modules.FlaskModule.FlaskModule import FlaskModule
from modules.TwistedModule.TwistedModule import TwistedModule

from libtera.ConfigManager import ConfigManager
from modules.Globals import db_man
from modules.UserManagerModule.UserManagerModule import UserManagerModule
from modules.WebRTCModule.WebRTCModule import WebRTCModule

import os

from sqlalchemy.exc import OperationalError

reactor_running = True


def reactor_is_shutting_down():
    print('before_shutdown')
    global reactor_running
    reactor_running = False


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

    config_file = application_path + os.sep + 'config' + os.sep + 'TeraServerConfig.ini'
    config_man.load_config(config_file)

    # We should remove that soon...
    # setup_redis(config_man)

    # print('Rdis started:', get_redis())
    # if get_redis() is None:
        # print('error...')

    # DATABASE CONFIG AND OPENING
    #############################
    POSTGRES = {
        'user': config_man.db_config['username'],
        'pw': config_man.db_config['password'],
        'db': config_man.db_config['name'],
        'host': config_man.db_config['url'],
        'port': config_man.db_config['port']
    }

    try:
        db_man.open(POSTGRES, True)
    except OperationalError:
        print("Unable to connect to database - please check settings in config file!")
        quit()

    # Create default values, if required
    db_man.create_defaults()

    # Main Flask module
    flask_module = FlaskModule(config_man)

    # LOGIN MANAGER
    ###############
    login_module = LoginModule(config_man)

    # Twisted will run flask
    twisted_module = TwistedModule(config_man)

    user_manager_module = UserManagerModule(config_man)

    # WebRTCModule
    webrtc_module = WebRTCModule(config_man)
    
    # This is blocking, running event loop
    # reactor.addSystemEventTrigger('before', 'shutdown', reactor_is_shutting_down)
    twisted_module.run()

