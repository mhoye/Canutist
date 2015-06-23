#!/usr/bin/env python
#
# Author: Mike Hoye
# Email: mhoye@mozilla.com
# License: MPL

import smtplib
import json
import urllib2
import sys
import re
import logging, logging.handlers
from datetime import date, timedelta
from os import mkdir
from bugzilla.agents import BMOAgent
from bugzilla.utils import get_credentials
from email.mime.text import MIMEText


def main():

    fmt = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s',
                            datefmt="%Y-%m-%d %H:%M:%S %Z")

    if "--quiet" not in sys.argv:
        sh = logging.StreamHandler()
        sh.setFormatter(fmt)
        sh.setLevel(logging.DEBUG)
        logging.root.addHandler(sh)

    #rfh = logging.handlers.RotatingFileHandler("/var/log/bz-triage.log",
    #                                           backupCount=10,
    #                                           maxBytes=1000000)
    #rfh.setFormatter(fmt)
    #rfh.setLevel(logging.DEBUG)
    #logging.root.addHandler(rfh)
    #logging.root.setLevel(logging.DEBUG)

    #logging.info("Generating static audit page for previous ten days."
    #logging.info("loading config... ")
    cfg = json.load(open("/etc/bz-triage.cfg"))

    server = cfg["server"].encode("utf8")
    owner = cfg["owner"].encode("utf8")
    user =  cfg["user"]
    password =  cfg["password"]

    # for (last ten days of bugs) get (bug count)
    
    for inc in range(1,10):
        print inc


def getOutstandingBugs(someday):
    try:
        bzagent = BMOAgent(user,password)
        logging.info("Connected to " + str(server) )
    except:
        logging.info("Failed to connect to " + str(server))
        exit(-1)
    date_from  = str(date.isoformat(someday - timedelta(1))).encode("utf8")
    date_to    = str(date.isoformat(someday)).encode("utf8")

    # NOTE: The reason it's laid out like this is because bztools doesn't
    # seem to work with the "product=foo,bar" syntax, despite what the docs say

    option_sets = {
        'firefox': {
            'changed_field':'[Bug creation]',
            'changed_after':date_from,
            'changed_before':   date_to,
            'product':  'Firefox',
            'status':   'UNCONFIRMED'  },
        'core': {
            'changed_field':'[Bug creation]',
            'changed_after':date_from,
            'changed_before':   date_to,
            'product':  'Core',
            'status':   'UNCONFIRMED'  },
        'toolkit': {
            'changed_field':'[Bug creation]',
            'changed_after':date_from,
            'changed_before':   date_to,
            'product':  'Toolkit',
            'status':   'UNCONFIRMED'},
        'firefox_untriaged': {
            'changed_field':'[Bug creation]',
            'changed_after':date_from,
            'changed_before':   date_to,
            'product':  'Firefox',
            'component':'Untriaged'},
        'core_untriaged': {
            'changed_field':'[Bug creation]',
            'changed_after':date_from,
            'changed_before':   date_to,
            'product':  'Toolkit',
            'component':'Untriaged'},
        'toolkit_untriaged': {
            'changed_field':'[Bug creation]',
            'changed_after':date_from,
            'changed_before':   date_to,
            'product':  'Core',
            'component':'Untriaged'
           },
        }

    buglist = list()

    # Get the bugs from the bugzilla API
 
    for options in option_sets.values():
        bugs = bzagent.get_bug_list(options) 
        buglist.extend(bugs)

    return bugs


if __name__ == "__main__":
    main()

