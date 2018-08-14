# Canutist/TriageBot
This is a tool for facilitating community involvement the Bugzilla triage process.
It is named for Canute The Great, 12th century king of what are now Denmark, Norway, 
England and Sweden, and dedicated to those of us who cannot simply order the 
incoming tides to stop.

https://en.wikipedia.org/wiki/King_Canute_and_the_waves
 
Outside of Python and the relevant modules it also depends on bztools, available here:

https://github.com/LegNeato/bztools

## Installation:

Steps to install are:
- Set up a webserver such as Apache or Lighhtpd.
- Configure that server to use python as CGI
- Create and set permissions as follows on the following files:

Files and permissions required by the web server for this application are:
 - /etc/bz-triage.cfg                       - Read access
 - /var/log/bz-triage.log                   - Write access
 - /var/local/bz-triage/contributors.cfg    - Read and write access.

bz-triage.cfg looks like this:

{
"server": "&lt;your Bugzilla server&gt;",
"owner": "&lt;your name&gt;",
"user": "&lt;bugzilla service account&gt;",
"password": "&lt;bugzilla service account password&gt;",
"smtp_user": "&lt;your outgoing mail service account&gt;",
"smtp_password": "&lt;mail service account password&gt;",
"smtp_server": "&lt;outgoing mail server&gt;"
}
