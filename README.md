# Canutist
This is a tool for facilitating community involvement the Bugzilla triage process. 
It depends on bztools, available here:

https://github.com/LegNeato/bztools

## Installation:

Steps to install are:
- Set up a webserver such as Apache or Lighhtpd.
- Configure that server to use python and CGI
- Create and set permissions on the following files as appropriate:

Files and permissions required by this application are:
 - /etc/bz-triage.cfg      - Read access
 - /var/log/bz-triage.log  - Write access
 - /var/local/bz-triage/contributors.cfg   - Read and write access.

The bz-triage.cfg file looks like this:

{
"server": "<your Bugzilla server>",
"owner": "<your name>",
"user": "<bugzilla service account>",
"password": "<bugzilla service account password>",
"smtp_user": "<your outgoing mail service account>",
"smtp_password": "<mail service account password>",
"smtp_server": "<outgoing mail server>"
}
