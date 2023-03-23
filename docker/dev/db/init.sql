
create database opentera;
create user TeraAgent with encrypted password 'tera';
grant all privileges on database opentera to TeraAgent;
ALTER USER TeraAgent WITH PASSWORD 'tera';
create database openteralogs;
grant all privileges on database openteralogs to TeraAgent;
create database openterafiles;
grant all privileges on database openterafiles to TeraAgent;
