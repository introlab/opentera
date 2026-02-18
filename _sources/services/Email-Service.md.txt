# Email Service
The email service is intented to provide email communications (sending) from the OpenTera platform. It uses an external SMTP server - the service
doesn't implement its own server.

## Main script
The Email service can be launched by running the 
[EmailService.py](https://github.com/introlab/opentera/blob/main/teraserver/python/services/EmailService/EmailService.py) 
script. As a system service, it is also launched automatically when running the 
[main OpenTera service](teraserver/teraserver.rst).

## Configuration
Configuration files for the email service are similar to the basic 
[configuration files](../Configuration-files). They, however, add a specific section for that service.

### Email config section
`hostname`: Hostname of the SMTP email server to use.
`port`: Port of the STMP email server
`tls`: If true, TLS encryption will be used when communicating with the SMTP email server
`ssl`: If true, SSL encryption will be used when communicating with the SMTP email server
`username`: Username to use when authenticating with the SMTP email server
`password`: Password to use when authenticating with the SMTP email server
`default_sender`: Default email address to use as sender when none is specified
`max_emails`: Maximum number of emails to send to the SMTP email server in one connection.

## Default port and location
By default, the service will listen to port 4043 (non-ssl) and will be at `/email` behind the NGINX router.

## Web URLs and REST API
**Doc page** - by default at https://127.0.0.1:40075/email/doc. Will display the [REST API](teraserver/api/API) 
documentation and test system. Useful to test queries manually.

## Specific notes
Since the email server is usually associated to a domain, it's easy for emails sent that way to be classified as "junkmail" by email clients.

To prevent that, ensure that users are using emails in the same domain or that you are sending emails using a default "noreply" email in the correct domain.

## Web Frontend
Currently, no web front-end is available for that service

## RPC API
None. This service uses the [asynchronous communication system](../developers/Internal-services-communication-module).
