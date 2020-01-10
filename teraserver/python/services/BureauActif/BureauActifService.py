from services.BureauActif.FlaskModule import FlaskModule
from services.BureauActif.TwistedModule import TwistedModule
from services.BureauActif.ConfigManager import ConfigManager

if __name__ == '__main__':

    # Load configuration
    config_man = ConfigManager()
    config_man.load_config('BureauActifService.ini')

    # DATABASE CONFIG AND OPENING
    #############################
    POSTGRES = {
        'user': config_man.db_config['username'],
        'pw': config_man.db_config['password'],
        'db': config_man.db_config['name'],
        'host': config_man.db_config['url'],
        'port': config_man.db_config['port']
    }

    # Main Flask module
    flask_module = FlaskModule(config_man)

    # Main Twisted module
    twisted_module = TwistedModule(config_man)

    # Run reactor
    twisted_module.run()

    print('BureauActifService - done!')
