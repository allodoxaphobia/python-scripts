#!/usr/bin/env python
import sqlite3
import subprocess
import os

DB_FILE = "/tmp/Cache.db"
TABLE_NAME= "cfurl_cache_blob_data"
FIELD_NAME = "request_object"

#DEST = Folder where files will be stored, trailing / required
DEST= "/tmp/sqlitefile/"

#AFTER_COMMAND = command to execute after each blob is extracted, supports $FILE replace code
AFTER_COMMAND = "perl ~/tools/plutil.pl $FILE"

#CLEANUP_AFTER_COMMAND, set to True to remove original files after command executed
CLEANUP_AFTER_COMMAND = True 

def writetofile(data,filen):
	try:
		with open(filen,"w") as f:
			f.write(data)
			f.close
		return True
	except Exception,e:
		print "Failed to write to file " + filen +", " + e.message
		return False

def main():
	if CLEANUP_AFTER_COMMAND== True:
		print "You selected to delete original export files after additional command execution."
		print "This means that original exported fiels will be deleted."
		var = raw_input("Do you wish to continue [y/N]: ")
		if var.lower()!="y":
			exit(0)
	try:
		con = sqlite3.connect(DB_FILE)
		cur = con.cursor()    
		print 'Executing SELECT ' +  FIELD_NAME + ' FROM ' + TABLE_NAME + ';'
		cur.execute('SELECT ' +  FIELD_NAME + ' FROM ' + TABLE_NAME + ';')
		i = 0 
		for row in cur: #cur does fetchall automagically
			i=i+1
			data = row[0]
			filen = DEST + "BLOB_"+str(i)
			if writetofile(data,filen)==True:
				print "Created file " + filen
				tmpcmd = AFTER_COMMAND
				tmpcmd = tmpcmd.replace("$FILE", filen)
				try:
					p = subprocess.Popen(tmpcmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
					retval = p.wait()
					if retval == 0: #command success
						if CLEANUP_AFTER_COMMAND==True:
							os.remove(filen)
							print "Cleaned up file " + filen
					print "Executed " + tmpcmd
				except Exception,e:
					print "Failed to trigger commmand for " + filen
		con.close()
	except Exception, e:
		print e.message

main()
