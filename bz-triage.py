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



def getbugs(cfg, bzagent)

# We're picking our options about what bugs to search for now.
# We're hardcoding some assumptions about interesting date range
# and bug categories here.
# Those components are:
# - Firefox, Core and Triaged "Untriaged", respectively, or
# - In one of the Firefox, Core or Toolkit categories, and UNCONFIRMED

# this is today-1 and today-2 because it's intended to run in a cron job at 1 AM.

    date_to    = str(date.isoformat(date.today() - timedelta(1))).encode("utf-8")
    date_from  = str(date.isoformat(date.today() - timedelta(2))).encode("utf-8")

# not proud of this, but it works.

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

def loadcontributors(cfg):
# do stuff



def sendbugmail(cfg):


    # Ok, let's email some bugs.


    smtp = cfg["smtp_server"].encode("utf8")
    sender = cfg["smtp_user"].encode("utf8")
    server = smtplib.SMTP_SSL(smtp, 465)
    server.set_debuglevel(True)
    server.connect(smtp, 465)
    server.ehlo()
    server.login(sender, cfg["smtp_pass"].encode("utf8"))



    for user in users:
        k = users[user]
        bugs = []
        while len(bugs) < k and len(issues) != 0:
            issue = issues.pop()
            num = issue["number"]
            desc = issue["title"].encode("utf8")
            bugs.append("  - [ ] %5s: %s\n               http://github.com/%s/%s/issues/%s\n" %
                        (num, desc,                      owner, repo,   num))
        assert(len(bugs) != 0)
        assert(k != 0)
        msg = MIMEText(("""Greetings %s contributor!

    This week's triage assignment is %d bugs randomly divided between %d people,
    based on their preferred weekly capacity. You have been assigned %d bugs.
    Please make some time to look through your set and look for ways to move
    the bugs forward:

      - Search for duplicates and close the less-clear one if found
      - Search for similar bugs and link them together if found
        (with a comment mentioning the #NNNN number of one bug in the other)
      - Check the tags, title and description for clarity and precision
      - Nominate for a milestone if it fits the milestone's criteria
      - Add testcases, narrow them down or attempt to reproduce failures
      - Provide suggestions on how to fix the bug
      - Modernize test cases
      - Can a newbie handle this bug? Tag it 'easy'!
      - Can a newbie not handle this 'easy' bug? Untag it!

    And finally:

      - Actually try to fix the bug, if it seems within reach

    Note: only after all the above has been attempted and no improvements can
    be made then you may 'bump' the bug by leaving a comment such as 'bumping
    for triage'.

    We recommend using https://github.com/stephencelis/ghi for command-line
    operations on bugs. If you have any questions about your assigned bugs,
    please drop in to IRC and ask about them.

    Your %d bugs for this week are:

    %s
    """ %
    (repo, n, len(users), len(bugs), len(bugs), "\n".join(bugs))))

        msg["Subject"] = "bug inspection assignment for %s on %s" % (repo, date)
        msg["From"] = sender
        msg["To"] = user
        msg["Reply-To"] = sender
        server.sendmail(sender, user, msg.as_string())

    server.quit()

if __name__ == "__main__":
    main()

