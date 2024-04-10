import pathlib
import sys
import os
import json
import argparse
from opentera.config.ConfigManager import ConfigManager
from opentera.redis.RedisClient import RedisClient
from opentera.db.models.TeraAsset import TeraAsset
from opentera.db.models.TeraService import TeraService
from opentera.db.models.TeraSession import TeraSession
from opentera.db.models.TeraParticipant import TeraParticipant

import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='AssetsArchiveWorker')
    parser.add_argument('--config', help='Configuration file.', default='config/TeraServerConfig.ini')
    parser.add_argument('--job_id', help='Unique job id to execute, fetched from redis')
    parser.add_argument('--verify', help='Verify certificate', default=False)
    args = parser.parse_args()

    # Load configuration
    config = ConfigManager()
    config.load_config(args.config)

    # Setup DB
    db_url = 'postgresql://%(username)s:%(password)s@%(url)s:%(port)s/%(name)s' % config.db_config
    db_engine = create_engine(db_url, echo=False)

    # Create a sessionmaker
    SessionMaker = sessionmaker(bind=db_engine)

    # Load redis job info
    redis_client = RedisClient(config.redis_config)
    job_info = json.loads(redis_client.redisGet(args.job_id))

    if 'service_key' not in job_info:
        print('Service key not found in job info')
        sys.exit(1)

    if 'server_name' not in job_info:
        print('Server name not found in job info')
        sys.exit(1)

    if 'port' not in job_info:
        print('Port not found in job info')
        sys.exit(1)

    if 'assets' not in job_info:
        print('Assets not found in job info')
        sys.exit(1)

    server_name = job_info['server_name']
    port = job_info['port']
    service_key = job_info['service_key'].encode('utf-8')

    for asset in job_info['assets']:
        with (SessionMaker() as db_session):
            path = asset['path'] if 'path' in asset else ''

            # Query service from database
            service: TeraService = db_session.query(TeraService) \
                .filter(TeraService.service_uuid == asset['asset_service_uuid']).first()

            if service is None:
                continue

            service_token = service.get_token(service_key)

            # Generate key for asset, request by service
            access_token = TeraAsset.get_access_token([asset['asset_uuid']], service_key,
                                                      asset['asset_service_uuid'])

            # Generate headers to request file
            headers = {'Authorization': 'OpenTera ' + service_token}
            params = {'access_token': access_token, 'asset_uuid': asset['asset_uuid']}

            # Request file from service
            url = 'https://' + server_name + ':' + str(port) + service.service_clientendpoint + '/api/assets'

            # Certificate will be verified if verify arg is True
            response = requests.get(url=url, params=params, headers=headers, verify=args.verify)

            if response.status_code == 200:
                # Save file
                file_size = len(response.content)


    print(config, job_info)