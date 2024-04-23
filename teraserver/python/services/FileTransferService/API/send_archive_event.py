from flask import request
from flask_babel import gettext
import services.FileTransferService.Globals as Globals
import opentera.messages.python as messages
from services.FileTransferService.libfiletransferservice.db.models.ArchiveFileData import ArchiveFileData


def send_archive_event(archive: ArchiveFileData):
    if Globals.service:
        servername = Globals.service.config['hostname']
        port = Globals.service.config['port']
        if 'X_EXTERNALSERVER' in request.headers:
            servername = request.headers['X_EXTERNALSERVER']

        if 'X_EXTERNALPORT' in request.headers:
            port = request.headers['X_EXTERNALPORT']

        event = messages.ArchiveEvent()
        event.status = archive.archive_status
        event.archive_uuid = archive.archive_uuid
        event.owner_uuid = archive.archive_owner_uuid
        endpoint = Globals.service.service_info['service_clientendpoint'] + '/api/archives'
        event.archive_url = f"{endpoint}?archive_uuid={archive.archive_uuid} "#f"https://{servername}:{port}{endpoint}?archive_uuid={archive.archive_uuid}"

        # Send event
        Globals.service.send_service_event_message(event)
