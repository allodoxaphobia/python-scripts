#!/usr/bin/env python
import urllib2

#url format print_data|request_confirmation|label|url
#set label to X to ignore
#set print_data to 1 to print label and result rather then just the url
#set request_confirmation to 1 for agressive stuff such as reset/reboot/clear logs etc

IP="192.168.1.1"

urls={"0|BASE|http://$IP:9000/",
"0|0|WEB CONFIG|http://$IP:9000/webconfig",
"0|0|WEB CONFIG|http://$IP:9000/config",
"0|0|WEB SETUP|http://$IP:9000/#setup",
"0|0|DUMP PARAMS|http://$IP:9000/rpc/get_all",
"0|0|X|http://$IP:9000/rpc/portal_page",
"0|0|X|http://$IP:9000/rpc/portal_page?login",
"0|0|X|http://$IP:9000/rpc/portal_page?login24",
"0|0|X|http://$IP:9000/rpc/portal_page?register",
"0|0|WEBDAV_ENABLED|http://$IP:9000/rpc/get_webdav_link",
"0|0|PORTAL INFO|http://$IP:9000/rpc/get_portal_info",
"0|0|Browse Dirs|http://$IP:9000/rpc/dirs?path=001",
"0|0|IS PORTAL ONLINE|http://$IP:9000/rpc/get_portal_info?onlineStatus",
"0|0|STATUS|http://$IP:9000/rpc/info_status",
"0|0|NAME|http://$IP:9000/rpc/get_friendlyname",
"0|0|SERVER TYPE|http://$IP:9000/rpc/get_server_type",
"0|0|TIMEOUT|http://$IP:9000/rpc/get_timeout_period",
"0|0|NICS|http://$IP:9000/rpc/info_nics",
"0|0|X|http://$IP:9000/rpc/get_option",
"0|0|PORTAL USER|http://$IP:9000/rpc/get_option?portalusername",
"0|0|X|http://$IP:9000/rpc/get_option?",
"0|0|ACTIVE STREAM|http://$IP:9000/rpc/stream_active",
"0|0|Web Browser|http://$IP:9000/webbrowse'",
"0|0|Web DAVProxy|http://$IP:9000/rpc/webdavproxy",
"0|0|X|http://$IP:9000/rpc/webdavproxy?/rpc/webdav/get_shares",
"0|0|X|http://$IP:9000/rpc/webdavproxy?/rpc/webdav/get_users",
"0|0|X|http://$IP:9000/rpc/webdavproxy?/rpc/webdav/get_rights",
"0|0|X|http://$IP:9000/rpc/webdavproxy?/rpc/webdav/",
"0|0|X|http://$IP:9000/rpc/webdavproxy?/rpc/webdav/get_admin_account",
"0|1|REBUILD DATABASE|http://$IP:9000/rpc/rebuild",
"0|1|RESCAN|http://$IP:9000/rpc/rescan",
"0|1|RESET|http://$IP:9000/rpc/reset",
"0|1|RESTART|http://$IP:9000/rpc/restart",
"0|1|STOP|http://$IP:9000/rpc/stop",
"1|0|VERSION|http://$IP:9000/rpc/version",
"0|0|SCANNER STATISTICS|http://$IP:9000/rpc/stat",
"0|0|SCANNER STATISTICS|http://$IP:9000/rpc/statistics",
"0|0|LOG|http://$IP:9000/rpc/log_getfile",
"0|1|CLEAR_LOG|http://$IP:9000/rpc/log_clearfile",
"0|0|LOG-DISABLE|http://$IP:9000/rpc/log_disable?1",
"0|0|LOG-DISABLE|http://$IP:9000/rpc/log_disable?0",
"1|0|MEMORY|http://$IP:9000/rpc/memory",
"0|0|CLIENTS|http://$IP:9000/rpc/info_clients",
"0|0|CLIENTS|http://$IP:9000/rpc/get_clients",
"0|0|ADD CLIENT MAC|http://$IP:9000/rpc/client_add?mac=AA:BB:CC:DD:EE:FF?id=172?enabled=1?view=advanceddefault",
"0|0|DELETE CLIENT MAC|http://$IP:9000/rpc/client_delete?mac=AA:BB:CC:DD:EE:FF",
"0|0|CONNECTED CLIENTS|http://$IP:9000/rpc/info_connected_clients",
"0|0|STREAM INFO|http://$IP:9000/rpc/stream_info",
"0|1|RESET CLIENTS|http://$IP:9000/rpc/resetclients",
"0|0|MEDIA FUSION|http://$IP:9000/rpc/mediafusion",
"0|0|MEDIA FUSION PROXY|http://$IP:9000/rpc/mediafusionproxy",
"0|0|AGGRAGATION|http://$IP:9000/rpc/aggregation",
"1|0|BAD FILES|http://$IP:9000/rpc/bad_files",
"0|1|CLEAR CACHE|http://$IP:9000/rpc/clear_cache",
"0|0|X|http://$IP:9000/rpc/set_option",
"0|0|X|http://$IP:9000/rpc/set_option?",
"0|0|X|http://$IP:9000/json",
"0|0|JSON FEED|http://$IP:9000/json/feed",
"0|0|HELP(has directory traversal issue)|http://$IP:9000/help/"}

def pageexists(req):
	try:
		result = urllib2.urlopen(req)
		return 1
        except urllib2.HTTPError, e:
            	return 0

def getcontent(req):
	try:
		result = urllib2.urlopen(req)
		return result.read()
        except urllib2.HTTPError, e:
            	return ""

def printheader(header):
	print "\n"
	print header
	print "-----------------------------------------------------------"

founduri=[]

for url in urls:
	data = url.split("|")
	if data[1]=="0":
		if data[2] != "X":
			if data[0]=="0":
				if pageexists(data[3].replace("$IP",IP))==1:founduri.append(data[3].replace("$IP",IP))
			elif data[0]=="1":
				printheader(data[2])
				print getcontent(data[3].replace("$IP",IP))
	else:
		print "Omitting " + data[3].replace("$IP",IP)
printheader("Enabled URLS")

for x in founduri:
	print x
