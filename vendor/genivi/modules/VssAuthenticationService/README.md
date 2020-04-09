# Copyright
Copyright (C) 2020, TietoEVRY

# License
This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Overview
## Build instructions
The intention is to maintain two build systems with a preference to support Android.bp.
Each module has its own Android.bp and gradle file.

### Gradle
From the directory of the desired module (_service_ for the service, _ExampleAppJava_ for the client):
```
./gradlew assembleDebug
```

### Android build system

Deploy the repository inside AOSP tree i.e. `/vendor/genivi/modules/vss` and call make from the top of the repo:
```
make vss-example-app vss-authentication-service
```
