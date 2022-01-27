'''
Created on Jan 21, 2022

@author: vladyslav_goncharuk
'''

from paf.paf_impl import Task, CommunicationMode
from asyncio.log import logger

class CuttlefishDeploymentTask(Task):

    def __init__(self):
        super().__init__()

        self.CUTTLEFISH_PATH = "${ROOT}/${ANDROID_DEPLOYMENT_DIR}/${SOURCE_DIR}/${CUTTLEFISH_SUB_DIR}"

class cuttlefish_install_docker(CuttlefishDeploymentTask):

    def __init__(self):
        super().__init__()
        self.set_name(cuttlefish_install_docker.__name__)

    def execute(self):
        self.subprocess_must_succeed("sudo -S apt-get update; "
            "sudo -S apt-get install -y ca-certificates curl gnupg lsb-release; ")

        self.subprocess_must_succeed("if [ ! -f /usr/share/keyrings/docker-archive-keyring.gpg ]; then curl -fsSL ${DOCKER_GPG_KEY_URL} "
            "| sudo -S gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg; fi")

        target_string = "deb [arch=$$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] "\
            "https://download.docker.com/linux/ubuntu $$(lsb_release -cs) stable"

        self.subprocess_must_succeed(f'( sudo -S grep -qxF \'{target_string}\' /etc/apt/sources.list.d/docker.list ) || ( echo "{target_string}" | '
            'sudo -S tee /etc/apt/sources.list.d/docker.list > /dev/null )')

        self.subprocess_must_succeed("sudo -S apt-get update; "
             "sudo -S apt-get install -y docker-ce docker-ce-cli containerd.io; "
             "sudo -S groupadd docker; "
             "sudo -S usermod -aG docker $$USER;")

class cuttlefish_sync(CuttlefishDeploymentTask):

    def __init__(self):
        super().__init__()
        self.set_name(cuttlefish_sync.__name__)


    def execute(self):

        self.subprocess_must_succeed(f"mkdir -p {self.CUTTLEFISH_PATH}")

        self.subprocess_must_succeed("( cd ${ROOT}/${ANDROID_DEPLOYMENT_DIR}/${SOURCE_DIR} && "
            "git clone ${CUTTLEFISH_GIT_URL}) || "
            f"(cd {self.CUTTLEFISH_PATH} && git pull)")

class cuttlefish_build(CuttlefishDeploymentTask):

    def __init__(self):
        super().__init__()
        self.set_name(cuttlefish_build.__name__)

    def execute(self):

        self.subprocess_must_succeed(f"cd {self.CUTTLEFISH_PATH}; "
                                     "source setup.sh; "
                                     "export ANDROID_PRODUCT_OUT=${ANDROID_PRODUCT_OUT}; "
                                     "export ANDROID_HOST_OUT=${ANDROID_HOST_OUT}; "
                                     "cvd_docker_rm_all; ")

        self.subprocess_must_succeed(f"cd {self.CUTTLEFISH_PATH}; debuild -i -us -uc -b")

        self.subprocess_must_succeed(f"cd {self.CUTTLEFISH_PATH}; mv ../cuttlefish-* {self.CUTTLEFISH_PATH}/out")

        self.subprocess_must_succeed(f"cd {self.CUTTLEFISH_PATH}; ./build.sh")

class cuttlefish_start(CuttlefishDeploymentTask):

    def __init__(self):
        super().__init__()
        self.set_name(cuttlefish_start.__name__)

    def execute(self):

        logger.info("In case of failure of this step check the content of the ANDROID_PRODUCT_OUT & ANDROID_HOST_OUT parameters.")
        logger.info("How to fill them in?")
        logger.info("Go to https://ci.android.com/.")
        logger.info("Select any specific aosp_cf_x86_64_phone artifacts build and download the following artifacts:")
        logger.info("- aosp_cf_x86_64_phone-img-xxxxxxx.zip")
        logger.info("- cvd-host_package.tar.gz ")
        logger.info("Place cvd-host_package.tar.gz to any folder and specify it as the ANDROID_HOST_OUT, without unpacking the archive.")
        logger.info("Place aosp_cf_x86_64_phone-img-xxxxxxx.zip to any folder, unpack it, and specify as ANDROID_PRODUCT_OUT")
        logger.info("Unfortunately it is quite hard to automate this download. So, currently it is a TODO task!")
        logger.info("As an alternative, you can specify the folders of the manually built AOSP:")
        logger.info("ANDROID_PRODUCT_OUT=/android_source_root_folder/out/target/product/vsoc_x86")
        logger.info("ANDROID_HOST_OUT=/android_source_root_folder/out/host/linux-x86")

        self.subprocess_must_succeed(f"cd {self.CUTTLEFISH_PATH}; "
                                     "source setup.sh; "
                                     "export ANDROID_PRODUCT_OUT=${ANDROID_PRODUCT_OUT}; "
                                     "export ANDROID_HOST_OUT=${ANDROID_HOST_OUT}; "
                                     "cvd_docker_rm_all; ")

        self.subprocess_must_succeed(f"cd {self.CUTTLEFISH_PATH}; "
                                     "source setup.sh; "
                                     "export ANDROID_PRODUCT_OUT=${ANDROID_PRODUCT_OUT}; "
                                     "export ANDROID_HOST_OUT=${ANDROID_HOST_OUT}; "
                                     "cvd_docker_create -A -C ${CUTTLEFISH_DOCKER_CONTAINER_NAME}; ")

        self.subprocess_must_succeed(f"cd {self.CUTTLEFISH_PATH}; "
                                     "source setup.sh; "
                                     "export ANDROID_PRODUCT_OUT=${ANDROID_PRODUCT_OUT}; "
                                     "export ANDROID_HOST_OUT=${ANDROID_HOST_OUT}; "
                                     "cvd_start_${CUTTLEFISH_DOCKER_CONTAINER_NAME} ${CUTTLEFISH_PARAMS}")

class cuttlefish_stop(CuttlefishDeploymentTask):

    def __init__(self):
        super().__init__()
        self.set_name(cuttlefish_stop.__name__)

    def execute(self):

        self.subprocess_must_succeed(f"cd {self.CUTTLEFISH_PATH}; "
                             "source setup.sh; "
                             "export ANDROID_PRODUCT_OUT=${ANDROID_PRODUCT_OUT}; "
                             "export ANDROID_HOST_OUT=${ANDROID_HOST_OUT}; "
                             "cvd_stop_${CUTTLEFISH_DOCKER_CONTAINER_NAME}")

