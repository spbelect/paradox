#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pip install https://github.com/kivy/kivy/archive/master.zip
import os
import re
from os.path import dirname, join, expanduser
from subprocess import Popen, call, check_output
from pathlib import Path
from textwrap import dedent

os.environ.setdefault('KIVY_NO_CONFIG', '1')
os.environ.setdefault('KIVY_LOG_MODE', 'PYTHON')

import paradox.config

import environ
import click

from app_state import state
from loguru import logger
from click import Context, confirm, command, option, group, argument, ClickException
#from psutil import Process

Context.get_usage = Context.get_help  # show full help on error


#os.chdir(dirname(__file__))
#print(os.getcwd())

def sh(cmd):
    print(cmd)
    return Popen(cmd, shell=True).wait()

#version = open(join(dirname(__file__), 'version.txt')).read().strip()



####raw_input('hit enter')

#sh(f'rm {dist}/bin/{name}-{version}-release-signed.apk')
#sh(f'/home/u1/Android/Sdk/build-tools/23.0.3/zipalign -v 4 {dist}/bin/{name}-{version}-release-unsigned.apk {dist}/bin/{name}-{version}-release-signed.apk')
#sh(f'cp {dist}/bin/{name}-{version}-release-signed.apk /home/u1/')

name = 'paradox'
#name = 'tst'

def init_state(arch):
    if state.debug:
        state.apk = f'{name}-{arch}-debug-{paradox.config.version}.apk'
    else:
        state.apk = f'{name}-{arch}-{paradox.config.version}-release-unsigned.apk'


@group('builder', chain=True)
#@option('--loglevel', '-l', default='INFO',
        #type=click.Choice(list(logging._nameToLevel), case_sensitive=False))
@option('--arch', default='armeabi-v7a', envvar='ANDROID_ARCH',
        type=click.Choice(['armeabi-v7a', 'arm64-v8a', 'x86_64']))
@option('--java_home', envvar='JAVA_HOME', default='/usr/lib64/jvm/java-17-openjdk-17/')
@option('--keypassword', envvar='KEYSTORE_PASSWORD')
@option('--sdk_dir', envvar='ANDROIDSDK', type=click.Path(
    file_okay=False, dir_okay=True, exists=True, resolve_path=True, path_type=Path),
    default=Path.home() / 'Android/Sdk/')
@option('--ndk_dir', envvar='ANDROIDNDK', type=click.Path(
    file_okay=False, dir_okay=True, exists=True, resolve_path=True, path_type=Path))
@option('--debug', is_flag=True, default=False, envvar='DEBUG')
def cli(**kwargs):
    """ Builder. """
    state.update(kwargs)
    #file = f'{dist}/bin/{name}-{version}-release-unsigned.apk'


    try:
        import paradox.config_android
    except ImportError as err:
        raise ClickException('Please copy src/paradox/config_local.example.py to src/paradox/config_android.py, and set SERVER_ADDRESS variable.') from err

    if not paradox.config_android.SERVER_ADDRESS:
        raise ClickException('Please set SERVER_ADDRESS in src/paradox/config_android.py')

    if not state.ndk_dir:
        ndkdir = state.sdk_dir / 'ndk'
        if not ndkdir.exists():
            raise ClickException('no ndk dir specified')
        for dir in ndkdir.iterdir():
            state.ndk_dir = dir
            break
        else:
            raise ClickException('no ndk dir specified')
        # return
    state.adb = f'{state.sdk_dir}/platform-tools/adb'
    state.adb = 'adb'
    
    #state.arch = 'armeabi-v7a'
    #state.arch = 'x86'
    init_state(state.arch)


@cli.command(context_settings={'auto_envvar_prefix': 'PARADOX'})
@click.pass_context
def find(ctx):
    for root, dirs, files in Path.home().walk():
        if root.name.startswith('android-sdk-'):
            print(root)
        elif root.name.startswith('android-ndk-'):
            print(root)


def getrequirements():
    # import tomllib
    # toml = tomllib.load(open('pyproject.toml', 'rb'))

    # sh('pdm lock --lockfile android.lock --prod --platform linux')
    deps = check_output(
        'pdm export --no-hashes --prod --lockfile android.lock',
        shell=True, text=True
    ).lower()

    for dep in deps.split('\n'):
        if dep.startswith('#') or not dep:
            continue
        if re.match('^kivy|pytz|pillow', dep):
            continue
        yield dep.split(';')[0].strip()
        


@cli.command(context_settings={'auto_envvar_prefix': 'PARADOX'})
@click.pass_context
def build(ctx):
    
    #os.environ['JAVA_OPTS'] = '-XX:+IgnoreUnrecognizedVMOptions '#'--add-modules java.se.ee'

    #distdir = '/home/u1/.local/share/python-for-android/dists/%s' % dist

    #args = f'--private /home/z/pproj/kvbugtest --version={version} --bootstrap=sdl2 --window --whitelist=./whitelist.txt --local-recipes="./recipes" --requirements=python3,kivy_myasync,openssl,sqlite3,pillow,pytz,sdl2 --orientation=portrait --dist-name {state.dist} --permission=WRITE_EXTERNAL_STORAGE --permission=READ_EXTERNAL_STORAGE --fileprovider-paths=./fileprovider_paths.xml'

    deps = ','.join(getrequirements())
    #state.package = f'paradox-{state.arch}'
    package = f'{name}dbg' if state.debug else f'{name}'
    
    args = dedent(f'''
        --version={paradox.config.version}
        --dist-name paradox-{state.arch}
        --arch={state.arch}
        --sdk-dir={state.sdk_dir}
        --ndk-dir={state.ndk_dir}

        --package=org.spbelect.{package}
        --name="{package}"

        --private "./src/"
        --bootstrap=sdl2
        --window
        --local-recipes="./recipes"

        --requirements="python3,kivy_2.3.1,openssl,sqlite3,pillow,pytz,sdl2,{deps}"

        --whitelist=./whitelist.txt
        --orientation=portrait
        --android-api=34
        --ndk-api=25
        --enable-androidx

        --permission=CALL_PHONE
        --permission=INTERNET
        --permission=WRITE_EXTERNAL_STORAGE
        --permission=READ_EXTERNAL_STORAGE
    ''')

    if not state.debug:
        args += " --release"

    print(args)
    input('hit enter')

    # debug = '--debug' if state.debug else '--release'
    result = sh('p4a apk {args}'.format(args=args.replace("\n", " ")))

    if not result == 0:
        print('Build failed')
        return  # Error

    # debug build is already signed by p4a
    if not state.debug:
        ctx.invoke(sign)
        ctx.invoke(zipalign)


@cli.command()
def sign():
    keytool = f'{state.java_home}/bin/keytool'
    jarsigner = f'{state.java_home}/bin/jarsigner'
    #keystore = '~/.android/debug.keystore'
    keystore = '~/.keystore'
    key = 'mygooglekey'
    #key = 'key0'
    #key = 'tomcat'
    #key = 'my2'

    #sh(f'{keytool} -genkey -alias {key} -keyalg RSA -validity 99999')

    sh(f'{jarsigner} -verbose:all -sigalg SHA1withRSA -digestalg SHA1 -keystore {keystore} {state.apk} {key} -storepass {state.keypassword}')
    
    
@cli.command()
def zipalign():
    cmd = f'{state.sdk_dir}/build-tools/29.0.0/zipalign'
    sh(f'{cmd} -f 4 {state.apk} align-{state.apk}')


@cli.command()
@click.pass_context
def install(ctx):
    res = check_output(f'{state.adb} devices -l', shell=True, text=True)
    devices = [x.split(maxsplit=1) for x in res.split('\n')[1:] if x]

    if not devices:
        print("No devices found")
        return

    for n, (id, flags) in enumerate(devices):
        print(f"{n}: {id} [{flags}]")

    # id = input(f'Please select device [1-{len(devices)}]:')

    from rich.prompt import Prompt, IntPrompt

    # device = Prompt.ask("Please select device", choices=[x[1] for x in devices])
    device = IntPrompt.ask(
        "Please select device",
        choices=[str(x) for x in range(len(devices))],
        default=0
    )
    id, flags = devices[device]
    if 'x86' in flags:
        state.arch = 'x86_64'
        init_state(state.arch)

    sh(f'{state.adb} install -r -d {state.apk}')

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
    
