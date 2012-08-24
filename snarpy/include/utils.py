from random import randint
import socket
import fcntl
import struct


def mergearrays(containingarray, extendingarray):
	tmparr = containingarray
	if len(extendingarray)>0:
		for newbyte in extendingarray:
			tmparr.append(newbyte)
	return tmparr

def dotteddec2binary(ip):
	tmpIP = ip.split('.')
	result = bytearray()
	for ipblock in tmpIP:
		result.append(int(ipblock))
	return result

def mac2binary(mac):
	tmpMAC = mac.split(':')
	result = bytearray()
	for part in tmpMAC:
		result.append(int(part,16))
	return result

def randommac():
	randval1 = randint(0,255)
	randval2= randint(0,255) #technically (TODO) : the last 2 bits must be 0 as per IEEE 802.3-2002 Section 3.2.3(b)
	randval3 = randint(0,255)
	randval4 = randint(0,255)
	randval5 = randint(0,255)
	randval6= randint(0,255)
	randmac= int2mac(randval1) + ":" +int2mac(randval2) + ":" + int2mac(randval3) + ":" + int2mac(randval4) + ":" + int2mac(randval5) + ":" + int2mac(randval6)
	return randmac

def int2mac(integr):
	#converts integer to hex string of exactly 2 characters
	#only int 0-255 allowed, if larger, 00 is returned
	if (integr <0) or  (integr > 255):
		return "00"
	else:
		result = hex(integr)
		result = result.replace("0x","")
		while len(result)< 2:
			result = "0" + result
		return result
	
	#fi

def getinterface_ip(interface):
	#copy/pasta
    	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	return socket.inet_ntoa(fcntl.ioctl(s.fileno(),0x8915, struct.pack('256s', interface[:15]))[20:24])

def getinterface_mac(interface):
	    #copy/pasta
	    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
	    info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', interface[:15])) 
	    return ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1]
 
