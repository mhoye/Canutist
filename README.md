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
"server": "&lt;your Bugzilla server&gt;",
"owner": "&lt;your name&gt;",
"user": "&lt;bugzilla service account&gt;",
"password": "&lt;bugzilla service account password&gt;",
"smtp_user": "&lt;your outgoing mail service account&gt;",
"smtp_password": "&lt;mail service account password&gt;",
"smtp_server": "&lt;outgoing mail server&gt;"
}
