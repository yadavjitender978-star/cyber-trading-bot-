[app]
title = Cyber Trading Bot
package.name = cybertradingbot
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy==2.1.0,kivymd==1.1.1,ccxt==4.2.28,websocket-client==1.6.2,urllib3==1.26.18
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,ACCESS_NETWORK_STATE
android.api = 34
android.minapi = 21
android.ndk = 25b
android.arch = arm64-v8a
android.private_storage = True

[buildozer]
log_level = 2
warn_on_root =1