'''
Created on Jan 10, 2022

@author: vladyslav_goncharuk
'''

from paf.paf_impl import SSHLocalClient

class prepare_directories(SSHLocalClient):

    def __init__(self):
        super().__init__()
        self.set_name(prepare_directories.__name__)

    def execute(self):
        if self.get_environment_param("CLEAR") == "True":
            self.subprocess_must_succeed("rm -rf ${ROOT}/${ANDROID_DEPLOYMENT_DIR}")

        self.subprocess_must_succeed("mkdir -p ${ROOT}")
        self.subprocess_must_succeed("mkdir -p ${ROOT}/${ANDROID_DEPLOYMENT_DIR}")
        self.subprocess_must_succeed("mkdir -p ${ROOT}/${ANDROID_DEPLOYMENT_DIR}/${DOWNLOAD_DIR}")
        self.subprocess_must_succeed("mkdir -p ${ROOT}/${ANDROID_DEPLOYMENT_DIR}/${SOURCE_DIR}")
        self.subprocess_must_succeed("mkdir -p ${ROOT}/${ANDROID_DEPLOYMENT_DIR}/${BUILD_DIR}")
        self.subprocess_must_succeed("mkdir -p ${ROOT}/${ANDROID_DEPLOYMENT_DIR}/${DEPLOY_DIR}")

        if self.has_non_empty_environment_param("ANDROID_CUTTLEFISH_EXEC_DIR"):
            self.subprocess_must_succeed("mkdir -p ${ANDROID_CUTTLEFISH_EXEC_DIR}")

        self.subprocess_must_succeed("mkdir -p ${ROOT}")

class install_dependencies(SSHLocalClient):

    def __init__(self):
        super().__init__()
        self.set_name(install_dependencies.__name__)

    def execute(self):

        # AOSP build dependencies
        self.subprocess_must_succeed("sudo -S apt-get -y install git-core gnupg flex bison build-essential zip "
                                     "curl zlib1g-dev gcc-multilib g++-multilib libc6-dev-i386 libncurses5 "
                                     "lib32ncurses5-dev x11proto-core-dev libx11-dev lib32z1-dev libgl1-mesa-dev "
                                     "libxml2-utils xsltproc unzip fontconfig")

        # cuttlefish build dependencies
        self.subprocess_must_succeed("sudo -S apt install -y git devscripts config-package-dev debhelper-compat golang")
