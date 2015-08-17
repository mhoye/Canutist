#!/usr/bin/env python

import sys
import json
import cgi
import cgitb
import logging, logging.handlers
from validate_email import validate_email
from lockfile import LockFile
import bleach

def main():

    fmt = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s',
                            datefmt="%Y-%m-%d %H:%M:%S %Z")
    
    if "--quiet" not in sys.argv:
        sh = logging.StreamHandler()
        sh.setFormatter(fmt)
        sh.setLevel(logging.DEBUG)
        logging.root.addHandler(sh)

    rfh = logging.handlers.RotatingFileHandler("/var/log/bz-signup.log",
                                               backupCount=10)
    rfh.setFormatter(fmt)
    rfh.setLevel(logging.DEBUG)
    logging.root.addHandler(rfh)
    logging.root.setLevel(logging.DEBUG)

    form = cgi.FieldStorage()
    unsub = open("unsubscribe.page")
    goodbye = open("goodbye.page")
    if (form.has_key("email")):
        remove(form.getvalue("email").encode("utf-8"))
        emit(goodbye)
    else:
        emit(unsub)
 
def emit(text):
    print "Content-type: text/html"
    print 
    print(file.read(text)) 

def remove(email):
    # User-entered data hits the filesystem here.  
    if not validate_email(email):
        return
    checked_email = bleach.clean(email)

    lock = LockFile("/var/local/bz-triage/contributors.cfg")
    lock.acquire()
    try:  
        contributors = json.load(open("/var/local/bz-triage/contributors.cfg"))
    except:
        logging.info("Failed to open the file...")

    for existing in contributors:
        if existing[0] == checked_email:
            contributors.remove(existing)
            logging.info("unsubscribing user: " + checked_email)

    with open("/var/local/bz-triage/contributors.cfg", 'w') as outfile:
        json.dump(contributors, outfile)
    lock.release()
       
if __name__ == "__main__":
    main()
