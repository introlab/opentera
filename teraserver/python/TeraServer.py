import sys

from modules.LoginModule.LoginModule import LoginModule
from modules.FlaskModule.FlaskModule import FlaskModule
from modules.TwistedModule.TwistedModule import TwistedModule

from libtera.ConfigManager import ConfigManager
from modules.Globals import db_man
from modules.RedisModule.RedisModule import setup_redis
from modules.RedisModule.RedisModule import get_redis
from modules.UserManagerModule.UserManagerModule import UserManagerModule
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
    setup_redis(config_man)

    print('Rdis started:', get_redis())
    if get_redis() is None:
        print('error...')

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
    
    # This is blocking, running event loop
    # reactor.addSystemEventTrigger('before', 'shutdown', reactor_is_shutting_down)
    twisted_module.run()

