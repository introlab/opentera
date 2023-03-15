---
title: 'OpenTera : A Microservice Framework Allowing Structured and Customized Tele-Health Sessions'
tags:
  - Python
  - Microservices
  - Tele-Health
  - Rehabilitation
  - Robotics
  - Telepresence
authors:
  - name: Dominic Létourneau
    orcid: 0000-0001-7825-7533
    affiliation: 1
  - name: Simon Brière
    orcid: 0000-0000-0000-0000
    affiliation: 2    
  - name: François Michaud
    orcid: 0000-0002-3639-7770
    affiliation: 1
  - name: Michel Tousignant
    orcid: 0000-0001-7561-1170
    affiliation: 2  
affiliations:
  - name: Interdisciplinary Institute for Technological Innovation (3IT), Université de Sherbrooke, Canada
    index: 1
  - name: Research Center on Aging (CDRV), Université de Sherbrooke, Canada
    index: 2

date: March 15 2023
bibliography: paper.bib
---

# Summary
OpenTera is a micro-services based framework primarily developed to support tele-health research projects.
The framework allows the creation of backend services in Python based on key technologies and open source projects : 
Redis[@redis], Flask[@Flask], SqlAlchemy[@SqlAlchemy], Twisted[@Twisted], NGINX[@NGINX], EasyWebRTC[@EasyWebRTC].
It is developed as a low cost, secure and easy to deploy alternative to existing proprietary or open source solutions.
The project contains the base server (TeraServer) offering a REST API, useful to manage users, 
participants, devices, sites, sessions, and supports multiple authentication methods. 
OpenTera also have some base services : VideoRehab, Logging and FileTransfer that enable WebRTC sessions along with appropriate
user web interface and data collection especially tailored for clinicians. The project is inspired by years of experience with tele-rehabilitation research with deployments in participant's home where we want to offer simple and effective way for participants and clinicians to communicate and do tele-rehabilitation sessions. 
The project has been developed to also support tele-operation of mobile robots and data collection from wearable devices or any source of data like surveys. 
Assets that are associated with a session can contain multiple user, participant and devices. 
The system has also been deployed for robot tele-operation during COVID[@panchea_opentera_2022].


# Statement of need
Focusing on years in the research field, common features between the different projects emerged:

* Data structure: The need to store data in a structured way to ease data analysis.
* Ecological data capture: The need to collect data not only in a laboratory or controlled environment, but also in the home or institution.
* Project adaptability: The need to develop projects specific dashboards while reusing as much as possible of what was done before to reduce development time.
* Security: The need to store and transfer data in a secure and controlled way.

To address those common features, OpenTera was designed with an architecture based as much as possible on recognized standards and best practices.



Library to ease development of new micro-services available on PyPi[@pypi_opentera].


# Related projects
Table \autoref{tab:opentera-related-projects} shows related projects implementing components required to build a robot tele-operation
application. 

Table: OpenTera Related Projects \label{tab:opentera-related-projects}

| GitHub Project Name             | Description                                                                                   |            
|---------------------------------|---------------------------------------------------------------------------------------------------|
| opentera-webrtc                 | WebRTC library in C++/Javascript/Python with signaling server to allow audio/video/data sessions. |
| opentera-teleop-service         | OpenTera Service managing sessions and web front-end.                                             |
| opentera-webrtc-teleop-frontend | Robot teleoperation front-end made with Vue.js.                                                   |
| openteraplus                    | QT Frontend for management and session configuration.                                             |



# Acknowledgements
This work was supported by the Natural Sciences and Engineering Research Council of Canada (NSERC), the Fonds de recherche du Québec – Nature et technologies (FRQNT) and the Network of Centres of Excellence of Canada on Aging Gracefully across Environments using Technology to Support Wellness, Engagement, and Long Life (AGE-WELL). It also supported by {FONDS MICHEL}.

# References

