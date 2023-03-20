---
title: 'OpenTera : A Microservice Framework Allowing Structured and Customized Tele-Health Sessions'
tags:
  - Python
  - Microservices
  - Tele-Health
  - Rehabilitation
  - Robotics
  - Telepresence
  - Serious Games
  - Exergames
  
authors:
  - name: Dominic Létourneau
    orcid: 0000-0001-7825-7533
    affiliation: 1
  - name: Simon Brière
    orcid: 0009-0000-1224-8001
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
OpenTera is a micro-services based framework primarily developed to support tele-health research projects and real world
deployment. This project is based on many years of experience linking at-home participants to remote users (such as
clinicians) with audio-video-data connections and in-the-field sensor (such as biometrics, activities and robotics
devices).

Most telehealth based research projects requires a common data structure: data collect sites, projects, participants
and sessions including various recorded data types (from sensors or other sources). Those projects also require many common low-level features: user
authentification based on various access roles, ability to add new features based on specific projects needs,
ease of use for the participant and secure data hosting. Some common features are also shared between research projects: videoconferencing
with specific health related features (angles measurement, timers, etc.), surveys data collection, data analysis and
export.

Since many of the available solutions are either costly, features limited, proprietary (e.g. can't be easily adapted for
research purpose and raw data is harder to access) or hard to deploy in a tele-health context, OpenTera was built to
allow for extensability over the various projects needs and to provide research project full control over their data and
hosting.

Applications of the OpenTera framework are not limited to research projects, and can also be applied in a clinical
environment, where clinicians have to communicate with patients. Such fields include but are not limited to:
tele-rehabilibation (physical, social, mental), robotic tele-operation and remote activity monitoring.

The project has been open sourced to make it available to a larger audience, but was developed internally since 2013.

#### ---- Ideas - remove if not needed ----
The framework allows the creation of backend services that are written in Python and based on key technologies and open source projects :
Redis[@redis], Flask[@Flask], SqlAlchemy[@SqlAlchemy], Twisted[@Twisted], NGINX[@NGINX], EasyWebRTC[@EasyWebRTC].

It is developed as a low cost, secure and easy to deploy alternative to existing proprietary or open source solutions.

Our goal is to have full control of the system and the produced data, alleviating the relevance on external projects and lowering costs.

It can run on embedded devices such as raspberry Pis, local servers or cloud infrastructure.

The project contains the base server (TeraServer) offering a REST API [@REST], useful to manage users,
participants, devices, sites, projects, sessions, and supports multiple authentication methods.

TeraServer also manages authorizations for users, participants and devices, allowing us to have a precise control
of accessible information, which is required for security reasons.

OpenTera also have some base services : VideoRehab, Logging and FileTransfer.

Those base services allow WebRTC sessions from the web along with appropriate logging and file transfer possiblities.

The project is inspired by years of experience with tele-rehabilitation research with deployments in participant's home where we want to offer simple and effective way for participants and clinicians to communicate and do tele-rehabilitation sessions.

The project have been deployed for robot tele-operation during COVID[@panchea_opentera_2022] and is currently used for multiple rehabilitation projects since 2021.

# Statement of need

From our research experience, common features between the different tele-health projects we participated emerged:

* Data structure. The need to store data in a structured way to ease data analysis.
* Ecological data capture. The need to collect data not only in a laboratory or controlled environment, but also in the home or institution.
* Project adaptability. The need to develop projects specific dashboards while reusing as much as possible of what was done before to reduce development time.
* Security. The need to store and transfer data in a secure and controlled way.
* Uniformity. The need to have an "all-in-one" integrated solution avoiding the use of multiple windows and tools and focusing attention on the current tele-health task.
* Ease of use. The need to have an easy to use solution for the user and the participant at all steps of the process (authentification, data collection, data management)

To address those common features, OpenTera was designed with an architecture based as much as possible on recognized standards and best practices.

There are many open-source solutions that can be integrated and could solve the identified needs, but none of those would
fit those needs completely and would require customization at some level that can quickly gets limitative or complicated.



- Ease of use through a web browser (for participants) is mandatory. Use participant's mobile or desktop devices. Avoid complicated installation of apps and login / password / registration.
- Avoid long list of "friends" for communication where we need to click the right person and start a conference.
- Use unique link to authenticate, automate the start of sessions with clinicians.
- Explain Asynchronous / Synchonous sessions.

- Applications are hard to install in healthcare applications and distribution over the web is easier.
- Network access is complicated, need to minimize non standard ports for easier access.
- Need central and secured place to put assets and manage backups.
- Not duplicating the Electronic Health/Medical Record (EHR/EMR) and avoid storing sensitive information if possible.
- Integration of research surveys
- Actimetry device integration
- Long term availablity, not often the case with proprietary solutions.
- Customization, still require technical knowledge.
- Need more than tele-consultation (videoconference) with chat and file sharing.

https://www.computerworld.com/article/3596891/10-open-source-videoconferencing-tools-for-business.html

TODO: Need to chose features to compare

There are several open source videoconferencing systems that could be used in tele-health scenarios. The table \ref{tab:open-source-videoconferencing} summarizes the important features and compares to what is developed in OpenTera.

Table: Open Source VideoConferencing Solutions Comparison \label{tab:open-source-videoconferencing}

|Project              | Audio | Video | Chat |Max Group | Devices| Organized Data | Rehab Tools | Usage Stats  | Security | Planning     | Web |
|---------------------|-------|-------|------|----------|--------|----------------|-------------|--------------|----------|--------------|-----|
| Jitsi               |
| Big Blue Button     |
| OpenMeetings        |
| NextCloud Talk      |
| Jami                |
| OpenVidu            |
| OpenTera            |

TODO:  Maybe we should focus on open source rehab solutions
https://www.goodfirms.co/telemedicine-software/
https://blog.containerize.com/top-5-open-source-video-conferencing-software-of-2021/


Talk about HIPPAA Compliance ?



[VSee](https://vsee.com/)
- HIPAA
- 

- [OpenRehab](https://openrehab.org/)
  - Web Site with a listing of rehabilitation tools for : Upper Limb, Mobility, Fitness, Cognition, Balance.

  - [VERA](https://www.cmrehabnetwork.nhs.uk/uploadedfiles/documents/Development%20of%20VERA%20Ganesh%20Bavikatte%20Jo%20Haworth%20Nic%20Branscombe%20Charlotte%20Lawrence.pdf):
    - Open ??? Did not find any web site / source repository.


- REHAB
- [OPEN FEASYO](https://openfeasyo.org/)
  - Games : https://github.com/openfeasyo/OpenFeasyo using EMG sensors.
  - 
  - 
- 
- [Intelehealth](https://github.com/Intelehealth)
- 
- 
- [OpenPT]()
- [PhysiTrack](https://www.physitrack.fr/)
  - Subscription based
  - Exercices

- [RehApp]()
- [RehabMe](https://github.com/djvolz/RehabMe) -->DEPRECATED
- [PhysioCam]()


- Serious games : Games with an additional purpose other than its original objective which is the seeking of enjoyment. For instance, rehabilitation of upper limbs.
  
- Exergames : Games that involve physical exertion and are thought of as a form of exercise.
  
Focus on live sessions with clinician.


Most of the recent commercial cloud tele-health applications provided is subscription based and do not offer the flexibility we need. Each vendor offers its own approch tailored for its products and services.

We often have data collections from dozens of participants and users and paying the subscription fee would be prohibitive.

We do not want to be dependant on services that can be changed over time and we need control on the data we collect.


Library to ease development of new micro-services available on PyPi[@pypi_opentera].


# Related projects
Table \autoref{tab:opentera-related-projects} shows related open-source projects that are currently under active developement and implementing new OpenTera services or underlying libraries.

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

