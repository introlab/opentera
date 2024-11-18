import datetime
from services.FileTransferService.FlaskModule import flask_app
import services.FileTransferService.Globals as Globals
from opentera.redis.RedisClient import RedisClient
from services.FileTransferService.ConfigManager import ConfigManager
from opentera.services.ServiceAccessManager import ServiceAccessManager
from opentera.redis.RedisVars import RedisVars

# Twisted
from twisted.internet import reactor, defer, task
from twisted.python import log
import sys
import os

from opentera.services.ServiceOpenTeraWithAssets import ServiceOpenTeraWithAssets
from sqlalchemy.exc import OperationalError
from services.FileTransferService.FlaskModule import FlaskModule
import opentera.messages.python as messages

from services.FileTransferService.libfiletransferservice.db.models.ArchiveFileData import ArchiveFileData

class FileTransferService(ServiceOpenTeraWithAssets):
    def __init__(self, config_man: ConfigManager, this_service_info):
        ServiceOpenTeraWithAssets.__init__(self, config_man, this_service_info)

        # Create REST backend
        self.flaskModule = FlaskModule(config_man)

        # Create twisted service
        self.flaskModuleService = self.flaskModule.create_service()

        self.upload_directory = self.verify_file_upload_directory(config_man)

        if self.upload_directory is not None:
            # Create cleaning task, every hour by default, can specify period (s) in arg.
            self.archive_cleaning_task = self.setup_file_archive_cleanup_task(3600.0)

    def setup_file_archive_cleanup_task(self, period_s: float = 3600.0) -> task.LoopingCall:
        loop = task.LoopingCall(self.archive_cleanup_task_callback)

        # Start looping every period_s seconds.
        d = loop.start(period_s, False)

        # Add callbacks for stop and failure.
        d.addCallback(self.cbArchiveLoopDone)
        d.addErrback(self.ebArchiveLoopFailed)

        return loop

    def archive_cleanup_task_callback(self):
        if self.upload_directory is not None:
            with flask_app.app_context():
                # Get all archives
                archives = ArchiveFileData.query.all()
                for archive in archives:
                    # 1) Verify if we have an expiration date
                    if archive.archive_expiration_datetime is not None:
                        # Verify if the expiration date is passed
                        if archive.archive_expiration_datetime < datetime.datetime.now(datetime.timezone.utc):
                            # Delete the archive
                            if not archive.delete_file_archive(self.upload_directory):
                                print(f'Error deleting archive {archive.archive_uuid}')
                                self.logger.log_error('FileTransferService', f'Error deleting archive {archive.archive_uuid}.')
                            else:
                                self.logger.log_info('FileTransferService', f'Archive {archive.archive_uuid} deleted.')
                            continue
                    # 2) Verify the state of the archive, if created more than 24 hours ago and not uploaded, delete it
                    elif archive.archive_creation_datetime < datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=24):
                        if archive.archive_upload_datetime is None:
                            # Delete the archive from DB
                            self.logger.log_info('FileTransferService', f'Archive {archive.archive_uuid} deleted.')
                            try:
                                ArchiveFileData.delete(archive.id_archive_file_data)
                            except Exception as e:
                                print(f'Error deleting archive {archive.archive_uuid}')
                                self.logger.log_error('FileTransferService', f'Error deleting archive {archive.archive_uuid} : {e}.')
                            continue

    def cbArchiveLoopDone(self, result):
        """
        Called when file archive cleanup task was stopped with success.
        """
        print('cbArchiveLoopDone', result)

    def ebArchiveLoopFailed(self, failure):
        """
        Called when file archive cleanup task execution failed.
        """
        self.logger.log_error('FileTransferService', f'ebArchiveLoopFailed : {failure}.')
        print('ebArchiveLoopFailed', failure)

    def verify_file_upload_directory(self, config: ConfigManager, create=True):
        file_upload_path = config.filetransfer_config['files_directory']

        if not os.path.exists(file_upload_path):
            if create:
                # TODO Change permissions?
                os.mkdir(file_upload_path, 0o700)
            else:
                return None
        return file_upload_path

    def notify_service_messages(self, pattern, channel, message):
        pass

    # @defer.inlineCallbacks
    def register_to_events(self):
        super().register_to_events()

    def asset_event_received(self, event: messages.DatabaseEvent):
        if event.object_type == 'asset':
            if event.type == messages.DatabaseEvent.DB_DELETE:
                print("FileTransfer Service - Delete Asset Event")
                asset_info = json.loads(event.object_value)
                from services.FileTransferService.libfiletransferservice.db.models.AssetFileData import AssetFileData
                asset = AssetFileData.get_asset_for_uuid(asset_info['asset_uuid'])
                if asset:
                    flask_app.app_context().push()
                    asset.delete_file_asset(flask_app.config['UPLOAD_FOLDER'])


if __name__ == '__main__':
    # Very first thing, log to stdout
    log.startLogging(sys.stdout)

    import argparse
    parser = argparse.ArgumentParser(description='FileTransfer Service')
    parser.add_argument('--enable_tests', help='Test mode for service.', default=False)
    args = parser.parse_args()

    # Load configuration
    if not Globals.config_man.load_config('FileTransferService.json'):
        print('Invalid config')
        exit(1)

    # Global redis client
    Globals.redis_client = RedisClient(Globals.config_man.redis_config)

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

    # Update port, hostname, endpoint
    Globals.config_man.service_config['port'] = service_info['service_port']
    Globals.config_man.service_config['hostname'] = service_info['service_hostname']

    # DATABASE CONFIG AND OPENING
    #############################
    POSTGRES = {
        'user': Globals.config_man.db_config['username'],
        'pw': Globals.config_man.db_config['password'],
        'db': Globals.config_man.db_config['name'],
        'host': Globals.config_man.db_config['url'],
        'port': Globals.config_man.db_config['port']
    }

    try:
        if args.enable_tests:
            Globals.db_man.open_local(echo=True)

            # Create default values, if required
            Globals.db_man.create_defaults(config=Globals.config_man, test=True)
        else:
            Globals.db_man.open(POSTGRES, Globals.config_man.service_config['debug_mode'])
    except OperationalError as e:
        print("Unable to connect to database - please check settings in config file!", e)
        quit()

    with flask_app.app_context():
        Globals.db_man.create_defaults(Globals.config_man)

        # Create the Service
        Globals.service = FileTransferService(Globals.config_man, service_info)

        # Start App / reactor events
        reactor.run()
