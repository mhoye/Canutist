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
    index = open("index.page")
    next = open("next.page")
    if (form.has_key("email") and form.has_key("nickname") and form.has_key("number") and form.has_key("rate")):
        emit(next)
        store(form.getvalue("email").encode("utf-8"), 
              form.getvalue("nickname").encode("utf-8"), 
              form.getvalue("number").encode("utf-8"),
              form.getvalue("rate").encode("utf-8"),
              form.getvalue("strs").encode("utf-8"),
              form.getvalue("regressions").encode("utf-8"))
              
    else:
        emit(index)
 
def emit(text):
    index = open("index.page")
    print "Content-type: text/html"
    print 
    print(file.read(text)) 

def store(email,nickname,number,rate,strs,regressions):
    # User-entered data hits the filesystem here.  
    if not validate_email(email):
        return

    newcontrib = [ bleach.clean(email), 
                   bleach.clean(nickname), 
                   bleach.clean(number), 
                   bleach.clean(rate),
                   bleach.clean(strs),
                   bleach.clean(regressions)]

    lock = LockFile("/var/local/bz-triage/contributors.cfg")
    lock.acquire()
    
    try:  
        contributors = json.load(open("/var/local/bz-triage/contributors.cfg"))
    except:
        logging.info("Failed to open the file...")
        contributors = list()

    for existing in contributors:
        if existing[0] == newcontrib[0]:
            contributors.remove(existing)
    contributors.append( newcontrib )

    with open("/var/local/bz-triage/contributors.cfg", 'w') as outfile:
        json.dump(contributors, outfile)
    lock.release()
       
if __name__ == "__main__":
    main()
