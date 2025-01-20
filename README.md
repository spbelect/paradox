[![Tests](https://github.com/spbelect/paradox/actions/workflows/ci.yml/badge.svg)](https://github.com/spbelect/paradox/actions/workflows/ci.yml)

# Development

```
pdm venv create
eval $(pdm venv activate)

pdm install --dev
```

## Testing

```
pytest
```

## Android build

### Install python-for-android

```
pipx install git+https://github.com/kivy/python-for-android.git@develop
pipx inject python-for-android ipdb
```

### Install development tools and libs

`zypper in java-17-openjdk java-17-openjdk-devel patch cmake autoconf automake libtool libopenssl-devel python311-Cython`


### Download Android Studio

in android studio:
More actions > SDK Manager
tab SDK Tools > check ANDROID SDK command-line tools (latest)

### Download NDK

> wget https://dl.google.com/android/repository/android-ndk-r27c-linux.zip
> unzip android-ndk-r27c-linux.zip

or go to https://developer.android.com/ndk/downloads/index.html and download manually

Add to ~/.bashrc:

### Set environment variables

```
export ANDROIDSDK=~/Android/Sdk"
export ANDROIDNDK=~/Downloads/android-ndk-r27c"
export JAVA_HOME="/usr/lib64/jvm/java-17-openjdk-17/"
```

`. ~/.bashrc`

### Build

`./build.py --debug --arch=x86_64 build`


### Manage dependencies

If dependencies have been changed in pyproject.toml, you must regenerate android lockfile: `pdm lock --lockfile android.lock --prod --platform linux`
