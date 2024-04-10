import pathlib
import sys
import os
import json
import argparse
from datetime import datetime
from opentera.config.ConfigManager import ConfigManager
from opentera.redis.RedisClient import RedisClient
from opentera.db.models.TeraAsset import TeraAsset
import zipfile
from io import BytesIO
import requests
import tempfile


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='AssetsArchiveWorker')
    parser.add_argument('--config', help='Configuration file.', default='config/TeraServerConfig.ini')
    parser.add_argument('--job_id', help='Unique job id to execute, fetched from redis')
    parser.add_argument('--verify', help='Verify certificate', default=False)
    args = parser.parse_args()

    start_time = datetime.now()

    # Load configuration
    config = ConfigManager()
    config.load_config(args.config)

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

    if 'assets_map' not in job_info:
        print('Assets not found in job info')
        sys.exit(1)

    server_name = job_info['server_name']
    port = job_info['port']
    service_key = job_info['service_key'].encode('utf-8')

    # Create an in-memory binary stream to store the zip file
    # zip_buffer = BytesIO()

    # Create a temporary file to store the zip file, deleted when closed
    zip_buffer = tempfile.NamedTemporaryFile(delete=True)

    # Create a ZipFile object to write to the in-memory stream
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:

        for _, service_data in job_info['assets_map'].items():
            for asset in service_data['service_assets']:

                path = asset['path'] if 'path' in asset else ''
                service_token = service_data['service_token']

                # Generate key for asset, request by service
                access_token = TeraAsset.get_access_token([asset['asset_uuid']], service_key,
                                                          asset['asset_service_uuid'])

                # Generate headers to request file
                headers = {'Authorization': 'OpenTera ' + service_token}
                params = {'access_token': access_token, 'asset_uuid': asset['asset_uuid']}

                # Request file from service
                url = 'https://' + server_name + ':' + str(port) + service_data['service_endpoint'] + '/api/assets'

                # Certificate will be verified if verify arg is True
                response = requests.get(url=url, params=params, headers=headers, verify=args.verify)

                if response.status_code == 200:
                    # Add to zip file
                    file_path = pathlib.Path(path) / pathlib.Path(f"[{asset['asset_uuid']}]_{asset['asset_name']}")
                    # Compress
                    zip_file.writestr(str(file_path), response.content)

    # Set the BytesIO object's position to the beginning
    zip_buffer.seek(0)

    # Transfer file to file transfer service


    # Close will automatically delete file
    zip_buffer.close()
    end_time = datetime.now()
    duration_s = (end_time - start_time).total_seconds()
    print(f"Duration: {duration_s}")



    print(config, job_info)