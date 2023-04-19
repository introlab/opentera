TeraServer Service
==================
The TeraServer service is the core service of the OpenTera platform. It runs the different
`modules <../../Architecture-Overview>`_ of the platform. An OpenTera server cannot exist without that service!

===========
Main script
===========
The TeraServer service can be launched by running the
`TeraServer.py <https://github.com/introlab/opentera/blob/main/teraserver/python/TeraServer.py>`_ script.

=============
Configuration
=============
Configuration files for the TeraServer service are described `here <../../Configuration-files>`_.

=========================
Default port and location
=========================
By default, the service will listen to port 4040 (non-ssl) and will be at the root of the web server url (/).

========
Web URLs
========
**About page** - by default at `https://127.0.0.1:40075/about <https://127.0.0.1:40075/about>`_. Will display the about
page of the server, including the version and possible `OpenTeraPlus <https://github.com/introlab/openteraplus>`_ client
versions available to download

**Doc page** - by default at `https://127.0.0.1:400075/doc <https://127.0.0.1:400075/doc>`_. Will display the
`REST API <api/API>`_ documentation and test system. This can be used to test the API. Please not that this URL will not
be available if not enabled in the `configuration file <../../Configuration-files>`_.

===============
Specific topics
===============
.. toctree::
   :maxdepth: 1

   OpenTera_AccessRoles.md
   UserManager-module.md
   Using REST API <api/API.md>
   api/api_doc
