# Triagebot Nubis deployment repository

This is the deployment repository for
[triagebot.mozilla.org](https://triagebot.mozilla.org)

## Components

Defined in [nubis/terraform/main.tf](nubis/terraform)

### Webservers

Defined in [nubis/puppet/apache.pp](nubis/puppet)

The produced image is that of a simple Ubuntu Apache webserver running Python CGIs

### Load Balancer

Simple ELB

### Email

This application sends outbound e-mails (password-resets, notifications, etc)
using SES

### Storage

Main application state is persisted on disk.  EFS/NFS is used to provide
persistency in 2 files *contributors.cfg* and *bznag-participants.cfg*, available
under /data/${project_name}/ on all [webservers](#webservers)

### Buckets

An S3 bucket is used to store periodic backups of the [Storage](#storage)

## Configuration

The application's configuration file is
[/etc/bznag.cfg](nubis/puppet/files/confd/templates) and [/etc/bz-triage.cfg](nubis/puppet/files/confd/templates)
and are confd managed.

### Consul Keys

This application's Consul keys, living under
*${project_name}-${environment}/${environment}/config/*
and defined in Defined in [nubis/terraform/consul.tf](nubis/terraform)

#### bugzilla_server

*Operator Supplied* Hostname of the bugzilla server to connect to

#### bugzilla_user

*Operator Supplied* Username to use when connecting to [bugzilla_server](#bugzilla_server)

#### bugzilla_user_bznag

*Operator Supplied* Username to use when connecting to [bugzilla_server](#bugzilla_server)

#### bugzilla_password

*Operator Supplied* Password to use when connecting to [bugzilla_server](#bugzilla_server)

#### bugzilla_password_bznag

*Operator Supplied* Password to use when connecting to [bugzilla_server](#bugzilla_server)

#### owner

*Operator Supplied* Unused?

#### smtp_from

*Operator Supplied* Full e-mail address mails are sent from

#### smtp_from_bznag

*Operator Supplied* Full e-mail address mails are sent from

#### Bucket/Backup/Name

Name of the S3 bucket used for backups

#### Bucket/Backup/Region

Region of the S3 bucket used for backups

#### SMTP/Server

SES SMTP server hostname

#### SMTP/User

SES SMTP username

#### SMTP/Password

SES SMTP password

#### storage/${project_name}/fsid

[Storage](#storage) Filesystem ID

## Cron Jobs

Daily backup job copies data from [Storage](#storage) to [Buckets](#buckets)

Aditionally, there are more cronjobs in [nubis/puppet/cron.pp](nubis/puppet)

### Dashboard

Generates a dashboard, accessible under /dashboard

### Triage

The main triage job, sending e-mail to interested users

### Nag

A secondary triage job

## Logs

No application specific logs
