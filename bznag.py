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
import pprint
from datetime import date, timedelta
from os import mkdir
from bugzilla.agents import BMOAgent
from bugzilla.utils import get_credentials
from email.mime.text import MIMEText


def main():

    pp = pprint.PrettyPrinter(indent=4)

    fmt = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s',
                            datefmt="%Y-%m-%d %H:%M:%S %Z")

    if "--quiet" not in sys.argv:
        sh = logging.StreamHandler()
        sh.setFormatter(fmt)
        sh.setLevel(logging.DEBUG)
        logging.root.addHandler(sh)

    rfh = logging.handlers.RotatingFileHandler("/var/log/bznag.log",
                                               backupCount=10)
    rfh.setFormatter(fmt)
    rfh.setLevel(logging.DEBUG)
    logging.root.addHandler(rfh)
    logging.root.setLevel(logging.DEBUG)

    # cfg should be safe to load/handle
    config = json.load(open("/etc/bznag.cfg"))
    recipients = json.load(open("/var/local/bznag/bznag-participants.cfg"))
    alerts = findbugs(config, recipients)

    sendSLAMail(alerts, recipients, config)

    # Debugging
    #pp.pprint(alerts)
    #pp.pprint(recipients)
    #pp.pprint(config)

    for derp in alerts.keys():
        pp.pprint(alerts[derp]['stale'])


def findbugs(cfg,recs):

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

    notif = dict() # key = intended recipient, value = list of bugs

    for ppl in recs.keys():

        buglist = list()
    # For each person, get the bugs have aged untouched to their level.
    # I'm making a design decision here to make this range window only
    # 2 days long - bugs older than that are being actively ignored.

        sla = recs[ppl]
        print str(ppl) + " " + str(sla)
        inc = 1

    # If it's a Monday, scan the last three days. Otherwise only the last one.
    # The cron job that kicks off this clownshow should only be running mon/fri.

        if (date.today().weekday() == 0):
            inc = 3
        week_inc = inc + 5
        date_to    = str(date.isoformat(date.today() - timedelta(sla + 1) )).encode("utf8")
        date_from  = str(date.isoformat(date.today() - timedelta(sla + inc + 1) )).encode("utf8")
        stale_time = str(date.isoformat(date.today() - timedelta(sla + week_inc + inc + 1) )).encode("utf8")

        print str("Stale date:") + str(stale_time)
    # Not proud of this next part. Store this properly in a file somewhere, you donkus.

        untriaged_bugs = list()

        untriaged_params= {
             'firefox_untriaged': {
                 'changed_field':'[Bug creation]',
                 'changed_after':date_from,
                 'changed_before':date_to,
                 'product':  'Firefox',
                 'component':'Untriaged'},
             'core_untriaged': {
                 'changed_field':'[Bug creation]',
                 'changed_after':date_from,
                 'changed_before':date_to,
                 'product':  'Toolkit',
                 'component':'Untriaged'},
             'toolkit_untriaged': {
                 'changed_field':'[Bug creation]',
                 'changed_after':date_from,
                 'changed_before':date_to,
                 'product':  'Core',
                 'component':'Untriaged' }
              }

        bugs = set()
        for options in untriaged_params.values():
            for b in bzagent.get_bug_list(options):
                if str(b.creation_time) == str(b.last_change_time):
                    bugs.add(b)
                    print "Untriaged:" + str(b.id) + " - " + str(b.creation_time) + " - " + str(b.last_change_time)

        untriaged_bugs = list(bugs) #add and dedupe

        stale_bugs = list()
        stale_params = {
            "firefox_stale_bug": {
                "product":  "Core",
                "bug_status": "UNCONFIRMED,NEW,ASSIGNED",
                "component":"Untriaged" },
            "core_stale_bug": {
                "bug_status": "UNCONFIRMED,NEW,ASSIGNED",
                "product":  "Core",
                "component":"Untriaged" },
            "toolkit_stale_bug": {
                "product":  "Core",
                "bug_status": "UNCONFIRMED,NEW,ASSIGNED",
                "component":"Untriaged" }
            }

        bugs = set()

        # juuuust subtly different.
        for options in stale_params.values():
            for b in bzagent.get_bug_list(options):
                if str(b.creation_time) == stale_time:
                    bugs.add(b)
                    print "Stale:" + str(b.id) + " - " + str(b.last_change_time)

        stale_bugs = list(bugs) # (this is so sloppy)


        notif[ppl] = { "untriaged": untriaged_bugs, "stale": stale_bugs }

    return ( notif )

def sendSLAMail(mailout,sla,cfg):

    msg = dict()
    # Ok, let's email some bugs.

    mailoutlog = ""
    for recipient in mailout.keys():
        if (mailout[recipient]['untriaged'] or mailout[recipient]['stale']):
            mailoutlog = recipient.encode("utf8")
            content = "This is a message from Mozilla's NagBot.\n\n"
            if mailout[recipient]['untriaged']:
                content += "You have asked receive notifications when Untriaged bugs have gone " + str(sla[recipient]) + " days without being acted upon.\n"
                content += "The following bugs have met that criteria:\n\n"
                for boog in mailout[recipient]['untriaged']:
                    mailoutlog += " " + str(boog.id).encode("utf-8")
                    content += '''Bug %s - http://bugzilla.mozilla.org/%s - %s\n''' \
                            % ( str(boog.id).encode("utf-8"), str(boog.id).encode("utf-8"), str(boog.summary).encode("utf-8") )
            if mailout[recipient]['stale']:
                content += "\nThe following bugs are still in an Untriaged component, and have not been acted on in " + str(sla[recipient] + 5 ) + " days.\n"
                content += "These bugs are getting stale:\n\n"
                for boog in mailout[recipient]['stale']:
                    mailoutlog += " " + str(boog.id).encode("utf-8")
                    content += '''Bug %s - http://bugzilla.mozilla.org/%s - %s\n''' \
                            % ( str(boog.id).encode("utf-8"), str(boog.id).encode("utf-8"), str(boog.summary).encode("utf-8") )
            content += "\n\nPlease examine these bugs at your earliest convenience, and either move them\n" +\
                       "to the correct category or assign them to or needinfo a developer.\n\n" +\
                       "If you have any questions about this notification service, please contact Mike Hoye."
            smtp = cfg["smtp_server"].encode("utf8")
            sender = cfg["smtp_user"].encode("utf8")
            server = smtplib.SMTP(smtp)
            #server.set_debuglevel(True)
            #server.connect(smtp)
            server.ehlo()
            #server.login(sender, cfg["smtp_pass"].encode("utf8"))
            msg = MIMEText(str(content).encode("utf8"))
            msg["Subject"] = str("NagBot: Untriaged bugs as of %s" % (date.today()) ).encode("utf8")
            msg["From"] = cfg["smtp_user"].encode("utf8")
            msg["To"] = recipient.encode("utf8")
            msg["BCC"] = str("mhoye@mozilla.com").encode("utf8")
            server.sendmail(sender, recipient.encode("utf8") , msg.as_string())
            server.quit()
            logging.info(mailoutlog)
            #print msg.as_string()

if __name__ == "__main__":
    main()

