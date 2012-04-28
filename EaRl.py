import socket
import base64
def tryURL (rhost, rport, url):
    #error recovery
    if rhost == "": rhost = "localhost"
    if url == "": url = "/"
    if rport == "" or rport == 0:rport = 80
    #connect
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.connect((rhost,rport)) 
    s.send('GET ' + url + ' HTTP/1.0\n\n')
    data = s.recv(15) 
    s.close() 
    #validate response
    if "200" in data:return "200"
#end
def tryURL_proxy (rhost, rport, url,proxy,proxyport,authstr):
    #error recovery
    if rhost == "": rhost = "localhost"
    if url == "": url = "/"
    url = url.replace('\n','')
    url = url.replace('\r','')    
    if rport == "" or rport == 0:rport = 80
    #connect
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.connect((proxy,int(proxyport))) 
    msg='GET http://'+rhost+':'+str(rport)+ url + ' HTTP/1.0\n'
    msg=msg+'Host: '+rhost+'\n'
    msg=msg+'Proxy-Authenticate: Basic '+authstr+'\r\n\r\n'
    
    s.send(msg)
    data = s.recv(15) 
    s.close() 
    #validate response
    if "200" in data:return "200"
#end
    
def scanDict(proxy=''):
    f = open("urls.txt","r")
    for line in f:
        if proxy == "":
            tryit = tryURL(rhost,rport,line)
        else:
            tryit = tryURL_proxy(rhost,rport,line,proxy,proxyport,proxuser)
        if tryit=="200": print "200 OK " + line,
#end

#def main_routine
print "Earl Scanner 1.0"
print "----------------"
#get remote host and port
rhost = raw_input("enter remote host: ")
if len(rhost)==0: rhost = "localhost"
rport = raw_input("enter remote port(80): ")
if len(rport) == 0:
    rport = 80
else:
    rport=int(rport)
useprox = raw_input("Do you want to use a proxy server(y/n default is n):")
proxy=""                                   #error recovery
if useprox=='y':
    proxy = raw_input("Enter proxy server: ")
    proxyport= raw_input("Enter a proxy port(3128):")
    if len(proxyport)==0:proxyport=3128
    proxuser = raw_input("Enter username and pass (user:pass): ")
    proxuser= base64.encodestring(proxuser)
print "trying to connect to " + rhost + " on port " + str(rport)
print "Found following pages: "
scanDict(proxy)      #start scanning URLs from dictionary file
print "----------------"
print "finished scanning"
x=raw_input("press enter to exit")
#end
