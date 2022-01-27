'''
Created on May 06, 2022

@author: vladyslav_goncharuk
'''

import time

from paf.paf_impl import logger, CommunicationMode, Task

class CTSDeploymentTask(Task):

    def __init__(self):
        super().__init__()

        self.CTS_DOWNLOAD_PATH = "${ROOT}/${ANDROID_DEPLOYMENT_DIR}/${DOWNLOAD_DIR}/${ANDROID_REPO_BRANCH}/${CTS_SUBDIR}"
        self.CTS_DEPLOY_PATH = "${ROOT}/${ANDROID_DEPLOYMENT_DIR}/${DEPLOY_DIR}/${ANDROID_REPO_BRANCH}/${CTS_SUBDIR}"

class cts_deploy(CTSDeploymentTask):
    def __init__(self):
        super().__init__()
        self.set_name(cts_deploy.__name__)

    def execute(self):
        self.subprocess_must_succeed("sudo -S apt-get -y install adb aapt")

        self.subprocess_must_succeed(
            f"mkdir -p {self.CTS_DOWNLOAD_PATH} && cd {self.CTS_DOWNLOAD_PATH}; " +
            f"if test -e \"./{self.CTS_ARCHIVE_NAME}\"; then zflag='--time-cond ./{self.CTS_ARCHIVE_NAME}'; else zflag=''; fi; "
            f" curl \"{self.CTS_DOWNLOAD_LINK}\" $${{zflag}} -C - --output ./{self.CTS_ARCHIVE_NAME}_copy; "
            f"if [ -f ./{self.CTS_ARCHIVE_NAME}_copy ]; then mv ./{self.CTS_ARCHIVE_NAME}_copy ./{self.CTS_ARCHIVE_NAME}; fi")

        self.subprocess_must_succeed( self._wrap_command_with_file_marker_condition(f"{self.CTS_DOWNLOAD_PATH + '/CTS_ARCHIVE_VERSION'}",
            f"rm -rf {self.CTS_DEPLOY_PATH} && mkdir -p {self.CTS_DEPLOY_PATH} " + f"&& cd {self.CTS_DEPLOY_PATH} && " + f"unzip {self.CTS_DOWNLOAD_PATH}/{self.CTS_ARCHIVE_NAME}", self.ANDROID_REPO_BRANCH))

class cts_execute(CTSDeploymentTask):
    def __init__(self):
        super().__init__()
        self.set_name(cts_execute.__name__)

    def execute(self):

        # We should wait for suitable device
        attempt = 0
        max_attempt = 100
        sleep_timeout = 3

        attempt_successful = False

        while attempt < max_attempt:

            logger.info("Polling available devicesAttempt " + str(attempt))

            result = self.subprocess_must_succeed(f"{self.CTS_DEPLOY_PATH}/android-cts/tools/cts-tradefed list devices",
                        communication_mode = CommunicationMode.PIPE_OUTPUT)

            if "emulator" in result:
                # Now we can run tests
                self.subprocess_must_succeed(f"{self.CTS_DEPLOY_PATH}/android-cts/tools/cts-tradefed run cts -m CtsCarTestCases",
                    communication_mode = CommunicationMode.PIPE_OUTPUT)
                attempt_successful = True
                break
            else:
                logger.info("Attempt " + str(attempt) + f" has failed. Will try again in {str(sleep_timeout)} seconds.")
                attempt = attempt + 1
                time.sleep(sleep_timeout)

        self.assertion(attempt_successful, "Expected 'attempt_successful' equal to 'True'")
