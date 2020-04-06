![Analytics](https://ga-beacon.appspot.com/UA-27707792-8/github-opentera-main?pixel) 

# OpenTera
We are developing an “Open Source” micro-services structure which will allow:
* Management of several sites, users, projects, participants, groups of participants, connected devices, sessions, data sources in a structured manner.
  * [OpenTeraPlus](https://github.com/introlab/openteraplus) Qt management tool is under developement.
* Easy and secure deployment on any cloud platform, dedicated or embedded (such as a Raspberry Pi, AWS, Azure)
* Easy to use for elderly participants (no configuration, interfaces adapted to customers).
* Better collaboration / dissemination for open code.
* Support for several current and future projects:
  * INTER - Tele-Actimetry: connected watches, portable capture devices. 
  * INTER - Tele-Rehabilitation: videoconference, management of sessions by participants for tele-rehabilitation. 
  * INTER - Active Office: Management of active offices and visualization of data in the form of a dashboard. 
  * INTER - [OpenIMU](https://github.com/introlab/OpenIMU), [OpenIMU-MiniLogger](https://github.com/introlab/OpenIMU-MiniLogger): Capture and visualization of data from inertial units.
  * AGEWELL (SMART, [MOvIT+](https://github.com/introlab/MOvITPlus)): Tele-presence and assistance of elderly people at home by a mobile robot and power wheelchairs. 

We focused our first efforts on systems that transmit data on a daily basis (in batch) to archive data on our servers and allow the recovery of this data for offline analysis by people with "permissions". We are currently working on the videoconference part for the tele-rehabilitation and tele-robot operation sessions. The IOT development hasn't started yet. However, this is a service that we would like to develop in the future and it would be a very interesting addition to the OpenTera platform. You are welcome to participate in this effort.

# News
* (April 2020) We made a quick COVID-19 videoconference dispatch center using OpenTera. The idea is to have a form that we fill out online and that gives us an appointment for a videoconference. For now it does not send emails and it gives a direct connection link. The central takes calls in order with the aim of using remote resource persons (retired nurses from home) who could help people navigate the health system better depending on the severity of the symptoms.
  * WARNING - This is a prototype only, not for production. Use at your own risks.
  * You can use the [docker image](https://hub.docker.com/repository/docker/introlab3it/openteraserver) for quick tests. Make sure your local port is 40075. Certificates are self signed and you will get a warning from the browser when navigating to the following urls:
    * Patient interface to register and test the registration form : https://localhost:40075/videodispatch/
    * Simple Dispatcher Demo for medical staff : https://localhost:40075/videodispatch/login. Use admin/admin for login and password.


# License
OpenTera is licensed under [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0.txt) . 

# Dependencies
OpenTera is based or uses the following Open Source Technologies :
* [Python 3.6+, PSFL (BSD like)](https://www.python.org)
* [Flask, BSD](http://flask.pocoo.org)
* [Redis, BSD](https://redislabs.com/why-redis/)
* [txredisapi, Apache License 2.0](https://github.com/fiorix/txredisapi) 
* [SQLAlchemy, MIT](https://www.sqlalchemy.org)
* [Twisted, MIT](https://twistedmatrix.com)
* [PostgreSQL,  PostgreSQL License(MIT/BSD like)](https://www.postgresql.org)
* [Node.js, Node license](https://nodejs.org/en/)

# Authors
* Dominic Létourneau, ing. M.Sc.A., IntRoLab, Université de Sherbrooke (@doumdi)
* Simon Brière, ing. M.Sc.A., CDRV, Université de Sherbrooke (@sbriere)

# Sponsors
![IntRoLab](teraserver/python/ervices/VideoDispatch/static/images/logos/IntRoLab.png)
![Estrad](teraserver/python/ervices/VideoDispatch/static/images/logos/Estrad.png)
![3IT](teraserver/python/ervices/VideoDispatch/static/images/logos/3IT.png)
![CDRV](teraserver/python/ervices/VideoDispatch/static/images/logos/logo_CDRV.png)
![AgeWell](teraserver/python/ervices/VideoDispatch/static/images/logos/AgeWell.png)
![INTER](teraserver/python/ervices/VideoDispatch/static/images/logos/INTER.png)