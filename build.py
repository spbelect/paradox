#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pip install https://github.com/kivy/kivy/archive/master.zip
import os
from os.path import dirname, join
from subprocess import Popen, call
from paradox.config import version

import environ
import click
from app_state import state
from loguru import logger
from click import Context, confirm, command, option, group, argument
#from psutil import Process

Context.get_usage = Context.get_help  # show full help on error


#os.chdir(dirname(__file__))
#print(os.getcwd())

def sh(cmd):
    print(cmd)
    return Popen(cmd, shell=True).wait()

#version = open(join(dirname(__file__), 'version.txt')).read().strip()
print(version)


####raw_input('hit enter')

#sh(f'rm {dist}/bin/{name}-{version}-release-signed.apk')
#sh(f'/home/u1/Android/Sdk/build-tools/23.0.3/zipalign -v 4 {dist}/bin/{name}-{version}-release-unsigned.apk {dist}/bin/{name}-{version}-release-signed.apk')
#sh(f'cp {dist}/bin/{name}-{version}-release-signed.apk /home/u1/')


@group('builder', chain=True)
#@option('--loglevel', '-l', default='INFO',
        #type=click.Choice(list(logging._nameToLevel), case_sensitive=False))
@option('--arch', default='armeabi-v7a', envvar='ANDROID_ARCH',
        type=click.Choice(['armeabi-v7a', 'x86']))
@option('--java_home', envvar='JAVA_HOME')
@option('--keypassword', envvar='KEYSTORE_PASSWORD')
@option('--sdk_dir', envvar='ANDROIDSDK')
@option('--debug', is_flag=True, default=False, envvar='DEBUG')
def cli(**kwargs):
    """ Builder. """
    state.update(kwargs)
    #file = f'{dist}/bin/{name}-{version}-release-unsigned.apk'

    state.adb = f'{state.sdk_dir}/platform-tools/adb'
    state.adb = 'adb'
    
    
    #state.arch = 'armeabi-v7a'
    #state.arch = 'x86'
    
    name = 'paradox'
    #name = 'tst'
    state.dist = f'{name}-{state.arch}'
    #state.package = f'paradox-{state.arch}'
    state.package = f'{name}2dbg' if state.debug else f'{name}2'
    if state.debug:
        state.apk = f'{name}-{version}-{state.arch}-debug.apk'
    else:
        state.apk = f'{name}-{version}-{state.arch}-release-unsigned.apk'
    

def getrequirements():
    for x in open('requirements.txt'):
        if x.startswith('Kivy') or x.startswith('pytz'):
            continue
        yield x.strip()
        
@cli.command(context_settings={'auto_envvar_prefix': 'PARADOX'})
@click.pass_context
def build(ctx):
    
    #os.environ['JAVA_OPTS'] = '-XX:+IgnoreUnrecognizedVMOptions '#'--add-modules java.se.ee'

    # DEPRECATED
    #os.environ['ANDROIDNDKVER'] = 'r9c'
    #os.environ['ANDROIDNDKVER'] = 'r18b'

    requirements = ','.join(getrequirements())
        
    #name = 'paradox2dbg' if state.debug else 'paradox2'

    #distdir = '/home/u1/.local/share/python-for-android/dists/%s' % dist

    #args = f'--private /home/z/pproj/kvbugtest --version={version} --bootstrap=sdl2 --window --whitelist=./whitelist.txt --local-recipes="./recipes" --requirements=python3,kivy_myasync,openssl,sqlite3,pillow,pytz,sdl2 --orientation=portrait --dist-name {state.dist} --permission=WRITE_EXTERNAL_STORAGE --permission=READ_EXTERNAL_STORAGE --fileprovider-paths=./fileprovider_paths.xml'
    
    
    args = f'--private {dirname(__file__)} --version={version} --bootstrap=sdl2 --window --local-recipes="./recipes" --requirements=python3,kivy_myasync,openssl,sqlite3,pillow,pytz,sdl2,{requirements} --whitelist=./whitelist.txt --permission=CALL_PHONE --permission=INTERNET --permission=WRITE_EXTERNAL_STORAGE --permission=READ_EXTERNAL_STORAGE --orientation=portrait --dist-name {state.dist} --fileprovider-paths=./fileprovider_paths.xml --arch={state.arch}'

    print(args)
    input('hit enter')

    debug = '--debug' if state.debug else '--release'
    sh(f'p4a apk {args} --package=org.spbelect.{state.package} --name="{state.package}" {debug}')
    
    # debug build is already signed by p4a
    if not state.debug:
        ctx.invoke(sign)


@cli.command()
def sign():
    keytool = f'{state.java_home}/bin/keytool'
    jarsigner = f'{state.java_home}/bin/jarsigner'
    #keystore = '~/.android/debug.keystore'
    keystore = '~/.keystore'
    #key = 'mygooglekey'
    #key = 'key0'
    key = 'tomcat'

    #sh(f'keytool -genkey -alias {key} -keyalg RSA')

    sh(f'{jarsigner} -verbose:all -sigalg SHA1withRSA -digestalg SHA1 -keystore {keystore} {state.apk} {key} -storepass {state.keypassword}')


@cli.command()
@click.pass_context
def install(ctx):
    sh(f'{state.adb} install -r {state.apk}')
    
    input('hit enter')
    ctx.invoke(logcat)


@cli.command()
def logcat():
    sh(f'{state.adb} logcat -v time | grep --line-buffered -E "SDL|[pP]ython|linker|spbelect|dlopen" | grep --line-buffered -vE "extracting|unused"')
    #sh(f'{state.adb} -d logcat -v time | grep --line-buffered -vE "WordingCode|RATE_LIMITED_API_CALLS|ResourcesManager|Finsky|StatusBar|LocationController|ServiceManager|PowerManagerService|VideoCapabilities|ActivityManager|SoLoader|SwipeUpService|wpa_supplicant|GoogleSignatureVerifier|ResourceType|DefaultAppManager|AccountTypeManager|SendRegistrationId|FingerGoodix|GetSettingsFromServerCm|W\/Resources|NetworkResolver|AlarmManager|PathParser|NetworkManagementService|FingerService|AmSmartShowFuncsImpl|extracting|PackageManager|Icing|CalendarSyncAdapter|RuntimeConfig|TaskManager|RecentTasksLoader|tnet-jni|WifiHAL|Plume|WifiService|vigi_ZteDrm|InputDispatcher|unused"')


if __name__ == '__main__':
    env = environ.Env()
    env.read_env('env-local')
    
    #import uvloop
    #uvloop.install()

    #from signal import SIGINT, signal
    #signal(SIGINT, utils.sigint_handler)    
    
    cli(auto_envvar_prefix='PARADOX')
    
