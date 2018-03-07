#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os.path import dirname, join
from subprocess import Popen, call
from paradox.config import version

def sh(cmd):
    print cmd
    return Popen(cmd, shell=True).wait()

#version = open(join(dirname(__file__), 'version.txt')).read().strip()
print version

name = 'paradox'

dist_name = 'testpygame'
dist_name = 'testsdl2'
dist_name = 'testsdl22'

if dist_name == 'testsdl22':
    name = 'paradox_2'

dist = '/home/u1/.local/share/python-for-android/dists/%s' % dist_name

cmd = 'p4a apk --private /home/z/pproj/paradox_ssh/ --package=org.spbelect.{name}_debug --name="{name}_debug" --version={version} --bootstrap=sdl2 --local-recipes=./p4a-recipes --requirements=python2,kivy,openssl,pil,requests,sdl2,tinydb,plyer --whitelist=./whitelist.txt'.format(**locals())

#cmd = 'p4a apk --private /home/z/pproj/paradox_ssh/ --package=org.spbelect.{name}_debug --name="{name}_debug" --version={version} --dist-name {dist_name} --orientation=portrait --blacklist=/home/z/pproj/paradox_ssh/blacklist.txt --permission=INTERNET --permission=CALL_PHONE'.format(**locals())
print cmd

### adb logcat | grep -E "SDL|[pP]ython|linker|spbelect|dlopen"

#raw_input('hit enter')
sh(cmd)


#sh('p4a apk --release --private /home/z/pproj/paradox_ssh/ --package=org.spbelect.{name} --name="{name}" --version={version} --dist-name {dist_name} --orientation=portrait --blacklist=/home/z/pproj/paradox_ssh/blacklist.txt --permission=INTERNET --permission=CALL_PHONE'.format(**locals()))
#sh('jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore ~/keystores/mygooglekey.keystore {dist}/bin/{name}-{version}-release-unsigned.apk mygooglekey'.format(**locals()))
#sh('rm {dist}/bin/{name}-{version}-release-signed.apk'.format(**locals()))
#sh('/home/u1/Android/Sdk/build-tools/23.0.3/zipalign -v 4 {dist}/bin/{name}-{version}-release-unsigned.apk {dist}/bin/{name}-{version}-release-signed.apk'.format(**locals()))
#sh('cp {dist}/bin/{name}-{version}-release-signed.apk /home/u1/'.format(**locals()))

sh('adb install -r paradox-{version}-debug.apk'.format(**locals()))
