
# AASIG Development Platform

----

## Table of content

- [About this repository](#about-this-repository)
- [Language](#language)
- [PAF](#paf)
- [Quick start](#quick-start)
- [Configuration](#configuration)
  - [Building AOSP parameters](#building-aosp-parameters)
  - [Cuttlefish emulator parameters](#cuttlefish-emulator-parameters)
  - [Build system parameters](#buld-system-parameters)
  - [Goldfish emulator parameters](#goldfish-emulator-parameters)
  - [Docker installation parameters](#docker-installation-parameters)
- [Supported scenarios](#supported-scenarios)
- [Useful tasks](#useful-tasks)
- [FAQ](#faq)

----

## About this repository

This repository contains an automation project, which allows to easily build the AOSP, configuring a set of the most frequently used parameters. Moreover, it supports automated preparation of execution of the AOSP on the goldfish and cuttlefish emulators.

The intention is to maintain this project and build more specific automation scenarios on top of it. Further extensions would support nuances of building AOSP for specific boards, which maintainers would be interested in.

## Language

As of now, we are using Python for the development of scenarios. Still, it is used in a specific way, meaning that the python code is firing a set of the bash one-liners. So, anyone who likes long bash commands also won't be disappointed :)

## PAF

AASIG dev platform is implemented, using the PAF framework. That is an open-source Github project. It originates from [this location](https://github.com/svlad-90/paf).

Still, it is so tiny, that it was fully copied to this repo, under the [paf](./paf) folder. The full copy was made, as the original project might evolve in a separate way. In the future that might cause incompatibility between the implemented automation scenarios of the AASIG project and the API of the framework. Thus, we've decided to stick to a certain version, and do manual updates of the framework, if ever needed.

To get the idea regarding the paf framework, please, visit [this page](./paf/README.md)

## Quick start

To get started, one should do the following things:
- Clone this repo
- Open terminal in the root folder
- Execute the following command:
  ```bash
  python ./paf/paf_main.py -imd ./build -c ./build/scenarios_covesa.xml -s build_android -ld="./"
  ```

The above major scenario will guide you through:
- downloading the repo tool
- injecting the specified local_manifest
- init and sync of the repo from the specified branch
- build of the AOSP

## Configuration

In order to get familiar with all supported parameters, and all declared scenarios, phases, and tasks you could check the [scenarios_covesa.xml](./build/scenarios_covesa.xml) file.

Still, as we love proper documentation, here is the full list of supported parameters with comments.

### Building AOSP parameters

|Parameter|Comment|
|---|---|
|ROOT|Root folder of the project. All the other things will be placed inside this folder. Note! Try to place the root folder near the "/" root. There were cases when the too deeply nested ROOT folder caused build failure due to the too-long argument lists, fired by the ninja tool.|
|ANDROID_DEPLOYMENT_DIR|This project's dir. Will be located inside ROOT.|
|DOWNLOAD_DIR|The directory, which is used to download the binary artifacts. E.g. repo tool. Located inside the ROOT/ANDROID_DEPLOYMENT_DIR.|
|SOURCE_DIR|The directory, which is used to clone git repositories in it. E.g. AOSP sources or cuttlefish git repo. Located inside the ROOT/ANDROID_DEPLOYMENT_DIR.|
|BUILD_DIR|The directory, which we try to use for the build. E.g. AOSP build process would be ongoing inside that folder's sub-folder. Located inside the ROOT/ANDROID_DEPLOYMENT_DIR.|
|DEPLOY_DIR|Placeholder. Currently not being used. Located inside the ROOT/ANDROID_DEPLOYMENT_DIR.|
|REPO_TOOL_SUB_DIR|Sub-directory, in which repo tool will be downloaded. Located inside the ROOT/ANDROID_DEPLOYMENT_DIR/DOWNLOAD_DIR.|
|ANDROID_REPO_URL|Link to a git repository that contains Android platform manifest.|
|ANDROID_REPO_BRANCH|Branch, which we will sync.|
|ANDROID_LUNCH_CONFIG|Lunch configuration, which will be used during the build and during the execution of the goldfish emulator.|
|ANDROID_MANIFEST|Link to the Android manifest.|
|ANDROID_LOCAL_MANIFESTS_GIT_URL|Link to the git repository, which contains the local manifest, which we want to inject into the build.|
|LOCAL_VENDOR_SOURCE_PATH|If you work with some local project, you can inject it into the AOSP build without the usage of the ANDROID_LOCAL_MANIFESTS_GIT_URL parameter. To do this, you will need to remove the usage of the ANDROID_LOCAL_MANIFESTS_GIT_URL. Then you'll need to specify the LOCAL_VENDOR_DESTINATION_PATH and the LOCAL_VENDOR_SOURCE_PATH parameters. The LOCAL_VENDOR_SOURCE_PATH should contain the path to your local vendor folder, which contains some buildable artifacts. Can be used to locally inject the folder into the AOSP build.|
|LOCAL_VENDOR_DESTINATION_PATH|The path inside the AOSP source folder, where you would like to locate your artifacts. It will be used to copy the content of the LOCAL_VENDOR_SOURCE_PATH folder inside the ANDROID_SOOURCE_ROOT / LOCAL_VENDOR_DESTINATION_PATH before the build. Be aware that if this option is used, it will cause removal and copy of the directory on each build iteration.|
|PATCH_AFTER_REPO_SYNC_HOOK|Can contain bash-like CLI command, which will be executed during the build, **AFTER THE "repo sync" COMMAND**. It can be used to patch some of the AOSP files.|
|IS_SDK_BUILD|Whether build includes the 'sdk' target. If it is equal to "True" - PATCH_AFTER_REPO_SYNC_HOOK_SDK hook will be executed.|
|PATCH_AFTER_REPO_SYNC_HOOK_SDK|Can contain bash-like CLI command, which will be executed during the build, **AFTER THE "repo sync" COMMAND in case if IS_SDK_BUILD is equal to "True"**. It can be used to patch some of the AOSP files.|
|MAKE_TARGET|Specifies target to be built|

### Cuttlefish emulator parameters

|Parameter|Comment|
|---|---|
|CUTTLEFISH_SUB_DIR|Sub-directory, into which the cuttlefish project would be synced. Located inside ROOT/ANDROID_DEPLOYMENT_DIR\SOURCE_DIR.|
|CUTTLEFISH_GIT_URL|Link to the cuttlefish git repository.|
|ANDROID_PRODUCT_OUT|Path to the Anroid product output directory.|
|ANDROID_HOST_OUT|Path to the Android host output directory.|
|CUTTLEFISH_DOCKER_CONTAINER_NAME|Name of the cuttlefish docker container, which will be created.|
|CUTTLEFISH_PARAMS|The string with parameters, which would be directly passed to the cuttlefish emulator.|
|INSTALL_DOCKER|Whether to install docker or not. Condition is considered during the execution of the "run_android_cuttlefish" scenario and "install_docker" phase.|

### Build system parameters

|Parameter|Comment|
|---|---|
|BUILD_SYSTEM_CORES_NUMBER|Number of the simultaneous tasks, which you want to run in parallel during repo init, repo sync, make, etc.|
|DPKG_SPECIFIC_AUTOMATION|Whether to run DPKG-specific parts of the automation process. Mainly related to the usage of the "apt" tool.|
|REPO_INIT_DEPTH|Specifies the "--depth" parameter during the "repo init" call. Creates a shallow clone with given depth. See "git clone" for more details.|
|REPO_SYNC_THREADS_NUMBER|Specifies the "-j" parameter during the "repo sync" call. Number of jobs to run in parallel.|
|REPO_TRACE|Specifies the "--trace" option during the "repo" calls. Trace git command execution (REPO_TRACE=1).|
|REPO_SYNC_CURRENT_BRANCH|Specifies the "--current-branch" parameter during the "repo sync" call. fSpecifies whether to fetch only current branch from the server.|
|REPO_SYNC_FORCE|Specifies the "--force-sync" parameter during the "repo sync" call. Overwrites an existing git directory if it needs to point to a different object directory. **WARNING: this may cause loss of data.**|

### Goldfish emulator parameters

|Parameter|Comment|
|---|---|
|WIPE_DATA|Whether to run the emulator from scratch or to continue from the previous suspension point.|

### Docker installation parameters

|Parameter|Comment|
|---|---|
|DOCKER_GPG_KEY_URL|Parameter is used to add docker's stable repository|

### CTS-specific parameters

|Parameter|Comment|
|---|---|
|CTS_ARCHIVE_NAME|Name of the archive with extension from the CTS_DOWNLOAD_LINK. E.g. android-cts-12.1_r1-linux_x86-x86.zip|
|CTS_DOWNLOAD_LINK|URL, from which we should download the CTS build. E.g. https://dl.google.com/dl/android/cts/android-cts-12.1_r1-linux_x86-x86.zip|
|CTS_SUBDIR|The sub-directory name, into which will be placed downloaded and unpacked CTS artifacts.|

## Supported scenarios

|Scenario|Comment|
|---|---|
|build_android|Syncs and builds the AOSP project.|
|run_android_goldfish|Runs the Android goldfish emulator. Should be executed AFTER the "build_android" scenario. In order to finish the scenario one would need to close the emulator using the "X" button.|
|run_android_cuttlefish|Syncs and builds cuttlefish emulator within the Docker container. Then starts the cuttlefish emulator, using the specified parameters. Make sure, that you are using the compatible "_cf_" image, before running this scenario.| 

## Useful tasks

It makes sense to run the task "aasig_dev_platform.build_android.android_build" separately, in case if you want to skip re-sync of the repo. The execution command would look like this:

```bash
python ./paf/paf_main.py -imd ./build -c ./build/scenarios_covesa.xml -t aasig_dev_platform.build_android.android_build -ld="./"
```

Also there is a helper task to install Docker into your system:

```bash
python ./paf/paf_main.py -imd ./build -c ./build/scenarios_covesa.xml -t aasig_dev_platform.cuttlefish.cuttlefish_install_docker -ld="./"
```

**Note!** As of now, the installation of the Docker is Ubuntu-specific. It uses apt tool inside.

## FAQ

**Q: How to fill in ANDROID_PRODUCT_OUT parameter?**

**A:** You need to do the following things:

- Go to https://ci.android.com/.
- Select any specific aosp_cf_x86_64_phone artifacts build and download the following artifact:
  aosp_cf_x86_64_phone-img-xxxxxxx.zip 
- Place aosp_cf_x86_64_phone-img-xxxxxxx.zip to any folder, unpack it, and specify it as the ANDROID_PRODUCT_OUT

Unfortunately, it is quite hard to automate this download. So, currently, it is a TODO task.

As an alternative, you can specify the folder of the manually built AOSP:
```
ANDROID_PRODUCT_OUT=/android_source_root_folder/out/target/product/vsoc_x86
```

**Q: How to fill in ANDROID_HOST_OUT parameter?**

**A:** You need to do the following things:

- Go to https://ci.android.com/.
- Select any specific aosp_cf_x86_64_phone artifacts build and download the following artifact:
  cvd-host_package.tar.gz 
- Place cvd-host_package.tar.gz to any folder and specify it as the ANDROID_HOST_OUT, without unpacking the archive.

Unfortunately, it is quite hard to automate this download. So, currently, it is a TODO task.

As an alternative, you can specify the folders of the manually built AOSP:
```
ANDROID_HOST_OUT=/android_source_root_folder/out/host/linux-x86
```

**Q: Why some of the automation scenarios do contain usage of "apt" tool? Does this repository cover only DPKG-based Linux distributions?**

**A:** As of now, there are several such tasks exist:

|Task name|Task purpose|
|---|---|
|aasig_dev_platform.cuttlefish.cuttlefish_install_docker|Installation of Docker|
|aasig_dev_platform.general.install_dependencies|Installation of the AOSP build prerequisite packages|

Due to that it is worth explaining the rule of thumb.

In general, it should be the responsibility of the host system to have all dependencies available. So, by good means, all dependencies of all main automation scenarios should be listed in a separate section, which would make it clear how to prepare your system in each separate case. We will try to move in that direction.

Still, no one prohibits creating additional automation tasks, which are **NOT** part of main scenarios, or which are **EXCLUDED** from the main scenarios via condition. Those scenarios can help with the preparation of prerequisites. As long as such tasks are not by default executed as part of the main scenarios, they will do no harm. And, such tasks could be distribution-dependent. If one would want, he can add support of additional distribution to such a task.

To summarize. Yes, there are some DPKG-specific tasks in the repository. And no, it is not a critical thing to have it in as far as the above rules are considered.
