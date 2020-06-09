import services.VideoRehabService.Globals as Globals
from libtera.redis.RedisClient import RedisClient
from modules.RedisVars import RedisVars

# Twisted
from twisted.application import internet, service
from twisted.internet import reactor, ssl
from twisted.python.threadpool import ThreadPool
from twisted.web.http import HTTPChannel
from twisted.web.server import Site
from twisted.web.static import File
from twisted.web.wsgi import WSGIResource
from twisted.python import log
import sys
import os

# Flask Module
from services.VideoRehabService.FlaskModule import FlaskModule

if __name__ == '__main__':

    # Very first thing, log to stdout
    log.startLogging(sys.stdout)

    # Load configuration
    if not Globals.config_man.load_config('VideoRehabService.json'):
        print('Invalid config')

    # Global redis client
    Globals.redis_client = RedisClient(Globals.config_man.redis_config)
    Globals.api_user_token_key = Globals.redis_client.redisGet(RedisVars.RedisVar_UserTokenAPIKey)
    Globals.api_device_token_key = Globals.redis_client.redisGet(RedisVars.RedisVar_DeviceTokenAPIKey)
    Globals.api_participant_token_key = Globals.redis_client.redisGet(RedisVars.RedisVar_ParticipantTokenAPIKey)

    # Get service UUID
    service_info = Globals.redis_client.redisGet(RedisVars.RedisVar_ServicePrefixKey +
                                                 Globals.config_man.service_config['name'])
    import sys
    if service_info is None:
        sys.stderr.write('Error: Unable to get service info from OpenTera Server - is the server running and config '
                         'correctly set in this service?')
        exit(1)
    import json
    service_info = json.loads(service_info)
    if 'service_uuid' not in service_info:
        sys.stderr.write('OpenTera Server didn\'t return a valid service UUID - aborting.')
        exit(1)

    # Update service uuid
    Globals.config_man.service_config['ServiceUUID'] = service_info['service_uuid']

    # Create the service app
    application = service.Application(Globals.config_man.service_config['name'])

    # Create REST backend
    flaskModule = FlaskModule(Globals.config_man)

    # Create twisted service
    flaskModuleService = flaskModule.create_service()

    # Connect our services to the application, just like a normal service.
    flaskModuleService.setServiceParent(application)

    # Start App / reactor events
    reactor.run()
