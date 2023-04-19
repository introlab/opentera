# About OpenTera

[![Actions Status](https://github.com/introlab/opentera/actions/workflows/python-package-pypi.yml/badge.svg)](https://github.com/introlab/opentera/actions)

OpenTera is a micro-services based backend primarily built to support research projects. Focusing on years in the research field, common features between the different projects emerged:

* Data structure: The need to store data in a structured way to ease data analysis
* Ecological data capture: The need to collect data not only in a laboratory or controlled environment, but also in the home
* Project adaptability: The need to develop projects specific dashboards while reusing as much as possible of what was done before to reduce development time
* Security: The need to store and transfer data in a secure and controlled way

To address those common features, OpenTera was designed with an architecture based as much as possible on recognized standards and best practices.

## Documentation
* https://introlab.github.io/opentera/

## What can OpenTera do for you?

In its essence, OpenTera provides an adaptable data structure on which you can base your developments. With its modular and service-based design, it is possible to tailor specific needs based on the OpenTera framework.

Applications of the OpenTera backend are not limited to research projects, and could also be applied in a clinical environment, where clinicians have to communicate with patients. Such fields include but are not limited to: tele-rehabilibation (physical, social, mental), robotic tele-operation and remote activity monitoring.

The OpenTera micro-services structure allows:

* Management of several sites, users, projects, participants, groups of participants, connected devices, sessions, data sources, assets in a structured manner.
  * We developed a Qt management tool called [OpenTeraPlus](https://github.com/introlab/openteraplus), which is also under developement.
  * A web management interface will be developed in the future.
* Easy and secure deployment on any cloud, dedicated or embedded platform(such as a Raspberry Pi, AWS, Azure)
* Easy to use for elderly participants (no configuration, interfaces adapted to clients needs).
* Better collaboration / dissemination for open code.
* Support for several current and future research projects:
  * [INTER](https://regroupementinter.com/) - Tele-Actimetry: connected watches, portable capture devices.
  * [INTER](https://regroupementinter.com/) - Tele-Rehabilitation: videoconference, management of rehabilitation sessions for participants using tele-rehabilitation.
  * [INTER](https://regroupementinter.com/) - Active desk: Management of active desks and data visualization in the form of a dashboard.
  * [INTER](https://regroupementinter.com/) - [OpenIMU](https://github.com/introlab/OpenIMU), [OpenIMU-MiniLogger](https://github.com/introlab/OpenIMU-MiniLogger): Capture, visualization and analysis of data from inertial measurement units.
  * [AGEWELL](https://agewell-nce.ca/research/research-programs-and-projects) (SMART, [MOvIT+](https://github.com/introlab/MOvITPlus)): Tele-presence and assistance of elderly people at home by a mobile robot, and power wheelchairs instrumentation and usage monitoring.

You are welcome to participate in this effort. Leave us comments or report [Issues](https://github.com/introlab/opentera/issues).

## Authors

* Dominic Létourneau, ing. M.Sc.A., IntRoLab, Université de Sherbrooke (@doumdi)
* Simon Brière, ing. M.Sc.A., CDRV, Université de Sherbrooke (@sbriere)
* François Michaud, ing. Ph.D., IntRoLab, Université de Sherbrooke
* Michel Tousignant, pht, Ph.D., CDRV, Université de Sherbrooke


## Contributors

* Philippe Arsenault
* Cédric Godin
* Marc-Antoine Maheux
* Cynthia Vilanova

## Publication(s)

* Panchea, A.M., Létourneau, D., Brière, S. et al., [OpenTera: A microservice architecture solution for rapid prototyping of robotic solutions to COVID-19 challenges in care facilities](https://rdcu.be/cHzmf),  Health Technol. 12, 583–596 (2022)

## Videos

### OpenTera Telehealth Platform

[![OpenTera Telehealth Platform](https://img.youtube.com/vi/s5XVIDCP8_s/maxresdefault.jpg)](https://youtu.be/s5XVIDCP8_s)

### OpenTera+ Clinical Telehealth Software

[![OpenTera+ Clinical Telehealth Software](https://img.youtube.com/vi/4YMKSUE6xJs/maxresdefault.jpg)](https://youtu.be/4YMKSUE6xJs)

## Documentation and getting started

Detailled information is available in the [docs](https://introlab.github.io/opentera/)

## License

OpenTera is licensed under [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0.txt) .

## Related Open Source Projects

### General

* [OpenTeraPlus Desktop Application](https://github.com/introlab/openteraplus)
* [OpenTera WebPortal Service](https://github.com/introlab/opentera-webportal-service)

### Robots

* [WebRTC Native Libraries](https://github.com/introlab/webrtc-native-build)
* [OpenTera WebRTC Libraries](https://github.com/introlab/opentera-webrtc)
* [OpenTera WebRTC ROS Client and Nodes](https://github.com/introlab/opentera-webrtc-ros)
* [OpenTera Teleoperation Service](https://github.com/introlab/opentera-teleop-service)
* [OpenTera WebRTC Teleoperation Frontend](https://github.com/introlab/opentera-webrtc-teleop-frontend)

## Dependencies

OpenTera is based or uses the following Open Source technologies :

* [Python 3.8+, PSFL (BSD like)](https://www.python.org)
* [Flask, BSD](http://flask.pocoo.org)
* [Redis, BSD](https://redislabs.com/why-redis/)
* [txredisapi, Apache License 2.0](https://github.com/fiorix/txredisapi)
* [SQLAlchemy, MIT](https://www.sqlalchemy.org)
* [Twisted, MIT](https://twistedmatrix.com)
* [PostgreSQL,  PostgreSQL License(MIT/BSD like)](https://www.postgresql.org)
* [Node.js, Node license](https://nodejs.org/en/)

## Sponsors

<table style="width:100%">
  <tr>
    <td align="center">
        <img src="teraserver/python/services/VideoRehabService/static/images/logos/IntRoLab.png" width="200">
        <img src="teraserver/python/services/VideoRehabService/static/images/logos/Estrad.png" width="200">
        <img src="teraserver/python/services/VideoRehabService/static/images/logos/3IT.png" width="200">
    </td>
  </tr>
  <tr>
    <td align="center">
        <img src="teraserver/python/services/VideoRehabService/static/images/logos/logo_CDRV.png" width="200">
        <img src="teraserver/python/services/VideoRehabService/static/images/logos/AgeWell.png" width="200">
        <img src="teraserver/python/services/VideoRehabService/static/images/logos/INTER.png" width="200">
    </td>
  </tr>
</table>
