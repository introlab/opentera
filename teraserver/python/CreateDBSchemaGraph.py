from sqlalchemy import MetaData
from sqlalchemy_schemadisplay import create_schema_graph
from opentera.config.ConfigManager import ConfigManager
import os
import sys


if __name__ == '__main__':

    config_file = None
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

    # Set environment variable for reading configuration file
    # Will be helpful for docker containers
    if os.environ.__contains__('OPENTERA_CONFIG_PATH'):
        config_file = str(os.environ['OPENTERA_CONFIG_PATH'])
    else:
        config_file = application_path + os.sep + 'config' + os.sep + 'TeraServerConfig.ini'

    print("Opening config file: ", config_file)

    # Load configuration file.
    config_man.load_config(config_file)


    # DATABASE CONFIG AND OPENING
    #############################
    # POSTGRES = {
    #     'user': config_man.db_config['username'],
    #     'pw': config_man.db_config['password'],
    #     'db': config_man.db_config['name'],
    #     'host': config_man.db_config['url'],
    #     'port': config_man.db_config['port']
    # }

    db_uri = 'postgresql://%(username)s:%(password)s@%(url)s:%(port)s/%(name)s' % config_man.db_config

    # create the pydot graph object by autoloading all tables via a bound metadata object
    graph = create_schema_graph(metadata=MetaData(db_uri),
                                show_datatypes=True,  # The image would get nasty big if we'd show the datatypes
                                show_indexes=True,  # ditto for indexes
                                rankdir='TB',  # From left to right (instead of top to bottom)
                                concentrate=True  # Don't try to join the relation lines together
                                )
    graph.write_png('opentera_dbschema.png')   # write out the file
