#!/usr/bin/env python
"""
========================================================================================================
XNFTP.PY - Created by R. Somers as an adaptation of nftp.py
      nftp.py was created by
      Author: Sean B. Palmer, inamidst.com
      License: GNU GPL 2
      Date: 2003-11
=========================================================================================================


"""

import sys, os, re, ftplib, datetime
from optparse import OptionParser

r_field = re.compile(r'(?s)([^\n:]+): (.*?)(?=\n[^ \t]|\Z)')

def writeLog(lsmsg):
   #writes timestamped log entry 
   ldate = datetime.datetime.now().strftime("%Y%m%d")
   logfile = open("arcoftp-" + ldate + ".log","a")
   logfile.write(getTime() + "   " + lsmsg+"\r\n")
   logfile.close()

def getTime():
   ltime =  datetime.datetime.now().strftime("%H:%M:%S")
   return ltime

def getConfig(name=None): 
   # Find the config file
   home = os.path.expanduser('~/')
   nftp_conf = os.getenv('NFTP_CONF')
   if os.path.exists('./xnftp.conf'): 
      s = open('./arcoftp.conf').read()
   else: return {}

   # Parse the config file
   conf = {}
   s = s.replace('\r\n', '\n')
   s = s.replace('\r', '\n')
   for item in s.split('\n\n'): 
      meta = dict(r_field.findall(item.strip()))
      if meta.has_key('name'): 
         fname = meta['name']
         del meta['name']
         conf[fname] = meta
      else: raise 'ConfigError', 'Must include a name'

   if name is not None: 
      return conf[name]
   else: return conf

def getFtp(meta): 
   ftp = ftplib.FTP(meta['host'], meta['username'], meta['password'])
   ftp.cwd(meta['remotedir'])
   # writeLog("Connection establisched")
   return ftp

def upload(name, filepath): 
   meta = getConfig(name)

   ftp = getFtp(meta)
   path, fn = os.path.split(filepath)
   path = path.lstrip('/') or '.'
   try:
      ftp.cwd(path)
   except:
      for folder in path.split("/"):
         try: ftp.cwd(folder)
         except:
            try:
               ftp.mkd(folder)
               ftp.cwd(folder)
            except:
               writeLog("Error creating target directory "+path)

   f = open(os.path.join(meta['localdir'], path+'/'+fn), 'rb')
   writeLog("PUT START: " + filepath + ":   " + path+'/')
   result = ""
   result = ftp.storbinary('STOR %s' % fn, f)
   writeLog("PUT END: " + filepath + ":   " + result)
   f.close()

def uploaddir(name, dir):
   for subdir, dirs, files in os.walk(dir):
      for file in files:
         upload(name, dir+"/"+file)

# upload, -c chmod, -d delete, -u update, -g get

def main(argv=None): 
   parser = OptionParser(usage='%prog [options] <name> <path>')
   parser.add_option("-u", "--update", dest="update", 
                     action="store_true", default=False, 
                     help="update a file, on the server or locally")
   parser.add_option("-d", "--dir", dest="directory", 
                     default="", 
                     help="Upload all files in a driectory")

   options, args = parser.parse_args(argv)

   if (len(args) < 1) or (len(args) > 2): 
      parser.error("Incorrect number of arguments")
   elif len(args) == 1: 
      if options.directory:
         name = args[0]
         uploaddir(name, options.directory)
      else:
         print >> sys.stderr, "Incorrect number of arguments, no profile specified"
         sys.exit(1)
   else: 
      name, filepath = args
      upload(name, filepath)

if __name__=="__main__": 
   main()

