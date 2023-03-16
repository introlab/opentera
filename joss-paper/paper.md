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
OpenTera is a micro-services based framework primarily developed to support tele-health research projects and real world deployment.
The framework allows the creation of backend services that are written in Python and based on key technologies and open source projects :
Redis[@redis], Flask[@Flask], SqlAlchemy[@SqlAlchemy], Twisted[@Twisted], NGINX[@NGINX], EasyWebRTC[@EasyWebRTC].

It is developed as a low cost, secure and easy to deploy alternative to existing proprietary or open source solutions.

Our goal is to have full control of the system and the produced data, alleviating the relevance on external projects and lowering costs.

It can run on embedded devices such as raspberry Pis, local servers or cloud infrastructure.

The project contains the base server (TeraServer) offering a REST API [@REST], useful to manage users,
participants, devices, sites, sessions, and supports multiple authentication methods.

TeraServer also manages authorizations for users, participants and devices, allowing us to have a precise control
of accessible information, which is required for security reasons.

OpenTera also have some base services : VideoRehab, Logging and FileTransfer.

Those base services allow WebRTC sessions from the web along with appropriate logging and file transfer possiblities.


The project is inspired by years of experience with tele-rehabilitation research with deployments in participant's home where we want to offer simple and effective way for participants and clinicians to communicate and do tele-rehabilitation sessions.


Applications of the OpenTera framework are not limited to research projects, and could also be applied in a clinical environment, where clinicians have to communicate with patients. Such fields include but are not limited to: tele-rehabilibation (physical, social, mental), robotic tele-operation and remote activity monitoring.

The project have been deployed for robot tele-operation during COVID[@panchea_opentera_2022] and is currently used for multiple rehabilitation projects since 2021.

# Statement of need

From our research experience, common features between the different tele-health projects we participated emerged:

* Data structure. The need to store data in a structured way to ease data analysis.
* Ecological data capture. The need to collect data not only in a laboratory or controlled environment, but also in the home or institution.
* Project adaptability. The need to develop projects specific dashboards while reusing as much as possible of what was done before to reduce development time.
* Security. The need to store and transfer data in a secure and controlled way.
* Uniformity. The need to have an "all-in-one" integrated solution avoiding the use of multiple windows and tools and focusing attention on the current task.

To address those common features, OpenTera was designed with an architecture based as much as possible on recognized standards and best practices.

List similar projects

Most of the recent cloud tele-health applications provided by external companies is subscription based and do not offer the flexibility we need. Each vendor offers its cloud based approch for its products and services.

We sometimes have data collections from dozens of participants and users and paying the subscription fee would be prohibitive.

We do not want to be dependant on services that can be changed over time and we need control on the data we collect.

There is many open-source solution that we can integrate that would fit our research needs.

The trade-off we decided to make is to invest in our engineering team to support custom made applications and providing support to clinicians on the field.

We also offer support to external clinics, in exchange to a minimal fee for technical support.

This might not be possible for all research teams to have such a system and sometimes chosing a commercially available and supported platform might be the solution.

Thus, “free software” is a matter of liberty, not price. To understand the concept, you should think of “free” as in “free speech,” not as in “free beer.” We sometimes call it “libre software,” borrowing the French or Spanish word for “free” as in freedom, to show we do not mean the software is gratis.



Library to ease development of new micro-services available on PyPi[@pypi_opentera].


# Related projects
Table \autoref{tab:opentera-related-projects} shows related open-source projects that are currently under active developement and implementing new services
or software libraries.

Table: OpenTera Related Projects \label{tab:opentera-related-projects}

| GitHub Project Name             | Description                                                                                         |
|---------------------------------|-----------------------------------------------------------------------------------------------------|
| opentera-webrtc                 | WebRTC library in C++/Javascript/Python with signaling server to allow audio/video/data sessions.|
| opentera-teleop-service         | OpenTera Service managing robots fleet and web front-end for tele-operation.|
| opentera-webrtc-teleop-frontend | Robot teleoperation front-end made with Vue.js[@vuejs].|
| opentera-webrtc-ros             | OpenTera robot device client and ROS integration for remote control and monitoring of mobile robots.|
| openteraplus                    | Qt Frontend to manage OpenTera configuration. Includes a chrome web engine for WebRTC sessions.|





# Acknowledgements
This work was supported by the Natural Sciences and Engineering Research Council of Canada (NSERC), the Fonds de recherche du Québec – Nature et technologies (FRQNT) and the Network of Centres of Excellence of Canada on Aging Gracefully across Environments using Technology to Support Wellness, Engagement, and Long Life (AGE-WELL). It also supported by {FONDS MICHEL}.

# References

