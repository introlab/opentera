# File Transfer Service
The file transfer service is provided as a generic file repository service. While other services can also store and manage their own assets (files), this service could also be used instead of implementing a local file manager.

## Main script
The File Transfer service can be launched by running the [FileTransferService.py](https://github.com/introlab/opentera/blob/main/teraserver/python/services/FileTransferService/FileTransferService.py) script. As a system service, it is also launched automatically when running the [main OpenTera service](teraserver/TeraServer-Service)

## Configuration
Configuration files for the file transfer service are similar to the basic [configuration files](../Configuration-files). They however add a specific section for that service.

### FileTransfer config section
`upload_directory`: the relative or full path to store transferred files.

## Default port and location
By default, the service will listen to port 4042 (non-ssl) and will be at `/file` behind the NGINX router.

## Code snippets and examples for POST, GET and DELETE

**Upload a file using POST request**

When uploading a file, you need to specify 2 mandatory components for the request.
The ``file_asset`` containing the ``asset_name`` and ``id_session``.
The ``file`` containing the data for the file itself.

Make sure to have the token generated from the logging procedure when doing this request.

This is a snippet of the data to send as a .json format to the server excluding the file.
For the file part you need to specify its package which depends on the library you are using to communicate
with the server.

**Snippet of the .json format**

```json
{
  "file_asset": {
    "asset_name": "Asset Name",
    "id_session": 1
  }
}
```

**Here is an example for Python Requests**

```python
import requests

url = "URL of the server with the FileTransfer API"

payload={'file_asset': '{"id_session": "Session number", "asset_name": "Asset Name"}'}
files=[
  ('file',('filename',open('PATH to file','rb'),'application type (ex: application/zip)'))
]
headers = {
  'Authorization': 'OpenTera {Previously generated token}'
}

response = requests.request("POST", url, headers=headers, data=payload, files=files)

print(response.text)
```

If you want snippets of any other HTTP libraries, https://www.postman.com/ could be used
to test API calls and get snippets of code.

For this **POST** request on Postman, specify the body as ``form-data`` with the ``file_asset`` and ``file`` key.
Select the key type as file for the ``file`` and select the file you want to upload.
Make sure to have a token generated from the server when logging in. This API request needs a token
in the ``Headers`` like so ``Authorization : OpenTera {{token}}``. The token can be set as a environment variable
that is updated when you launch the login GET request.

Lastly, you can click on the ``Code`` section and get snippets in any languages you desire.

**Download and Delete a file using GET and DELETE request**

Refer to the documentation at https://127.0.0.1:40075/file/doc

## Web URLs (if enabled)
**Doc page** - by default at https://127.0.0.1:40075/file/doc. Will display the [REST API](teraserver/api/API) documentation and test system. Useful to test queries manually.
