import smtplib, os.path, sys
from optparse import OptionParser

# VARIABLES, CHANGE YOUR SETTINGS HERE
mailserver = 'le mail server'
mailport = 25
sender = 'somescript@someserver.org'
# END VARIABLES

def readFile(lsfile):
   lsData = ''
   if os.path.exists(lsfile):
      if os.path.isfile(lsfile):
         f = open(lsfile,'r')
         for line in f:
              lsData = lsData + line    
         f.close()
   else: lsData='File '+lsfile+' not found'
   return lsData

def main(argv=None):
   parser = OptionParser(usage='%prog [options] recipient filename')
   parser.add_option("-a", "--attach", dest="attachment", default=False, help="Add the file as attachmente, True or False")
   options, args = parser.parse_args(argv)
   
   if len(args) != 2: parser.error("Incorrect number of arguments.")
   else:
      recipient, file = args
      #do the magic
      lsdata = readFile(file)
      if lsdata == '':
         print >> sys.stderr, "Unable to read file"
      else:
         # add the mail headers manually, the smtp library doesn't.... (funny guys)
         lsheader = ''
         lsheader = lsheader + 'from: ' + sender + '\n'
         lsheader = lsheader + 'to: ' + recipient + '\n'
         lsheader = lsheader + 'subject: mail from ESXI \n'
         lsdata = lsheader + '\n' + lsdata
         try:
            s = smtplib.SMTP()
            s.connect(mailserver, mailport)
            s.sendmail(sender, recipient, lsdata)
            s.quit()
         except: print >> sys.stderr, "Unalbe to send mail"

if __name__=="__main__":
   main()

