'''
Created on Dec 29, 2021

@author: vladyslav_goncharuk
'''

from linux_deployment import general
from paf.paf_impl import CommunicationMode

class UbootDeploymentTask(general.LinuxDeploymentTask):

    def __init__(self):
        super().__init__()
        self.DOWNLOAD_PATH = "${ROOT}/${LINUX_DEPLOYMENT_DIR}/${DOWNLOAD_DIR}/${ARCH_TYPE}/${UBOOT_FOLDER_NAME}"
        self.SOURCE_PATH = "${ROOT}/${LINUX_DEPLOYMENT_DIR}/${SOURCE_DIR}/${ARCH_TYPE}/${UBOOT_FOLDER_NAME}"
        self.BUILD_PATH = "${ROOT}/${LINUX_DEPLOYMENT_DIR}/${BUILD_DIR}/${ARCH_TYPE}/${UBOOT_FOLDER_NAME}"
        self.DEPLOY_PATH = "${ROOT}/${LINUX_DEPLOYMENT_DIR}/${DEPLOY_DIR}/${ARCH_TYPE}/${UBOOT_FOLDER_NAME}"

    def _get_uboot_config_target(self):
        target = ""

        arch_type = self._get_arch_type()

        if(arch_type == "ARM"):
            target = "${UBOOT_CONFIG_TARGET_ARM}"
        elif(arch_type == "ARM64"):
            target = "${UBOOT_CONFIG_TARGET_ARM64}"
        else:
            raise Exception(f"Can't determine config target for architecture '${arch_type}'")

        return target

class uboot_sync(UbootDeploymentTask):

    def __init__(self):
        super().__init__()
        self.set_name(uboot_sync.__name__)

    def execute(self):

        self.subprocess_must_succeed(f"mkdir -p {self.DOWNLOAD_PATH}")
        self.subprocess_must_succeed(f"mkdir -p {self.SOURCE_PATH}")
        self.subprocess_must_succeed(f"mkdir -p {self.BUILD_PATH}")
        self.subprocess_must_succeed(f"mkdir -p {self.DEPLOY_PATH}")

        self.subprocess_must_succeed("(cd ${ROOT}/${LINUX_DEPLOYMENT_DIR}/${SOURCE_DIR}/${ARCH_TYPE} && " +
            "git clone ${UBOOT_GIT_REFERENCE}) || (cd " + f"{self.SOURCE_PATH} && git pull)")

class uboot_clean(UbootDeploymentTask):

    def __init__(self):
        super().__init__()
        self.set_name(uboot_clean.__name__)

    def execute(self):
        self.subprocess_must_succeed(f"cd {self.SOURCE_PATH}; make O={self.BUILD_PATH} -C {self.SOURCE_PATH} distclean",
                                     communication_mode = CommunicationMode.PIPE_OUTPUT)


class uboot_configure(UbootDeploymentTask):

    def __init__(self):
        super().__init__()
        self.set_name(uboot_configure.__name__)

    def execute(self):

        used_compiler = self._get_compiler()
        target = self._get_uboot_config_target()

        self.subprocess_must_succeed(f"cd {self.SOURCE_PATH}; make O={self.BUILD_PATH} -C {self.SOURCE_PATH} V=1 "
                                      "CROSS_COMPILE=" + used_compiler + "- " + target,
                                     communication_mode = CommunicationMode.PIPE_OUTPUT)

        self.subprocess_must_succeed(f"cd {self.SOURCE_PATH}; make O={self.BUILD_PATH} -C {self.SOURCE_PATH} V=1 "
                                      "CROSS_COMPILE=" + used_compiler + "- -j${BUILD_SYSTEM_CORES_NUMBER} menuconfig",
                                     communication_mode = CommunicationMode.PIPE_OUTPUT)

class uboot_build(UbootDeploymentTask):
    def __init__(self):
        super().__init__()
        self.set_name(uboot_build.__name__)

    def execute(self):

        used_compiler = self._get_compiler()

        self.subprocess_must_succeed(f"cd {self.SOURCE_PATH}; make O={self.BUILD_PATH} -C {self.SOURCE_PATH} V=1 "
                                      "CROSS_COMPILE=" + used_compiler + "- -j${BUILD_SYSTEM_CORES_NUMBER} all",
                                     communication_mode = CommunicationMode.PIPE_OUTPUT)

class uboot_deploy(UbootDeploymentTask):
    def __init__(self):
        super().__init__()
        self.set_name(uboot_deploy.__name__)

    def execute(self):
        self.subprocess_must_succeed(f"rm -rf {self.DEPLOY_PATH}; mkdir -p {self.DEPLOY_PATH};")

        self.subprocess_must_succeed(f"cp {self.BUILD_PATH}/u-boot {self.DEPLOY_PATH}/")
        self.subprocess_must_succeed(f"cp {self.BUILD_PATH}/u-boot.bin {self.DEPLOY_PATH}/")

class uboot_run_on_qemu(UbootDeploymentTask):
    def __init__(self):
        super().__init__()
        self.set_name(uboot_run_on_qemu.__name__)

    def execute( self ):

        arch_type = self._get_arch_type()

        if arch_type == "ARM":
            self.subprocess_must_succeed(f"cd {self.DEPLOY_PATH} && " +
            "qemu-system-arm -machine ${ARM_MACHINE_TYPE} -nographic -smp 1 "
            "-m 512M -kernel ./u-boot")
        elif arch_type == "ARM64":
            self.subprocess_must_succeed(f"cd {self.DEPLOY_PATH} && " +
            "qemu-system-aarch64 -machine ${ARM64_MACHINE_TYPE} -cpu cortex-a53 -machine type=\"${ARM64_MACHINE_TYPE}\" -nographic -smp 1 "
            "-m 512M -kernel ./u-boot")
        else:
            raise Exception( f"Unsupported architecture {arch_type}" )
