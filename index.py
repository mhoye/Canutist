#!/usr/bin/env python

import sys
import json
import cgi
import cgitb
import logging, logging.handlers
from validate_email import validate_email
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
                                               backupCount=10,
                                               maxBytes=100000)
    rfh.setFormatter(fmt)
    rfh.setLevel(logging.DEBUG)
    logging.root.addHandler(rfh)
    logging.root.setLevel(logging.DEBUG)

    logging.info("---- Starting user session... ----")

    form = cgi.FieldStorage()
    index = open("index.page")
    next = open("next.page")
    if (form.has_key("email") and form.has_key("nickname") and form.has_key("number") and form.has_key("rate")):
        emit(next)
        store(form.getvalue("email").encode("utf-8"), 
              form.getvalue("nickname").encode("utf-8"), 
              form.getvalue("number").encode("utf-8"),
              form.getvalue("rate").encode("utf-8") )
    else:
        emit(index)
 
def emit(text):
    index = open("index.page")
    print "Content-type: text/html"
    print 
    print(file.read(text)) 

def store(email,nickname,number,rate):
    # User-entered data hits the filesystem here.  
    #if not validate_email(email):
    #    return

    logging.info("Sanitizing user-provided data...")
    clean_email = bleach.clean(email)  # belt and suspenders, why not.
    clean_nick = bleach.clean(nickname)
    clean_num  = bleach.clean(number)
    clean_rate = bleach.clean(rate)
   
    try:  
        participants = json.load(open("/etc/bz-triage/participants.cfg"))
    except:
        participants = list()
    # If email is in data, remove it.
    
    #FIXME: FILE LOCK RACE CONDITION HERE.

    for optset in participants:
        if optset[0] == clean_email:
            participants.remove(optset)
            logging.info("Replacing redundant entry...")
            break
    else:
        logging.info("Appending new information for user " + str(clean_nick))
        participants.append( [clean_email, clean_nick, clean_num, clean_rate] )
     
    logging.info("Writing table to disk.") 
    with open("/etc/bz-triage/participants.cfg", 'w') as outfile:
        json.dump(participants, outfile)

       
if __name__ == "__main__":
    main()
