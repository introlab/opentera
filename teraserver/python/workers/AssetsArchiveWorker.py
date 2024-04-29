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

    if 'server_name' not in job_info:
        print('server_name not found in job info')
        sys.exit(1)

    if 'service_key' not in job_info:
        print('service_key not found in job info')
        sys.exit(1)

    if 'service_token' not in job_info:
        print('service_token not found in job info')
        sys.exit(1)

    if 'port' not in job_info:
        print('port not found in job info')
        sys.exit(1)

    if 'archive_file_infos_url' not in job_info:
        print('archive_file_infos_url not found in job info')
        sys.exit(1)

    if 'archive_file_upload_url' not in job_info:
        print('archive_file_upload_url not found in job info')
        sys.exit(1)

    if 'assets_map' not in job_info:
        print('Assets not found in job info')
        sys.exit(1)

    if 'archive_info' not in job_info:
        print('Archive info not found in job info')
        sys.exit(1)

    server_name = job_info['server_name']
    service_key = job_info['service_key']
    service_token = job_info['service_token']
    port = job_info['port']
    archive_file_infos_url = job_info['archive_file_infos_url']
    archive_file_upload_url = job_info['archive_file_upload_url']
    archive_info = job_info['archive_info']

    # Create an in-memory binary stream to store the zip file
    # zip_buffer = BytesIO()

    # Change status of the file transfer to 'in progress'
    archive_info['archive_status'] = 1  # STATUS_INPROGRESS
    response = requests.post(archive_file_infos_url, json={'archive': archive_info},
                             headers={'Authorization': 'OpenTera ' + job_info['service_token']},
                             timeout=30, verify=args.verify)

    # Create a temporary file to store the zip file, deleted when closed
    zip_buffer = tempfile.NamedTemporaryFile(delete=True)

    # Create a ZipFile object to write to the in-memory stream
    with (zipfile.ZipFile(zip_buffer, 'w') as zip_file):
        files_in_zip = {}
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
                # url = 'https://' + server_name + ':' + str(port) + service_data['service_endpoint'] + '/api/assets'
                url = f'http://{service_data["service_hostname"]}:{service_data["service_port"]}/api/assets'

                # Certificate will be verified if verify arg is True
                response = requests.get(url=url, params=params, headers=headers, timeout=300, verify=args.verify)

                if response.status_code == 200:
                    # Add to zip file
                    # file_path = pathlib.Path(path) / pathlib.Path(f"[{asset['asset_uuid']}]_{asset['asset_name']}")
                    file_path = pathlib.Path(path) / pathlib.Path(f"{asset['asset_name']}")

                    if file_path in files_in_zip:
                        files_in_zip[file_path] = files_in_zip[file_path] + 1
                        # File with that name already exists - insert number
                        file_name_ext = '.' + asset['asset_name'].split('.')[-1]
                        file_name = asset['asset_name'].removesuffix(file_name_ext) + '(' + \
                            str(files_in_zip[file_path]) + ')' + file_name_ext
                        file_path = pathlib.Path(path) / pathlib.Path(f"{file_name}")
                    else:
                        files_in_zip[file_path] = 1
                    # Compress
                    zip_file.writestr(str(file_path), response.content)

    # Set the BytesIO object's position to the beginning
    zip_buffer.seek(0)

    # Upload file to file transfer service
    response = requests.post(archive_file_upload_url,
                             files={'file': (archive_info['archive_original_filename'], zip_buffer)},
                             data={'archive': json.dumps(archive_info)},
                             timeout=30,
                             headers={'Authorization': 'OpenTera ' + job_info['service_token']}, verify=args.verify)

    # Close will automatically delete file
    zip_buffer.close()
    end_time = datetime.now()
    duration_s = (end_time - start_time).total_seconds()
    print(f"Duration: {duration_s}, return code: {response.status_code}")
    sys.exit(0)
