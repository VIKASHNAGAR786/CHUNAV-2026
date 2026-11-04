[app]

# (str) Title of your application
title = JAINAGAR CHUNAV

# (str) Package name
package.name = jainagarchunav

# (str) Package domain (needed for android/ios packaging)
package.domain = org.jainagar

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,ttf,db,json

# (list) List of inclusions using pattern matching
source.include_patterns = assets/*,assets/fonts/*,assets/candidate/*

# (str) Application versioning (method 1)
version = 1.0.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy==2.3.1,pillow,sqlite3

# (str) Presplash of the application
presplash.filename = %(source.dir)s/assets/candidate/candidate_banner.png

# (str) Icon of the application
icon.filename = %(source.dir)s/assets/candidate/app_icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET,ACCESS_NETWORK_STATE,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (int) Android SDK version to use
android.sdk = 33

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (list) List of Java .jar files to add to the libs so that pyjnius can access
# their classes. Don't add jars that you do not need, since extra jars can slow
# down the build process.
#android.add_jars = foo.jar,bar.jar,path/to/more/*.jar

# (list) Android AAR archives to add
#android.add_aars =

# (list) Gradle dependencies
#android.gradle_dependencies =

# (bool) Enable AndroidX support. Enable when you use AndroidX libraries or
# when a library you use requires it.
android.enable_androidx = True

# (bool) If True, then skip trying to update the Android sdk
android.skip_update = False

# (bool) If True, then automatically accept SDK license agreements.
android.accept_sdk_license = True

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
# For modern phones arm64-v8a is the standard
android.archs = arm64-v8a, armeabi-v7a

# (bool) allows Android to issue a warning if the architecture doesn't match the phone
android.allow_backup = True

# (str) The format used to package the app for release mode (aab or apk or aar).
android.release_artifact = apk

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
