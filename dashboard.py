#!/usr/bin/env python
#
# Author: Mike Hoye
# Email: mhoye@mozilla.com
# License: MPL

import json
import urllib2
import sys
import re
import logging, logging.handlers
from datetime import date, timedelta
from os import mkdir
from bugzilla.agents import BMOAgent
from bugzilla.utils import get_credentials
from xml.sax.saxutils import escape

def main():

    fmt = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s',
                            datefmt="%Y-%m-%d %H:%M:%S %Z")

    if "--quiet" not in sys.argv:
        sh = logging.StreamHandler()
        sh.setFormatter(fmt)
        sh.setLevel(logging.DEBUG)
        logging.root.addHandler(sh)

    rfh = logging.handlers.RotatingFileHandler("/var/log/bz-triage.log",
                                               backupCount=10)
    rfh.setFormatter(fmt)
    rfh.setLevel(logging.DEBUG)
    logging.root.addHandler(rfh)
    logging.root.setLevel(logging.DEBUG)

    logging.info("Generating static audit page.")
    cfg = json.load(open("/etc/bz-triage.cfg"))

    server = cfg["server"].encode("utf8")
    owner = cfg["owner"].encode("utf8")
    user =  cfg["user"]
    password =  cfg["password"]

    bugdays = dict()
    try:
        contributors = json.load(open("/var/local/bz-triage/contributors.cfg"))
        bzagent = BMOAgent(user,password)
    except:
        logging.info("Failed to obtain data sources.")
        exit(-1) 
    for inc in range(1,10):
       d = date.today() - timedelta(inc)
       bugdays[d] = getOutstandingBugs(bzagent, d)
    
    print '''<html>
<head>
<title>All Hail King Canute</title>
<link href="index.css" rel="stylesheet" type="text/css">
</head>
<body>
<div class="logo">
<center><img src="allthethings.jpeg" width="800px"></center>
</div>

<div id="header">
<h2>Current Status</h2>
</div>
<div id="body">
<h3>Number of contributors: %d</h3> 
''' % (len(contributors))
   
    print '''</div>

<div id="header">
Outstanding Bugs!
</div>
'''

    for key in list(reversed( sorted(bugdays.keys()))):
        print '''<div class="dayheader">Outstanding bugs for %s: %s</div>''' % (str(key),  str(len(bugdays[key])))
        print '''<div class="day"><blockquote>'''
        for boog in bugdays[key]:
            print '''<br/><a href="https://bugzilla.mozilla.org/%s">Bug %s</a>: %s''' % (boog.id, boog.id, escape(boog.summary))
        print '''</blockquote></div>'''

    print "</body></html>"


def getOutstandingBugs(bzagent,someday):

    date_from  = str(date.isoformat(someday)).encode("utf8")
    date_to    = str(date.isoformat(someday)).encode("utf8")

    # NOTE: The reason it's laid out like this is because bztools doesn't
    # seem to work with the "product=foo,bar" syntax, despite what the docs say

    option_sets = {
        'firefox_untriaged': {
            'changed_field':'[Bug creation]',
            'changed_after':date_from,
            'changed_before':   date_to,
            'product':  'Firefox',
            'component':'Untriaged',
            'status': 'UNCONFIRMED'},
        'core_untriaged': {
            'changed_field':'[Bug creation]',
            'changed_after':date_from,
            'changed_before':   date_to,
            'product':  'Toolkit',
            'component':'Untriaged',
            'status': 'UNCONFIRMED'},
        'toolkit_untriaged': {
            'changed_field':'[Bug creation]',
            'changed_after':date_from,
            'changed_before':   date_to,
            'product':  'Core',
            'component':'Untriaged',
            'status': 'UNCONFIRMED'},
        }

    buglist = list()

    # Get the bugs from the bugzilla API
 
    for options in option_sets.values():
        bugs = bzagent.get_bug_list(options) 
        buglist.extend(bugs)
  
    #print  date_to + " - " + str(len(buglist))
    return buglist


if __name__ == "__main__":
    main()

