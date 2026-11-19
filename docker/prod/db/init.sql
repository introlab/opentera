/* This needs to fit with OpenTera server configuration files. This script will be executed only once at first startup. */
/* Since PostgreSQL 15, only the database owner can create objects in the public schema by default,
   so TeraAgent is made the owner of each database. */
create user TeraAgent with encrypted password 'tera';
create database opentera owner TeraAgent;
create database openteralogs owner TeraAgent;
create database openterafiles owner TeraAgent;
create database openteraemails owner TeraAgent;
