'''
Created on Jan 5, 2022

@author: vladyslav_goncharuk
'''

import os
import re

from linux_deployment import general
from paf.paf_impl import logger, CommunicationMode

class BusyboxDeploymentTask(general.LinuxDeploymentTask):

    def __init__(self):
        super().__init__()

        self.DOWNLOAD_PATH = "${ROOT}/${LINUX_DEPLOYMENT_DIR}/${DOWNLOAD_DIR}/${ARCH_TYPE}/${BUSYBOX_FOLDER_NAME}"
        self.SOURCE_PATH = "${ROOT}/${LINUX_DEPLOYMENT_DIR}/${SOURCE_DIR}/${ARCH_TYPE}/${BUSYBOX_FOLDER_NAME}"
        self.BUILD_PATH = "${ROOT}/${LINUX_DEPLOYMENT_DIR}/${BUILD_DIR}/${ARCH_TYPE}/${BUSYBOX_FOLDER_NAME}"
        self.DEPLOY_PATH = "${ROOT}/${LINUX_DEPLOYMENT_DIR}/${DEPLOY_DIR}/${ARCH_TYPE}/${BUSYBOX_FOLDER_NAME}"
        self.ROOTFS_PATH = "${ROOT}/${LINUX_DEPLOYMENT_DIR}/${DEPLOY_DIR}/${ARCH_TYPE}/${BUSYBOX_FOLDER_NAME}/initramfs"
        self.LINUX_KERNEL_IMAGE_PATH = "${ROOT}/${LINUX_DEPLOYMENT_DIR}/${DEPLOY_DIR}/${ARCH_TYPE}/${LINUX_KERNEL_FOLDER_NAME}"
        self.LINUX_KERNEL_DTB_LOCATION_ARM_PATH = "${ROOT}/${LINUX_DEPLOYMENT_DIR}/${DEPLOY_DIR}/${ARCH_TYPE}/${LINUX_KERNEL_FOLDER_NAME}/${LINUX_KERNEL_DTB_LOCATION_ARM}"

class busybox_sync(BusyboxDeploymentTask):

    def __init__(self):
        super().__init__()
        self.set_name(busybox_sync.__name__)

    def execute(self):

        self.subprocess_must_succeed(f"mkdir -p {self.DOWNLOAD_PATH}")
        self.subprocess_must_succeed(f"mkdir -p {self.SOURCE_PATH}")
        self.subprocess_must_succeed(f"mkdir -p {self.BUILD_PATH}")
        self.subprocess_must_succeed(f"mkdir -p {self.DEPLOY_PATH}")

        folder_name = "busybox-${BUSYBOX_VERSION}"
        archive_name = f"{folder_name}.tar.bz2"
        busybox_link = f"https://busybox.net/downloads/{archive_name}"
        self.subprocess_must_succeed(self._wrap_command_with_file_marker_condition(f"{self.DOWNLOAD_PATH + '/BUSYBOX_ARCHIVE_VERSION'}",
            f"wget -c -P {self.DOWNLOAD_PATH}" + f" {busybox_link}",
            "${BUSYBOX_VERSION}"))
        self.subprocess_must_succeed( self._wrap_command_with_file_marker_condition(f"{self.DOWNLOAD_PATH + '/BUSYBOX_EXTRACTED_ARCHIVE_VERSION'}",
            f"rm -rf {self.SOURCE_PATH} " + "&& cd ${ROOT}/${LINUX_DEPLOYMENT_DIR}/${SOURCE_DIR}/${ARCH_TYPE}/ && " + f"tar -xvf {self.DOWNLOAD_PATH}/" +
            f"{archive_name}" + " --checkpoint=100 && mv ${ROOT}/${LINUX_DEPLOYMENT_DIR}/${SOURCE_DIR}/${ARCH_TYPE}/" + f"{folder_name} {self.SOURCE_PATH}",
            "${BUSYBOX_VERSION}"))

class busybox_clean(BusyboxDeploymentTask):

    def __init__(self):
        super().__init__()
        self.set_name(busybox_clean.__name__)

    def execute(self):
        arch_type = self._get_arch_type()
        used_compiler = self._get_compiler()

        self.subprocess_must_succeed(f"cd {self.SOURCE_PATH}; make O={self.BUILD_PATH} -C {self.SOURCE_PATH} ARCH=" +
            arch_type.lower() + " CROSS_COMPILE=" + used_compiler + " distclean",
            communication_mode = CommunicationMode.PIPE_OUTPUT)

class busybox_configure(BusyboxDeploymentTask):

    def __init__(self):
        super().__init__()
        self.set_name(busybox_configure.__name__)

    def execute(self):
        arch_type = self._get_arch_type()
        used_compiler = self._get_compiler()

        self.subprocess_must_succeed(f"cd {self.SOURCE_PATH}; make O={self.BUILD_PATH} -C {self.SOURCE_PATH} ARCH=" + arch_type.lower() +
            " CROSS_COMPILE=" + used_compiler + "- ${BUSYBOX_CONFIG_TARGET}",
            communication_mode = CommunicationMode.PIPE_OUTPUT)

        config_flags_raw = self.get_environment().getVariableValue("BUSYBOX_CONFIG_FLAGS")

        config_dict = {}

        if config_flags_raw:

            logger.info(f"config_flags_raw - '{config_flags_raw}'")

            splited_config_flags = re.compile("[ ]*\|[ ]*").split(config_flags_raw)
            config_key_value_pair_regex = re.compile("[ ]*=[ ]*")

            for config_flag in splited_config_flags:

                logger.info(f"Config flag - '{config_flag}'")

                splited_config_key_value = config_key_value_pair_regex.split(config_flag)
                if len(splited_config_key_value) == 2:
                    config_dict[splited_config_key_value[0]] = splited_config_key_value[1]
                    logger.info(f"Parsed key - '{splited_config_key_value[0]}'; parsed value - '{splited_config_key_value[1]}'")

        for config_key in config_dict:
            self.subprocess_must_succeed(f"sed -i -E '/{config_key}(=| )/d' {self.BUILD_PATH}/.config; "
                                          f"echo \'{config_key}={config_dict[config_key]}\' >> " + f"{self.BUILD_PATH}/.config")

        config_adjustment_mode = self.get_environment_param("BUSYBOX_CONFIG_ADJUSTMENT_MODE")

        if  config_adjustment_mode == "PARAMETERS_ONLY":
            pass
        elif config_adjustment_mode == "USER_INTERACTIVE":
            self.subprocess_must_succeed(f"cd {self.SOURCE_PATH}; make O={self.BUILD_PATH} -C {self.SOURCE_PATH} "
            "ARCH=" + arch_type.lower() + " CROSS_COMPILE=" + used_compiler + "- " + 'menuconfig',
            communication_mode = CommunicationMode.PIPE_OUTPUT)

class busybox_build(BusyboxDeploymentTask):
    def __init__(self):
        super().__init__()
        self.set_name(busybox_build.__name__)

    def execute(self):

        arch_type = self._get_arch_type()
        used_compiler = self._get_compiler()

        self.subprocess_must_succeed(f"cd {self.SOURCE_PATH}; make O={self.BUILD_PATH} -C {self.SOURCE_PATH} ARCH=" + arch_type.lower() +
            " CROSS_COMPILE=" + used_compiler + "- -j${BUILD_SYSTEM_CORES_NUMBER} ${BUSYBOX_BUILD_TARGET}",
            communication_mode = CommunicationMode.PIPE_OUTPUT)

        self.subprocess_must_succeed(f"cd {self.SOURCE_PATH}; make O={self.BUILD_PATH} -C {self.SOURCE_PATH} ARCH=" + arch_type.lower() +
            " CROSS_COMPILE=" + used_compiler + "- " + "install",
            communication_mode = CommunicationMode.PIPE_OUTPUT)

class busybox_deploy(BusyboxDeploymentTask):
    def __init__(self):
        super().__init__()
        self.set_name(busybox_deploy.__name__)

    def execute(self):

        products_folder = "_install"

        self.subprocess_must_succeed(f"rm -rf {self.DEPLOY_PATH}; mkdir -p {self.DEPLOY_PATH};")

        self.subprocess_must_succeed(f"mkdir -p {self.ROOTFS_PATH}")

        directories_list: list = [
            os.path.join( f"{self.BUILD_PATH}", f"{products_folder}", "." )
        ]

        for directory in directories_list:
            self.subprocess_must_succeed(f"cp -r {directory} {self.ROOTFS_PATH}")

        self.subprocess_must_succeed(f"mkdir -p {self.ROOTFS_PATH}/lib && cp -r {self._get_compiler_path() + '/lib/.'} {self.ROOTFS_PATH}/lib")
        self.subprocess_must_succeed(f"mkdir -p {self.ROOTFS_PATH}/dev")

        self.subprocess_must_succeed(f"for i in {{0..4}}; do sudo -S mknod -m 666 {self.ROOTFS_PATH}/dev/tty$$i c 4 $$i; done; ")
        self.subprocess_must_succeed(f"sudo -S mknod -m 666 {self.ROOTFS_PATH}/dev/console c 5 1 && "
                                      f"sudo -S mknod -m 666 {self.ROOTFS_PATH}/dev/nulll c 1 3;")

        self.subprocess_must_succeed(f"cd {self.ROOTFS_PATH}; find . | cpio -H newc -ov --owner root:root > {self.DEPLOY_PATH}/initramfs.cpio")

        self.subprocess_must_succeed(f"gzip -k {self.DEPLOY_PATH}/initramfs.cpio")

class busybox_run_on_qemu(BusyboxDeploymentTask):
    def __init__(self):
        super().__init__()
        self.set_name(busybox_run_on_qemu.__name__)

    def execute(self):
        arch_type = self._get_arch_type()

        if arch_type == "ARM":
            self.subprocess_must_succeed("qemu-system-arm -machine ${ARM_MACHINE_TYPE} "
                "-nographic -smp 2 -m 1024M -dtb " + f"{self.LINUX_KERNEL_DTB_LOCATION_ARM_PATH} "
                "-kernel " + f"{self.LINUX_KERNEL_IMAGE_PATH}" + "/zImage "
                f"-initrd {self.DEPLOY_PATH}/initramfs.cpio "
                "-append \"root=/dev/ram rw rdinit=/bin/sh console=ttyAMA0\"")
        elif arch_type == "ARM64":
            self.subprocess_must_succeed("qemu-system-aarch64 -machine ${ARM64_MACHINE_TYPE} -cpu cortex-a57 -machine type=${ARM64_MACHINE_TYPE} "
                "-nographic -smp 2 -m 1024M "
                f"-kernel {self.LINUX_KERNEL_IMAGE_PATH}/Image "
                f"-initrd {self.DEPLOY_PATH}/initramfs.cpio "
                "-append \"root=/dev/ram rw rdinit=/bin/sh console=ttyAMA0\"")
        else:
            raise Exception(f"Unsupported architecture type '{arch_type}'")

