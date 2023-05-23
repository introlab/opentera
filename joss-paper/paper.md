---
title: 'OpenTera: A Framework for Telehealth Applications'
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
    orcid: 0009-0000-1224-8001
    affiliation: 2

  - name : Marc-Antoine Maheux
    orcid : 0000-0002-3983-8754
    affiliation : 1

  - name: Cédric Godin
    affiliation : 1

  - name : Philippe Warren
    orcid : 0009-0008-4466-0963
    affiliation : 1

  - name : Gabriel Lauzier
    affiliation: 1

  - name: Ian-Mathieu Joly
    affiliation: 1

  - name: Jérémie Bourque
    orcid: 0009-0008-5868-9724
    affiliation : 1

  - name: Philippe Arsenault
    orcid: 0009-0003-0772-1177
    affiliation: 1

  - name: Cynthia Vilanova
    affiliation : 2

  - name: Michel Tousignant
    orcid: 0000-0001-7561-1170
    affiliation: 2

  - name: François Michaud
    orcid: 0000-0002-3639-7770
    affiliation: 1

affiliations:

  - name: Interdisciplinary Institute for Technological Innovation (3IT), Université de Sherbrooke, Canada
    index: 1

  - name: Research Center on Aging (CDRV), Université de Sherbrooke, Canada
    index: 2

date: April 6 2023
bibliography: paper.bib
---

# Summary

OpenTera is a microservice based framework primarily developed to support telehealth research projects and real-world deployment. This project is based on 20 years of experience linking at-home participants to remote users (such as clinicians, researchers, healthcare professionals) with audio-video-data connections and in-the-field sensors, such as biometrics, wearable and robotics devices. Applications of the OpenTera framework are not limited to research projects and can also be used in clinical environments.
Most telehealth-based research projects require a common data structure: data collection sites, projects, participants and sessions including various recorded data types from sensors or other sources. They also require many common features: user authentication based on various access roles, ability to add new features based on specific project needs, ease of use for the participant, and secure data hosting.  These features are also shared between research projects: videoconferencing with specific health related features (e.g., angles measurement, timers), surveys data collection, data analysis and exportation.

Many of the available solutions are either costly, feature limited, proprietary (e.g., can hardly be adapted for research purposes and raw data is harder to access) or hard to deploy in a telehealth context. OpenTera was built for extensibility to provide research projects full control over their data and hosting.

# Statement of need

From our research experience, common features between the different telehealth projects emerged:

* **Data structure.** Store data in a structured way to ease data extraction and analysis.
* **Ecological data capture.** Collect data not only in laboratories or controlled environments, but also in homes or institutions.
* **Project adaptability.** Develop project-specific dashboards and user interfaces while reusing what was previously implemented as much as possible of to reduce development time. Rehabilitation projects may require implementing serious games or exergames, while teleoperation projects may require real-time navigation tools. Adapting already existing open-source software when possible is often the key.
* **Cost effectiveness.** Most of the recent commercial cloud telehealth applications available are subscription-based and do not offer the flexibility needed. Each vendor offers its own approach tailored for its products and services. We often have data collections from dozens of participants and users, and paying subscription fees would be prohibitive.
* **Security.** Store and transfer data in a secure and controlled way. Access control to information depends on specific project requirements. Research projects involving participants must be approved by the ethics committee, and they often require servers hosted locally or in a specific region.
* **Uniformity.** Avoid the use of multiple applications and tools that would require the user to navigate between them (minimizing and restoring them as needed) and focusing attention on the current task.
* Ease of use. Implement an easy-to-use solution for users and participants at all steps of the process, I.e., authentication, data collection, data management.
* **Synchronous and asynchronous sessions.** Support real-time sessions (synchronous) or on-demand pre-recorded or application-based sessions (asynchronous) with multiple users, devices and participants.
* **No installation.** Connecting through a web browser with a personalized link is favored, avoiding complicated installation of apps and login / password / registration steps which is not an easy task for everyone, depending on their technological literacy. In the context of healthcare establishments, support of deployed apps often requires long-term planning and discussions with the Information Technology team, as opposed to web-based applications.
* **Long term availability.** Research projects can be conducted over a long period of time, and software versions, data structures, APIs, and used features must be stable over that period. There is no guarantee with a commercial system that used features will be supported for the required duration.
* **Server deployment and management.** Installation on low-cost hardware (e.g., Raspberry Pis), local servers and cloud infrastructure can be required, depending on the scale of the projects and its location. Deployments should be manageable by a small team.

Most of the open-source projects currently available concentrated their efforts on providing videoconferencing alternative to proprietary solutions (i.e., Skype, Google Meet, MS Teams, Zoom, etc.) with chat and file transfer capabilities. Alternative open-source projects include Big Blue Button, NextCloud Talk, Jami, OpenVidu, Jitsi Meet, and Kurento. Although excellent solutions for videoconferencing, they are not especially fit for research and do not meet all requirements for telehealth applications. They would also require customization at some level that can quickly become limitative or complicated.

Open-source rehabilitation-oriented applications are also available. The OpenRehab [@freitas_openrehab_2017] project lists multiple rehabilitation tools for upper limb, mobility, fitness, cognition, balance. Such applications are often dedicated to a specific domain and mostly contain pre-recorded videos or games that are prescribed by physiotherapists. Most of them do not offer teleconsultation features and remote access to research data.
Finally, open-source Electronic Health/Medical Records (EHR, EMR) [@neha_intelehealth_2017] are available and can meet some research requirements, but we want to avoid storing personal and sensitive information on participants. We prefer to use or connect to existing systems that comply with local regulations like Health Insurance Portability and Accountability Act (HIPPAA).
OpenTera is specifically designed to address the previously mentioned and required features for research. It is built using a microservice architecture based on recognized standards and best practices. This architecture provides scalability, flexibility, resilience, maintainability and technology diversity, all needed in a research context.

OpenTera contains the base server (TeraServer) offering a REST API [@fielding_rest_2002], useful to manage users, participants, devices, sites, projects, sessions, and supports multiple authentication methods via user/password, certificates or tokens. TeraServer also manages authorizations for users, participants and devices, providing a fine-grained access control on resources and assets.

OpenTera also includes base services: Video Rehabilitation, Logging and File Transfer. They are used to conduct audio/video WebRTC sessions from the web along with appropriate logging and file transfer capabilities. Structured sessions enable organized information such as survey data, sensor data, metadata and analytics, and facilitate the retrieval of information and key statistics. Development of new microservices allows developers to add new features to the system such as serious or exergames, exercises coach / videos and participant calendar / portal.

# Related projects

\autoref{tab:opentera-related-projects} shows OpenTera-related open-source projects that are currently under active development, implementing new OpenTera services or underlying libraries. OpenTera has been deployed for robot teleoperation during COVID [@panchea_opentera_2022] and is currently used for multiple rehabilitation projects.

Table: OpenTera Related Projects \label{tab:opentera-related-projects}

| GitHub Project Name             | Description                                                                                         |
|---------------------------------|-----------------------------------------------------------------------------------------------------|
| opentera-webrtc                 | WebRTC library in C++/Javascript/Python with signaling server to allow audio/video/data sessions.   |
| opentera-teleop-service         | OpenTera Service managing robots fleet and web front-end for tele-operation.                        |
| opentera-webrtc-teleop-frontend | Robot teleoperation front-end made with Vue.js.                                                     |
| opentera-webrtc-ros             | OpenTera robot device client and ROS integration for remote control and monitoring of mobile robots.|
| openteraplus                    | Qt Frontend to manage OpenTera configuration and data.                                              |

# Acknowledgements

This work was supported by the Natural Sciences and Engineering Research Council of Canada (NSERC), the Fonds de recherche du Québec – Nature et technologies (FRQNT) and the Network of Centres of Excellence of Canada on Aging Gracefully across Environments using Technology to Support Wellness, Engagement, and Long Life (AGE-WELL).

# References
