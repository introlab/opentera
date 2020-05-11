from services.VideoRehabService.Globals import config_man

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
    if not config_man.load_config('VideoRehabService.json'):
        print('Invalid config')

    # Global redis client
    # Globals.redis_client = RedisClient(config_man.redis_config)
    # Globals.api_user_token_key = Globals.redis_client.redisGet(RedisVars.RedisVar_UserTokenAPIKey)
    # Globals.api_device_token_key = Globals.redis_client.redisGet(RedisVars.RedisVar_DeviceTokenAPIKey)
    # Globals.api_participant_token_key = Globals.redis_client.redisGet(RedisVars.RedisVar_ParticipantTokenAPIKey)



    # Create the service app
    application = service.Application(config_man.service_config['name'])

    flaskModule = FlaskModule(config_man)

    flaskModuleService = flaskModule.create_service()

    # Connect our services to the application, just like a normal service.
    flaskModuleService.setServiceParent(application)

    # Start App
    reactor.run()