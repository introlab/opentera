# Security
OpenTera was built with security considerations. While the platform isn't meant to be used as a full electronic medical record (EMR) and was built at first for research purpose and needs, any system that exchanges and stores data should be properly secured nowadays. This is especially true in the telehealth field where there are professionals and patients involved.

This page presents a brief overview of the security elements that have been put in place in the OpenTera platform.

## Logins and system access
As presented in the [login and authentication](developers/Login-and-authentication) section, sensitive parts of the system are secured with a need to authenticate. Furthermore, [access roles](services/teraserver/OpenTera_AccessRoles) are defined to further filter out information that cannot be accessed by an end-user that doesn't have the required access.

All of that filtering is done on server-side, preventing the clients to even have access to data they are not allowed to.

While token-based authentication can be used, those tokens are encrypted and validated by the server against tampering, and static tokens have a very limited used (typically to login), requiring the need to use a dynamic token. Thus, in case of a security breach, the static tokens can be easily changed with minimal impact.

## SSL certificates
All communication occurring from and to the server are encrypted using SSL certificates. Since a single point of entry is used ([NGINX](https://www.nginx.com/)), the certificates only needs to be maintained and updated there, easing server maintenance without having to update each of the services and modules certificates individually.

Except in [special cases](developers/Login-and-authentication), the certificates are not used to authenticate the clients, only to encrypt data transfer and to authenticate the server.

While self-signed certificates can be used in local and development setup, on a [production server](Deployment), certificate-authority issued certificates should be used, especially since most web browsers (and operating systems) refuse to accept self-signed certificates.

## Websocket communication
Secure websockets are used and all communication occurring over them are encrypted using the same SSL certificates as above.

In the [websocket connection](developers/Websockets-communication) with a client, the websocket listens only for 60 seconds before closing and will be tied to internal session id of the client requesting a websocket, preventing another client to connect on that particular websocket.

## Video sessions
Many layers of security have been added in the video sessions to properly secure them:
* By using [WebRTC](https://www.webrtc.org), **peer-to-peer connections are used**, preventing video, audio and data information to transit over a third-party server. This server only acts as a signaling server to put peers in communications with each others. In the rare case that a TURN server might be required to relay information between peers, it would not have the key to decrypt and access the information it relays.

* Each video sessions are **started on a different process**. There is not a singular process on the server that would separate sessions into "rooms" or any similar software concepts. By using different process, this prevents possible data leaking: as each session runs by itself without knowing or having access to data in the other sessions, unless an invitation is sent to join that session, it is impossible to know what's going on in each of them.

* Each video sessions are *dynamically created*. As opposed to standard online videoconferencing systems where a link for a specific meeting needs to be sent in advance to each invitees, OpenTera requires that each invitees logs to the system, and then invites them to a video session. This ease the use of the system in general for the participants (not having to receive many "meetings" invitation), but also makes a video session volatile and only present on the system for the time it is running.

* In a similar way, each video session is **secured by an access key** and **runs on a different port**. While the last element is a side effect of the video sessions running in different process, it provides a welcome variability in the sessions URLs (see the [Video Rehab Service](services/Videorehab-Service) for more information). Each session access key is a 128 bit unique ID that changes with each session and is sent only to the invitees. Thus, a hacker trying to join an out-going session would have to match the session port and the session access key, combined with the fact that this combination is valid for a limited time (the time the session is ongoing), would required a lot of computing resources to hack into a session... or be very very lucky! And in the improbable case such a hack would happen, the users would just have to close and start a new session to start anew.

## Divide and conquer
The OpenTera approach is to be as modular as possible. Thus, all components, be them the database, internal communication module, services and file storage, are designed to be hosted, if needed, on different servers. If an high-security environment is needed for example, each of the components could be physically separated, and if a server becomes compromised, not all data would be.

Such an approach could also be used for load-balancing and redundancy, if required, by properly configuring the NGINX router module.

## In conclusion
While security is never perfect in any system, various approach have been implemented in the OpenTera platform to address potential security issues. 
