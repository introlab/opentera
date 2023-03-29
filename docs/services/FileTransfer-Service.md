# File Transfer Service
The file transfer service is provided as a generic file repository service. While other services can also store and
manage their own assets (files), this service could also be used instead of implementing a service that only stores 
files.

## Main script
The File Transfer service can be launched by running the 
[FileTransferService.py](https://github.com/introlab/opentera/blob/main/teraserver/python/services/FileTransferService/FileTransferService.py) 
script. As a system service, it is also launched automatically when running the 
[main OpenTera service](teraserver/teraserver.rst).

## Configuration
Configuration files for the file transfer service are similar to the basic 
[configuration files](../Configuration-files). They, however, add a specific section for that service.

### FileTransfer config section
`files_directory`: the relative or full path to store transferred files on the server.

## Default port and location
By default, the service will listen to port 4042 (non-ssl) and will be at `/file` behind the NGINX router.

## Code snippets and examples for POST, GET and DELETE

### Upload a file using POST request

Each file needs to be attached to a session. No session are created in the upload process - make sure that the session 
exists beforehand by using the appropriate [API](teraserver/api/API).

When uploading a file, you need to specify 2 mandatory components for the request:

* ``file_asset`` describing the file itself, containing at minimum the ``asset_name`` and ``id_session`` to attach the 
file to.
*  ``file`` containing the data for the file itself.

Make sure to have the token generated from the [logging](../developers/Login-and-authentication) procedure when doing 
this request.

This is a snippet of the data to send as a .json format to the server excluding the file.
For the file part you need to specify its package which depends on the library you are using to communicate
with the server.

### `file_asset` json format example

```json
{
  "file_asset": {
    "asset_name": "Asset Name",
    "id_session": 1
  }
}
```

### Python requests POST example

```python
import requests

url = "URL of the server with the FileTransfer API"

payload={'file_asset': '{"id_session": "Session number", "asset_name": "Asset Name"}'}
files=[
  ('file',('filename',open('PATH to file','rb'),'application type (ex: application/zip)'))
]
headers = {
  'Authorization': 'OpenTera {Previously obtained token}'
}

response = requests.request("POST", url, headers=headers, data=payload, files=files)

print(response.text)
```

### Testing and generating POST requests
If you want snippets in other programming languages, [PostMan](https://www.postman.com/) can be used
to test API calls and get snippets of code.

#### Using PostMan to test POST queries
To generate a **POST** request on Postman:
1. Specify the body as ``form-data`` with the ``file_asset`` and ``file`` key.
2. Select the key type as file for the ``file`` and select the file you want to upload.
3. Make sure to have a token generated from the server when logging in. This API request needs a token
in the ``Headers`` in the format: ``Authorization : OpenTera {{token}}``. The token can be set as a environment variable
that is updated when you launch the login GET request.
4. Click on the ``Code`` section and get snippets in any languages you desire.

### Download and Delete a file using GET and DELETE request

Refer to the service documentation on a running server at https://127.0.0.1:40075/file/doc

## Web URLs and REST API
**Doc page** - by default at https://127.0.0.1:40075/file/doc. Will display the [REST API](teraserver/api/API) 
documentation and test system. Useful to test queries manually.

## Web Frontend
Currently, no web front-end is available for that service

## RPC API
None. This service uses the [asynchronous communication system](../developers/Internal-services-communication-module).
