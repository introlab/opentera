/* This needs to fit with OpenTera server configuration files. This script will be executed only once at first startup. */
create database opentera;
create user TeraAgent with encrypted password 'tera';
grant all privileges on database opentera to TeraAgent;
create database openteralogs;
grant all privileges on database openteralogs to TeraAgent;
create database openterafiles;
grant all privileges on database openterafiles to TeraAgent;

