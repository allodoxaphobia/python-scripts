from socket import *


def checkhost(hostname, sck):
    try:
        data=sck.recv(1024)
        cmd_helo= 'helo ' + hostname +'\r\n'
        cmd_rset= 'rset\r\n'
        sck.settimeout(1)
        sck.send(cmd_helo.encode('utf-8'))
        data=sck.recv(1024)
        if data:
            print(hostname)
        sck.send(cmd_rset.encode('utf-8'))
    except: return 0

#end def



s = socket(AF_INET, SOCK_STREAM)
s.connect(("name of mailserver here",25))
s.settimeout(5)
data=s.recv(1)


#scan
hosts = open('D:\Own_development\Python\SIDScan.lst').read()
hosts.replace('\r','\n')
hosts.replace('\n\n','\n')
for lohost in hosts.split('\n'):
    checkhost(lohost,s)

#end for

