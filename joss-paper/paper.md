---
title: 'OpenTera : A Microservice Framework Allowing Structured and Customized Tele-Health Sessions And Data Collection for Research' 
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

date: April 4 2023 
bibliography: paper.bib 
--- 
# Summary 

OpenTera is a microservice based framework primarily developed to support tele-health research projects and real-world deployment. This project is based on many years of experience linking at-home participants to remote users (such as clinicians, researchers, healthcare professionals) with audio-video-data connections and in-the-field sensors (such as biometrics, activities and robotics devices). 

 
Most telehealth-based research projects require a common data structure: data collection sites, projects, participants and sessions including various recorded data types (from sensors or other sources). Those projects also require many common features: user authentication based on various access roles, ability to add new features based on specific project needs, ease of use for the participant and secure data hosting.  These features are also shared between research projects: videoconferencing with specific health related features (angles measurement, timers, etc.), surveys data collection, data analysis and exportation. 

Since many of the available solutions are either costly, features limited, proprietary (e.g., can't be easily adapted for research purpose and raw data is harder to access) or hard to deploy in a tele-health context, OpenTera was built to allow for extensibility over the various projects needs and to provide research projects full control over their data and hosting. 

Applications of the OpenTera framework are not limited to research projects, and can also be applied in a clinical environment, where clinicians must communicate with patients. Such fields include but are not limited to: tele-rehabilitation (physical, social, mental), robotic tele-operation and remote activity monitoring. 

 
The project has been developed internally since 2013 but published as open-source software on GitHub in 2019 with an Apache-2.0 license along with documentation and examples. 

# Statement of need 

From our research experience, common features between the different tele-health projects we participated emerged: 

* Data structure. Store data in a structured way to ease data extraction and analysis. 

* Ecological data capture. Collect data not only in laboratories or controlled environments, but also in homes or institutions. 

* Project adaptability. Develop projects specific dashboards and user interfaces while reusing as much as possible of what was done before to reduce development time. Rehabilitation projects may require implementing serious games or exergames while teleoperation projects may require real-time navigation tools. Adapting already existing open-source software when possible is often the key. 

* Cost effectiveness. Most of the recent commercial cloud tele-health applications available are subscription based and do not offer the flexibility we need. Each vendor offers its own approach tailored for its products and services. We often have data collections from dozens of participants and users and paying the subscription fee would be prohibitive. 

* Security. Store and transfer data in a secure and controlled way. Access control to information depending on each project requirements. Research projects involving participants must be approved by the ethics committee, and they often require servers hosted locally or in a specific region. 

* Uniformity. Avoid the use of multiple applications and tools that would require the user to navigate between them (minimizing and restoring them as needed) and focusing attention on the current tele-health task.  

* Ease of use. Implement an easy-to-use solution for the user and the participant at all steps of the process (authentication, data collection, data management).  Avoid long list of "friends" for communication where we need to click the right person and start a conference. 

* Synchronous and asynchronous sessions. Support real-time sessions (synchronous) or on-demand pre-recorded or application-based sessions (asynchronous) with multiple users, devices and participants. 

* No installation. Especially for participants, connecting through a web browser with a personalized link is favored, avoiding complicated installation of apps and login / password / registration steps which is not an easy task for everyone, depending on their technological literacy. In the context of healthcare establishments, support of deployed apps often requires long-term planning and discussions with the IT team, as opposed to web-based applications. 

* Long term availability. Since research projects can extend over a long period of time, it is required that the underlying systems to be supported for that period. No guarantee exists when using a commercial system that it will remain feature compatible for the required duration.  

* Server deployment and management. Installing the system on low-cost hardware (like Raspberry Pis), local servers and cloud infrastructure can be required, depending on the scale of the projects and its location. Deployments should be manageable by a small team. 

 
Most of the open-source projects currently available concentrated their efforts on providing videoconferencing alternative to proprietary solutions (i.e., Skype, Google Meet, MS Teams, Zoom, etc.) with chat and file transfer capabilities. Alternative open-source projects include Big Blue Button, NextCloud Talk, Jami, OpenVidu, Jitsi Meet, Kurento. Although excellent solutions for videoconferencing, they are not especially fit for research and do not meet all requirements for tele-health applications and would require customization at some level that can quickly become limitative or complicated.  

Open-source rehabilitation-oriented applications are also available. The OpenRehab [@freitas_openrehab_2017] project lists multiple rehabilitation tools for: upper limb, mobility, fitness, cognition, balance. Such applications are often dedicated to a specific domain and mostly contain pre-recorded videos that are prescribed by the physiotherapists. Most of them do not offer tele-consultation features and remote access to research data. 

Finally, open-source Electronic Health/Medical Records (EHR, EMR) [@neha_intelehealth_2017] are available and can meet some research requirements, but we want to avoid storing personal and sensitive information on participants and prefer to use or connect to existing systems that comply with local regulations like Health Insurance Portability and Accountability Act (HIPPAA).  

OpenTera is specifically designed to address the previously mentioned and required features for research. It is built using a microservice architecture based as much as possible on recognized standards and best practices. This architecture allows scalability, flexibility, resilience, maintainability and technology diversity, all needed in a research context.  

 
OpenTera contains the base server (TeraServer) offering a REST API [@fielding_rest_2002], useful to manage users, participants, devices, sites, projects, sessions, and supports multiple authentication methods via user/password, certificates or tokens. TeraServer also manages authorizations for users, participants and devices, allowing a fine-grained access control on resources and assets. 


OpenTera also includes base services: Video Rehabilitation, Logging and File Transfer. They allow audio/video WebRTC sessions from the web along with appropriate logging and file transfer capabilities. Structured sessions enable organized information such as survey results, sensor data, metadata and analytics and facilitate the retrieval of information and key statistics. 

 
Microservices scalability and diversity allows developers to use any technology for backends and frontends. Such microservices can add new features to the system such as serious or exergames, exercises coach / videos and participant calendar / portal. Development of new microservices can leverage on the OpenTera Python library, available on PyPi. 

# Related projects 

Table \autoref{tab:opentera-related-projects} shows related open-source projects that are currently under active development and implementing new OpenTera services or underlying libraries. 
 
Table: OpenTera Related Projects \label{tab:opentera-related-projects} 

| GitHub Project Name             | Description                                                                                         | 
|---------------------------------|-----------------------------------------------------------------------------------------------------| 
| opentera-webrtc                 | WebRTC library in C++/Javascript/Python with signaling server to allow audio/video/data sessions.   | 
| opentera-teleop-service         | OpenTera Service managing robots fleet and web front-end for tele-operation.                        | 
| opentera-webrtc-teleop-frontend | Robot teleoperation front-end made with Vue.js[@vuejs].                                             | 
| opentera-webrtc-ros             | OpenTera robot device client and ROS integration for remote control and monitoring of mobile robots.| 
| openteraplus                    | Qt Frontend to manage OpenTera configuration and data.                                              | 

 
OpenTera has been deployed for robot tele-operation during COVID[@panchea_opentera_2022] and is currently used for multiple rehabilitation projects since its inception. 

 
# Acknowledgements 

This work was supported by the Natural Sciences and Engineering Research Council of Canada (NSERC), the Fonds de recherche du Québec – Nature et technologies (FRQNT) and the Network of Centres of Excellence of Canada on Aging Gracefully across Environments using Technology to Support Wellness, Engagement, and Long Life (AGE-WELL). 

# References 
