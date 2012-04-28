import sys
import subprocess
import urllib.parse, urllib.request
import json
from optparse import OptionParser

BASE_URL_TRANSLATE = "http://translate.google.com/translate_a/t?client=t&text=$ORIGTEXT&hl=en&sl=auto&tl=$TOLANG&multires=1&prev=enter&ssel=0&tsel=0&uptl=$TOLANG&sc=1"
BASE_URL_VOICE = "http://translate.google.com/translate_tts?ie=UTF-8&q=$TEXT&tl=$TOLANG"
HTTP_PROXY= 'http://10.1.14.81:9999'
HTTP_AGENT='spoofy/1.1'
PLAYER = "c:\\Program Files (x86)\\Windows Media Player\\wmplayer.exe"
#PLAYER = """c:\\Program Files (x86)\\VideoLAN\\VLC\\vlc.exe"""
PLAYER_TEMP_FILE = "c:\\tmp.mpeg"
PLAYER_ARGS = [PLAYER_TEMP_FILE," /close"]

def GetTranslation(OrigText,DestLanguage):
#    geturl = urllib.request.Request("+DestLanguage+""+DestLanguage+"")
    lsurl =BASE_URL_TRANSLATE.replace('$ORIGTEXT',OrigText)
    lsurl = lsurl.replace('$TOLANG',DestLanguage)
    geturl = urllib.request.Request(lsurl)
    geturl.add_header('User-Agent',HTTP_AGENT)
    proxy = urllib.request.ProxyHandler({'http': HTTP_PROXY})
    opener = urllib.request.build_opener(proxy)
    f= opener.open(geturl,None,None)
    return  f.read().decode('ISO-8859-1')

    

def parsetranslation(lstext):
    translation=lstext.split('[')[3]
    translation=translation.split(",")
    lsresult = translation[0]
    return lsresult

#end def

def getMP3(lstext,lslang):
    lsurl = BASE_URL_VOICE.replace('$TEXT',lstext)
    lsurl = lsurl.replace('$TOLANG',lslang)
    geturl = urllib.request.Request(lsurl)
    geturl.add_header('User-Agent',HTTP_AGENT)
    proxy = urllib.request.ProxyHandler({'http': HTTP_PROXY})
    opener = urllib.request.build_opener(proxy)

    f= opener.open(geturl,None,None)
    return  f.read()


def main(argv=None):
    parser = OptionParser(usage='%prog text lang')
    options, args = parser.parse_args(argv)
    text, lang = args
    print ("translating to  "  + lang)
    translation = GetTranslation(text,lang)
    translation = parsetranslation(translation)
    print(translation)
    mp3 = getMP3(translation, lang)
    f= open(PLAYER_TEMP_FILE,'wb')
    f.write(mp3)
    f.close()
    subprocess.call([PLAYER,  PLAYER_ARGS])
        
#end def
if __name__=="__main__":
   main()
