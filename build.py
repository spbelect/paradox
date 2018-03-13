#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from os.path import dirname, join
from subprocess import Popen, call
from paradox.config import version

os.environ['ANDROIDAPI'] = '17'
os.environ['ANDROIDNDK'] = '/home/z/soft/android-ndk-r12b/'
os.environ['ANDROIDSDK'] = '/home/u1/Android/Sdk/'
os.environ['ANDROIDNDKVER'] = 'r9c'

def sh(cmd):
    print cmd
    return Popen(cmd, shell=True).wait()

#version = open(join(dirname(__file__), 'version.txt')).read().strip()
print version

name = 'paradox'

dist_name = 'testpygame'
dist_name = 'testsdl2'
dist_name = 'testsdl22'
dist_name = 'unnamed_dist_2'

if dist_name == 'testsdl22':
    name = 'paradox_2'

dist = '/home/u1/.local/share/python-for-android/dists/%s' % dist_name

args = '--private /home/z/pproj/paradox_ssh/ --version={version} --bootstrap=sdl2 --local-recipes=./p4a-recipes --requirements=python2,kivy,openssl,pil,requests,sdl2,tinydb,plyer --whitelist=./whitelist.txt --permission=CALL_PHONE --permission=INTERNET --orientation=portrait'.format(**locals())

cmd = 'p4a apk {args} --package=org.spbelect.{name}_debug --name="{name}_debug"'.format(**locals())

#cmd = 'p4a apk --private /home/z/pproj/paradox_ssh/ --package=org.spbelect.{name}_debug --name="{name}_debug" --version={version} --dist-name {dist_name} --orientation=portrait --blacklist=/home/z/pproj/paradox_ssh/blacklist.txt --permission=INTERNET --permission=CALL_PHONE'.format(**locals())
#print cmd


#sh(cmd)
jarsigner = '/usr/lib64/jvm/java-1.8.0-openjdk-1.8.0/bin/jarsigner'

sh('p4a apk {args} --package=org.spbelect.{name} --name="{name}" --release '.format(**locals()))
sh('{jarsigner} -verbose:all -sigalg SHA1withRSA -digestalg SHA1 -keystore ~/keystores/mygooglekey.keystore {dist}/bin/{name}-{version}-release-unsigned.apk mygooglekey'.format(**locals()))

#raw_input('hit enter')

sh('rm {dist}/bin/{name}-{version}-release-signed.apk'.format(**locals()))
sh('/home/u1/Android/Sdk/build-tools/23.0.3/zipalign -v 4 {dist}/bin/{name}-{version}-release-unsigned.apk {dist}/bin/{name}-{version}-release-signed.apk'.format(**locals()))
sh('cp {dist}/bin/{name}-{version}-release-signed.apk /home/u1/'.format(**locals()))

#####sh('adb install -r paradox-{version}-debug.apk'.format(**locals()))


### adb logcat | grep -E "SDL|[pP]ython|linker|spbelect|dlopen"
