#!/usr/bin/env python
#
# Author: Mike Hoye
# Email: mhoye@mozilla.com
# License: MPL (current)

import smtplib
import json
import urllib2
import sys
import re
import logging, logging.handlers
import random
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
                                               backupCount=10)
    rfh.setFormatter(fmt)
    rfh.setLevel(logging.DEBUG)
    logging.root.addHandler(rfh)
    logging.root.setLevel(logging.DEBUG)

    logging.info("---------- starting run ----------")
    logging.info("loading config... ")

    # cfg should be safe to load/handle
    config = json.load(open("/etc/bz-triage.cfg"))

    bugs,strs,ranges = findbugs(config)
    users = getContributors()
    sendTriageMail(users, bugs, strs, ranges, config)

def findbugs(cfg):

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

    # This is today-1 and today-3 because it's intended to run in a cron job at 3 AM,
    # and have some overlap with the previous day, so we get a floating window across
    # our incoming bugs. 

    date_to    = str(date.isoformat(date.today() - timedelta(1))).encode("utf8")
    date_from  = str(date.isoformat(date.today() - timedelta(3))).encode("utf8")

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
        buglist = list(set(buglist + bugs)) #add and dedupe

    logging.info("Found %s bugs in %s components." % (len(buglist), (len(option_sets)))) 

    # let's open this up a bit.

    date_to    = str(date.isoformat(date.today() - timedelta(1))).encode("utf8")
    date_from  = str(date.isoformat(date.today() - timedelta(40))).encode("utf8")


    stepslist = list()
    option_sets = {
         'firefox': {
            'changed_field':'keywords',
            'changed_after':date_from,
            'changed_before':   date_to,
            'product':  'Firefox',
            'keywords':   'steps-wanted'  },
        'core': {
            'changed_field':'keywords',
            'changed_after':date_from,
            'changed_before':   date_to,
            'product':  'Core',
            'keywords':   'steps-wanted'  },
        'toolkit': {
            'changed_field':'keywords',
            'changed_after':date_from,
            'changed_before':   date_to,
           'product':  'Toolkit',
            'keywords':   'steps-wanted'},
        }


    for options in option_sets.values():
        steps = bzagent.get_bug_list(options) 
        stepslist = list(set(stepslist + steps)) #add and dedupe

    logging.info("Found %s steps-wanted in %s components." % (len(stepslist), (len(option_sets)))) 


    regressionlist = list()

    option_sets = {
         'firefox': {
            'changed_field':'keywords',
            'changed_after':date_from,
            'changed_before':   date_to,
            'product':  'Firefox',
            'keywords':   'regressionwindow-wanted'  },
        'core': {
            'changed_field':'keywords',
            'changed_after':date_from,
            'changed_before':   date_to,
            'product':  'Core',
            'keywords':   'regressionwindow-wanted'  },
        'toolkit': {
            'changed_field':'keywords',
            'changed_after':date_from,
            'changed_before':   date_to,
            'product':  'Toolkit',
            'keywords':   'regressionwindow-wanted'},
        }

    for options in option_sets.values():
        regression = bzagent.get_bug_list(options) 
        regressionlist = list(set(regressionlist + regression)) #add and dedupe

    logging.info("Found %s regression-wanted in %s components." % (len(regressionlist), (len(option_sets)))) 

    return ( buglist, stepslist, regressionlist ) 
 


def getContributors():

    # got bugs. let's get contributors!

    try:
        allcontributors = json.load(open("/var/local/bz-triage/contributors.cfg"))
    except:
        logging.info("Failed to open contributors file.....")
        print("Failed to open contributors.cfg.")
        exit(-1)

    #print str(allcontributors)

    # Assign bugs to contributors. The process below favors getting 
    # some bugs to many people over getting many bugs to some people.

    today = list()

    for contrib in allcontributors:
        if contrib[3] == "daily"                            \
        or (contrib[3] == "workdays" and date.weekday(date.today()) < 5)   \
        or (contrib[3] == "weekly" and date.weekday(date.today()) == 0 ):
            today.append(contrib)

    return today;

def sendTriageMail(people, buglist, rangelist, stepslist, cfg):

    random.shuffle(people)
    random.shuffle(buglist) 
    random.shuffle(rangelist)
    random.shuffle(stepslist)

    triagemail  = dict()
    stepsmail   = dict()
    rangemail   = dict()
    msg         = dict()

    spin = True 

    while spin:
        if not people: # If we're out of volunteers, stop
            break
        for t in people: 
            if not t[0] in rangemail:
                rangemail[t[0]] = []
            if not t[0] in stepsmail:
                stepsmail[t[0]] = []
            if not t[0] in triagemail:
                triagemail[t[0]] = []
            if len(triagemail[t[0]]) + len(rangemail[t[0]]) + len(stepsmail[t[0]])  >= int(t[2]):
                people.remove(t) # If this contributor is full, pop them.
                continue
            if buglist or rangelist or stepslist:
                if t[4] == "on" and rangelist: 
                    rangemail[t[0]].append(rangelist.pop())
                    continue
                elif t[5] == "on" and stepslist: 
                    stepsmail[t[0]].append(stepslist.pop())
                    continue
                elif t[0] in triagemail and buglist:
                    triagemail[t[0]].append(buglist.pop())
                    continue
                else:
                    spin = False  # We get here only if we've been able to take no action.
                                  # as in - task-to-available-slot mismatch.


    participants = list(set(triagemail.keys() + stepsmail.keys() + rangemail.keys()))

    mailoutlog = ""

    for rec in participants:
        if not ( triagemail[rec] or stepsmail[rec] or rangemail[rec] ):  # keep it clean.
            continue
        mailoutlog = rec.encode("utf8")
        content = "Hello, " + rec.encode("utf8") + '''

Bug triage is the most important part of a program's life. We're building a smarter, faster Firefox for a smarter, faster Web, and we're grateful for your help.

Thank you.

'''

        if triagemail[rec]:
            content += '''

Today we would like your help triaging the following bugs:

'''
        bugurls = ""
        for boog in triagemail[rec]:
            mailoutlog += " " + str(boog.id).encode("utf-8")
            bugurls += '''Bug %s - http://bugzilla.mozilla.org/%s - %s

''' % ( str(boog.id).encode("utf-8"), str(boog.id).encode("utf-8"), str(boog.summary).encode("utf-8") )
        content += bugurls

        if rangemail[rec]:
            content += '''

Our engineers have asked for help finding a regression range for these bugs:
'''
        bugurls = ""
        for boog in rangemail[rec]:
            mailoutlog += " " + str(boog.id).encode("utf-8")
            bugurls += '''Bug %s - http://bugzilla.mozilla.org/%s - %s

''' % ( str(boog.id).encode("utf-8"), str(boog.id).encode("utf-8"), str(boog.summary).encode("utf-8") )
        content += bugurls

        if stepsmail[rec]:
            content += '''

We need to figure out the steps to reproduce the following bugs:

'''
        bugurls = ""
        for boog in stepsmail[rec]:
            mailoutlog += " " + str(boog.id).encode("utf-8")
            bugurls += '''Bug %s - http://bugzilla.mozilla.org/%s - %s

''' % ( str(boog.id).encode("utf-8"), str(boog.id).encode("utf-8"), str(boog.summary).encode("utf-8") )
        content += bugurls


        content += '''

There are a few things you can do to move these bugs forward:

  - Most importantly, sort the bug into the correct component: https://developer.mozilla.org/en-US/docs/Mozilla/QA/Confirming_unconfirmed_bugs
  - Use MozRegression to figure out exactly when a bug was introduced. You can learn about MozRegression here: http://mozilla.github.io/mozregression/
  - Search for similar bugs or duplicates and link them together if found: https://bugzilla.mozilla.org/duplicates.cgi
  - Check the flags, title and description for clarity and precision
  - Ask the reporter for related crash reports in about:crashes https://developer.mozilla.org/en-US/docs/Crash_reporting
  - Does this look like a small fix? Add [good first bug] to the whiteboard!

If you're just getting started and aren't sure how to proceed, this link will help:
  - https://developer.mozilla.org/en-US/docs/Mozilla/QA/Triaging_Bugs_for_Firefox

As always, the point of this exercise is to get the best information possible in front the right engineers. If you can reproduce them or isolate a test case, please add that information to the bug and change the status from "UNCONFIRMED" to "NEW".

Again, thank you. If you have any questions or concerns about the this process, you can join us on IRC in the #triage channel, or email Mike Hoye - mhoye@mozilla.com - directly.

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
        msg["To"] = rec.encode("utf8")
        msg["Bcc"] = str("mhoye@mozilla.com").encode("utf8")
        #msg["Reply-To"] = "noreply@mozilla.com"
        server.sendmail(sender, rec.encode("utf8") , msg.as_string())
        server.quit()
        logging.info(mailoutlog)


if __name__ == "__main__":
    main()

