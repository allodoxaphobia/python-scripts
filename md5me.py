#!/usr/bin/env python
import time
import md5
import base64

def calchash(val):
	m = md5.new()
	m.update(str(val))
	binval= m.digest()
	val64= base64.b64encode(binval)
	return val64

tmp = calchash(time.time()).upper()
print tmp
