# Created by Somers.R on 07/05/2006
# used as part of a backup utility
# this program requires three parameters: email server email address and file


import string
import sys
import os
import socket

xVersion = "FileMailer 1.0"
parmFile = ""
parmServer = ""
parmEmail = ""
parmSubject = ""

def CheckFileExists(xfile=""):
    try:
        f = open(xfile,"r")
        return 1
    except IOError, (errno, strerror):
        print "file not found: " + xfile
        return 0

# End 

def SetParams():                                        # checks if all parameters arethere and loads them in global variables
    try:                                                # sys.argv[0] = executable file name
        global parmServer                               # have to be trapped as being global vars
        parmServer = sys.argv[1]                        # email server
        global parmEmail
        parmEmail = sys.argv[2]                         # address of recipient
        global parmFile
        parmFile = sys.argv[3]                          # file to send
        return 1
    except IndexError:
        print "correct usage: file_mailer 'mailserver' 'recipient address' 'file to send'"
        return 0

# End
def TakeTimeOut(xSock, data):
#waits for a response, then sends next data
    while data == "":
        data = xSock.recv(100)

    print data
    return 1

# end


def SendFile(sServer, sRecipient, sFile):
    x = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    x.connect ((sServer, 25))
    TakeTimeOut(x,"")
    x.send("HELO FileMailer1.0\r\n")
    TakeTimeOut(x,"")
    x.send("MAIL FROM: FileMailer@working.net\r\n")
    TakeTimeOut(x,"")
    x.send("RCPT TO: " + sRecipient + "\r\n")
    TakeTimeOut(x,"")
    x.send("DATA\r\n")
    x.send("From: FileMailer@working.net\r\n")
    x.send("To:" + sRecipient + "\r\n")
    x.send("Subject: " + xVersion + " sends you the file " + sFile + "\r\n")
    x.send("\r\n")                                        #needed to end headers and start body
    f = open(sFile)
    for line in f:
        x.send(line)
    x.send(xVersion + "\r\nCreated by Somers.R     (Python Powered)\r\n")
    x.send("\r\n.\r\n")
    TakeTimeOut(x,"")
    x.send("QUIT\r\n")
    TakeTimeOut(x,"")
    x.close
    print "email send"
# end
    
def main():                                             # run main routines
    SendFile(parmServer,parmEmail,parmFile)

# end

def startup_check():                                    #triggers everything
    os.system('cls')
    print "Filemailer 1.0 by somers.r"
    print "--------------------------"
    gp = SetParams()
    if gp != 0:                                         # if all parameters are set
        fx = CheckFileExists(parmFile)                  # and the file to send exists
        if fx != 0:             
            main()                                      # run main routine

# end

#start program
startup_check()
