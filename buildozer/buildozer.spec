[app]

# (str) Title of your application
title = Braille Learner

# (str) Package name
package.name = braillelearner

# (str) Package domain (needed for android/ios packaging)
package.domain = xyz.braille.learner

# (str) Application versioning
version = 1.0.1

# (list) Application requirements
requirements = python3,kivy

##############################################

# (str) Source code where the main.py live
source.dir = .

# (str) The entry point of the application
entrypoint = main.py

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,kv,png,jpg,jpeg,ttf,otf,atlas,txt,json

# (list) List of inclusions using pattern matching
source.include_patterns = assets/**

# (list) Source files to exclude
source.exclude_dirs = .git, .idea, __pycache__, venv, .venv, build, bin, tests, dist

icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/presplash.png

# (list) Supported orientations
orientation = portrait





#############################################################################################





# Android specific
##############################################

# (list) The Android archs to build for
android.archs = arm64-v8a, armeabi-v7a

# (list) Permissions
# android.permissions = VIBRATE,INTERNET

##############################################

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (int) Target Android API
android.api = 33

# (int) Minimum API your APK / AAB will support
android.minapi = 21

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (bool) Copy library instead of making a libpymodules.so
android.copy_libs = 1

# (bool) Enable Android auto backup feature (Android API >=23)
android.allow_backup = True

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

# (str) The format used to package the app for debug mode (apk or aar).
android.debug_artifact = apk

# (str) The format used to package the app for release mode (aab or apk or aar).
android.release_artifact = aab





#############################################################################################





# Python for android (p4a) specific
##############################################

# (str) python-for-android fork to use
p4a.fork = kivy

# (str) python-for-android branch to use
p4a.branch = master

# (str) extra command line arguments to pass when invoking pythonforandroid.toolchain
# p4a.extra_args = --debug





[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 1
