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

    rfh = logging.handlers.RotatingFileHandler("/var/log/bz-triage.log",
                                               backupCount=10,
                                               maxBytes=1000000)
    rfh.setFormatter(fmt)
    rfh.setLevel(logging.DEBUG)
    logging.root.addHandler(rfh)
    logging.root.setLevel(logging.DEBUG)

    logging.info("---------- starting run ----------")
    logging.info("loading config... ")
    cfg = json.load(open("/etc/bz-triage.cfg"))

    server = cfg["server"].encode("utf8")
    owner = cfg["owner"].encode("utf8")
    user =  cfg["user"]
    password =  cfg["password"]

    try:
        bzagent = BMOAgent(user,password)
        logging.info("Connected to " + str(server) )
    except:
        logging.info("Failed to connect to " + str(server))
        exit(-1)

    # We're picking our options about what bugs to search for now.
# We're hardcoding some assumptions about interesting date range
# and bug categories here.
# Those components are:
# - Firefox, Core and Triaged "Untriaged", respectively, or
# - In one of the Firefox, Core or Toolkit categories, and UNCONFIRMED

    # this is today-1 and today-2 because it's intended to run in a cron job at 1 AM.

    date_to    = str(date.isoformat(date.today() - timedelta(1))).encode("utf8")
    date_from  = str(date.isoformat(date.today() - timedelta(2))).encode("utf8")

    # Not proud of this next part. Store this properly in a file somewhere, you donkus.

    # NOTE: The reason it's laid out like this is because bztools doesn't,
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

    logging.info("Found %s bugs in %s components." % (len(buglist), (len(option_sets)))) 
    logging.info("Reading in triage volunteer file.")

    # Ok, we've got bugs. let's get contributors!

    try:
        allcontributors = json.load(open("/var/local/bz-triage/contributors.cfg"))
    except:
        logging.info("Failed to open contributors file.....")
        exit(-1)

    print str(allcontributors)
    # Assign bugs to contributors. There are a few ways we could do this, and this
    # needs to be revisited for inclusiveness later. Best balance of inclusiveness
    # and participation I've got is an even spread of bugs up to each individual's
    # max, so: assign bugs to users one at a time, until you either run out of bugs
    # or all users are at their chosen max.

    today = list()

    for contrib in allcontributors:
        if contrib[3] == "daily"                            \
        or (contrib[3] == "workdays" and date.weekday(date.today()) < 5)   \
        or (contrib[3] == "weekly" and date.weekday(date.today()) == 0 ):
            today.append(contrib)
  
    mailout = dict()
    queue = list(today)
     
    while True:
        if not queue or not buglist: #once we've emptied one of them out...
            break
        for t in queue:
            if t[0] in mailout:
                mailout[t[0]].append(buglist.pop())
            else:
                mailout[t[0]] = [ buglist.pop() ]
            if not buglist:
                break
            if len(mailout[t[0]]) >= int(t[2]):
                 queue.remove(t)

    # Ok, let's email some bugs.


    for rec in today:
        content = "Hello, " + rec[1].encode("utf8") + '''

Triage is the most important part of a bug's lifecycle. By helping triage 
incoming bugs, you're helping Mozilla and the Web get better and move faster.
Thank you.
    
Today we'd like you to look at the following bugs:

'''
        bugurls = ""
        for boog in mailout[rec[0]]:
        # ADDBUGS HERE     
              bugurls += '''Bug %s - http://bugzilla.mozilla.org/%s - %s

''' % (boog.id, boog.id, boog.summary)
        content += bugurls


        content += '''

Please make some time to look through your set and look for ways to move the bugs forward:

      - Most importantly, sort the bug into the correct component:
        https://developer.mozilla.org/en-US/docs/Mozilla/QA/Confirming_unconfirmed_bugs
      - Search for similar bugs or duplicates and link them together if found
        https://bugzilla.mozilla.org/duplicates.cgi
      - Check the flags, title and description for clarity and precision
      - Ask for ( or provide! ) steps to reproduce in a clean profile or safe mode
        https://developer.mozilla.org/en-US/docs/Mozilla/Multiple_Firefox_Profiles
      - Ask the reporter for related crash reports in about:crashes
        https://developer.mozilla.org/en-US/docs/Crash_reporting
      - Provide suggestions on how to fix the bug
      - Does this look like a small fix? Add [good first bug] to the whiteboard!

And finally:

      - Actually try to fix the bug, if it seems within reach

If you're just getting started and aren't sure how to proceed, this link will help:

        https://developer.mozilla.org/en-US/docs/Mozilla/QA/Triaging_Bugs_for_Firefox

As always, the point of this exercise is to get the best information possible in front the right engineers.
After some or all the above has been attempted, you can bump the status of the bug from "unconfirmed" to "new"
to bring it to their attention.

Again, thank you. If you have any questions or concerns about the this process, you can join us on IRC in the
#triage channel, or email Mike Hoye - mhoye@mozilla.com directly.

'''

        smtp = cfg["smtp_server"].encode("utf8")
        sender = cfg["smtp_user"].encode("utf8")
        server = smtplib.SMTP(smtp)
        server.set_debuglevel(True)
        #server.connect(smtp)
        server.ehlo()
        #server.login(sender, cfg["smtp_pass"].encode("utf8"))
        msg = MIMEText(str(content).encode("utf8"))
        msg["Subject"] = str("Bugs to triage for %s" % (date.today()) ).encode("utf8")
        msg["From"] = cfg["smtp_user"].encode("utf8")
        msg["To"] = rec[0].encode("utf8")
        #msg["Reply-To"] = "noreply@mozilla.com"
        server.sendmail(sender, rec[0].encode("utf8") , msg.as_string())
        server.quit()
        logging.info("Mailed bugs to: " + rec[0].encode("utf8"))

if __name__ == "__main__":
    main()

