'''
Created on Dec 29, 2021

@author: vladyslav_goncharuk
'''

import time

from paf.paf_impl import logger, CommunicationMode, Task, ExecutionMode

class AndroidDeploymentTask(Task):

    def __init__(self):
        super().__init__()

        self.REPO_TOOL_PATH = "${ROOT}/${ANDROID_DEPLOYMENT_DIR}/${DOWNLOAD_DIR}/${ANDROID_REPO_BRANCH}/${REPO_TOOL_SUB_DIR}"
        self.ANDROID_SOURCE_PATH = "${ROOT}/${ANDROID_DEPLOYMENT_DIR}/${SOURCE_DIR}/${ANDROID_REPO_BRANCH}"
        self.ANDROID_BUILD_DIR = "${ROOT}/${ANDROID_DEPLOYMENT_DIR}/${BUILD_DIR}/"
        self.ANDROID_BUILD_PATH = "${ROOT}/${ANDROID_DEPLOYMENT_DIR}/${BUILD_DIR}/${ANDROID_REPO_BRANCH}"
        self.REPO_SYNCED_TOOL_PATH = "${ROOT}/${ANDROID_DEPLOYMENT_DIR}/${SOURCE_DIR}/${ANDROID_REPO_BRANCH}/.repo/repo"
        self.VENDOR_PATH = "${ROOT}/${ANDROID_DEPLOYMENT_DIR}/${SOURCE_DIR}/${ANDROID_REPO_BRANCH}/${LOCAL_VENDOR_DESTINATION_PATH}"

class android_init(AndroidDeploymentTask):

    def __init__(self):
        super().__init__()
        self.set_name(android_init.__name__)

    def execute(self):

        logger.info("Get initial repo binary from Google")
        self.subprocess_must_succeed(
            f"mkdir -p {self.REPO_TOOL_PATH} && cd {self.REPO_TOOL_PATH}; " +
            f"if test -e \"./repo\"; then zflag='--time-cond ./repo'; else zflag=''; fi; "
            f" curl \"https://storage.googleapis.com/git-repo-downloads/repo\" $${{zflag}} -C - --output ./repo_copy; " +
            f"if [ -f ./repo_copy ]; then mv ./repo_copy ./repo; fi; chmod a+x {self.REPO_TOOL_PATH}/repo")

        logger.info("Check of the git user name/email configuration")

        self.subprocess_must_succeed('git config user.name; if [ $$? -ne 0 ]; then '
            'echo "A git user name should be configured for later build steps. '
            'You seem to be running outside of container, because the container should have it configured already. '
            'Therefore, please note that what you provide here will be stored in the global git settings (in your home directory!)"; '
            'read -p "Name: " name; git config --global user.name "$$name"; fi')

        logger.info("Init and sync repo")
        self.subprocess_must_succeed("git config user.email; if [ $$? -ne 0 ]; then "
            'echo "A git user email should be configured for later build steps. '
            'You seem to be running outside of container, because the container should have it configured already. '
            'Therefore, please note that what you provide here will be stored in the global git settings (in your home directory!)"; '
            'read -p "Email: " email; git config --global user.email "$$email"; fi')

        trace = ""
        if self.has_environment_true_param("REPO_TRACE"):
            trace = f" --trace"

        depth = ""
        if self.has_non_empty_environment_param("REPO_INIT_DEPTH"):
            depth = f" --depth={self.REPO_INIT_DEPTH}"

        self.subprocess_must_succeed(f"mkdir -p {self.ANDROID_SOURCE_PATH} && cd {self.ANDROID_SOURCE_PATH}; "
                                     f"{self.REPO_TOOL_PATH}/repo" + trace + " init" + depth +
                                     f"{' -u ' + '${ANDROID_REPO_URL}' if (hasattr(self, 'ANDROID_REPO_URL') and self.ANDROID_REPO_URL) else ''}" +
                                     f"{' -b ' + '${ANDROID_REPO_BRANCH}' if (hasattr(self, 'ANDROID_REPO_BRANCH') and self.ANDROID_REPO_BRANCH) else ''}" +
                                     f"{' -m ' + '${ANDROID_MANIFEST}' if (hasattr(self, 'ANDROID_MANIFEST') and self.ANDROID_MANIFEST) else ''}")

        if self.has_non_empty_environment_param("ANDROID_LOCAL_MANIFESTS_GIT_URL"):
            logger.info("ANDROID_LOCAL_MANIFESTS_GIT_URL is specified. Let's clone the local manifest")
            self.subprocess_must_succeed(f"cd {self.ANDROID_SOURCE_PATH} && rm -rf .repo/local_manifests && mkdir -p .repo/local_manifests && git clone" + " ${ANDROID_LOCAL_MANIFESTS_GIT_URL} .repo/local_manifests")

        sync_current_branch = ""
        if self.has_environment_true_param("REPO_SYNC_CURRENT_BRANCH"):
            sync_current_branch = f" -c"

        force_sync = ""
        if self.has_environment_true_param("REPO_SYNC_FORCE"):
            force_sync = f" --force-sync"

        self.subprocess_must_succeed(f"cd {self.ANDROID_SOURCE_PATH} && {self.REPO_SYNCED_TOOL_PATH}/repo" + trace + " sync"
                                     + force_sync + sync_current_branch + " -j${REPO_SYNC_THREADS_NUMBER}")

class android_after_repo_sync_hooks(AndroidDeploymentTask):
    def __init__(self):
        super().__init__()
        self.set_name(android_after_repo_sync_hooks.__name__)

    def execute(self):
        if self.has_non_empty_environment_param("PATCH_AFTER_REPO_SYNC_HOOK") and \
        self.has_non_empty_environment_param("PATCH_AFTER_REPO_SYNC_HOOK"):
            self.subprocess_must_succeed(self.PATCH_AFTER_REPO_SYNC_HOOK)

        if self.has_environment_true_param("IS_SDK_BUILD") and \
        self.has_non_empty_environment_param("PATCH_AFTER_REPO_SYNC_HOOK_SDK") and \
        self.has_non_empty_environment_param("PATCH_AFTER_REPO_SYNC_HOOK_SDK"):
            self.subprocess_must_succeed(self.PATCH_AFTER_REPO_SYNC_HOOK_SDK)

class android_build(AndroidDeploymentTask):
    def __init__(self):
        super().__init__()
        self.set_name(android_build.__name__)

    def execute(self):

        if self.has_non_empty_environment_param("LOCAL_VENDOR_DESTINATION_PATH") and \
        self.has_non_empty_environment_param("LOCAL_VENDOR_SOURCE_PATH"):
            self.subprocess_must_succeed(f"cd {self.ANDROID_SOURCE_PATH} && mkdir -p " + "${LOCAL_VENDOR_DESTINATION_PATH}; rm -rf ${LOCAL_VENDOR_DESTINATION_PATH}/* " + "&& cp -r ${LOCAL_VENDOR_SOURCE_PATH}/* " + f"{self.VENDOR_PATH}")

        make_target = ""

        if self.has_non_empty_environment_param("MAKE_TARGET"):
            make_target = self.MAKE_TARGET
            make_target = make_target.ljust(len(make_target) + 1)
            make_target = make_target.rjust(len(make_target) + 1)
        else:
            make_target = " "

        self.subprocess_must_succeed(f"cd {self.ANDROID_SOURCE_PATH} && . ./build/envsetup.sh; "
                                     f"export OUT_DIR_COMMON_BASE={self.ANDROID_BUILD_DIR}; "
                                     "lunch ${ANDROID_LUNCH_CONFIG} && make showcommands" + make_target + "-j${BUILD_SYSTEM_CORES_NUMBER}",
                                     communication_mode = CommunicationMode.PIPE_OUTPUT)

class android_run_emulator(AndroidDeploymentTask):
    def __init__(self):
        super().__init__()
        self.set_name(android_run_emulator.__name__)

    def execute(self):

        self.subprocess_must_succeed("adb kill-server", expected_return_codes = [0, 127])
        self.subprocess_must_succeed(f"sudo ln -sf {self.ANDROID_SOURCE_PATH}/prebuilts/runtime/adb /usr/bin/adb")
        self.subprocess_must_succeed("adb start-server")

        # First we need to terminate any already running qemu emulator, if such exists
        self.subprocess_must_succeed("PID_OF_EMULATOR=$$(pgrep -f \"export OUT_DIR_COMMON_BASE=\w.*emulator\"); if [ ! -z \"$$PID_OF_EMULATOR\" ]; then kill -9 $${PID_OF_EMULATOR}; fi")

        wipe_data_param = ""
        network = ""

        if self.has_environment_true_param("WIPE_DATA"):
            wipe_data_param = " -wipe-data"
        if self.has_environment_true_param("NET"):
            network = " -netdev bridge,id=n1,br=virbr0,helper=/usr/lib/qemu/qemu-bridge-helper -device virtio-net,netdev=n1,id=renesas"

        self.subprocess_must_succeed(f"export OUT_DIR_COMMON_BASE={self.ANDROID_BUILD_DIR}; cd {self.ANDROID_SOURCE_PATH} && . ./build/envsetup.sh && lunch "
                                     "${ANDROID_LUNCH_CONFIG}; " + f"emulator{wipe_data_param} -qemu{network}")

class android_run_emulator_non_blocking(AndroidDeploymentTask):
    def __init__(self):
        super().__init__()
        self.set_name(android_run_emulator_non_blocking.__name__)

    def execute(self):

        self.subprocess_must_succeed("adb kill-server", expected_return_codes = [0, 127])
        self.subprocess_must_succeed(f"sudo ln -sf {self.ANDROID_SOURCE_PATH}/prebuilts/runtime/adb /usr/bin/adb")
        self.subprocess_must_succeed("adb start-server")

        # First we need to terminate any already running qemu emulator, if such exists
        self.subprocess_must_succeed("PID_OF_EMULATOR=$$(pgrep -f \"export OUT_DIR_COMMON_BASE=\w.*emulator\"); if [ ! -z \"$$PID_OF_EMULATOR\" ]; then kill -9 $${PID_OF_EMULATOR}; fi")

        # Then let's start a new one, but in background mode
        wipe_data_param = ""
        network = ""

        if self.has_environment_true_param("WIPE_DATA"):
            wipe_data_param = " -wipe-data"
        if self.has_environment_true_param("NET"):
            network = " -netdev bridge,id=n1,br=virbr0,helper=/usr/lib/qemu/qemu-bridge-helper -device virtio-net,netdev=n1,id=renesas"

        self.subprocess_must_succeed(f"export OUT_DIR_COMMON_BASE={self.ANDROID_BUILD_DIR}; cd {self.ANDROID_SOURCE_PATH} && . ./build/envsetup.sh && lunch "
                                     "${ANDROID_LUNCH_CONFIG}; " + f"emulator{wipe_data_param} -qemu{network} &")

        # Now we need to poll the status of the emulator
        attempt = 0
        max_attempt = 300
        sleep_timeout = 3
        reboot_for_attempts = 30

        attempt_successful = False

        while attempt < max_attempt:

            logger.info("Polling emulator status. Attempt " + str(attempt))

            result = self.exec_subprocess("adb shell getprop sys.boot_completed", exec_mode = ExecutionMode.COLLECT_DATA)

            if result.exit_code == 0 and "1" in result.stdout:
                attempt_successful = True
                break
            else:
                logger.info("Attempt " + str(attempt) + f" has failed. Will try again in {str(sleep_timeout)} seconds.")
                attempt = attempt + 1

                if attempt % reboot_for_attempts == 0:
                    logger.info("Attempt " + str(attempt) + ". Retry limit reached. Restarting Android")
                    self.subprocess_must_succeed("adb shell reboot", expected_return_codes = [0, 1])

                time.sleep(sleep_timeout)

        self.assertion(attempt_successful, "Expected 'attempt_successful' equal to 'True'")
