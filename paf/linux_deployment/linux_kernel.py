'''
Created on Dec 30, 2021

@author: vladyslav_goncharuk
'''

import os
import re

from linux_deployment import general
from paf.paf_impl import logger, CommunicationMode

class LinuxKernelDeploymentTask(general.LinuxDeploymentTask):

    def __init__(self):
        super().__init__()

        self.DOWNLOAD_PATH = "${ROOT}/${LINUX_DEPLOYMENT_DIR}/${DOWNLOAD_DIR}/${ARCH_TYPE}/${LINUX_KERNEL_FOLDER_NAME}"
        self.SOURCE_PATH = "${ROOT}/${LINUX_DEPLOYMENT_DIR}/${SOURCE_DIR}/${ARCH_TYPE}/${LINUX_KERNEL_FOLDER_NAME}"
        self.BUILD_PATH = "${ROOT}/${LINUX_DEPLOYMENT_DIR}/${BUILD_DIR}/${ARCH_TYPE}/${LINUX_KERNEL_FOLDER_NAME}"
        self.DEPLOY_PATH = "${ROOT}/${LINUX_DEPLOYMENT_DIR}/${DEPLOY_DIR}/${ARCH_TYPE}/${LINUX_KERNEL_FOLDER_NAME}"

    def _get_linux_kernel_config_target(self):
        target = ""

        arch_type = self._get_arch_type()

        if(arch_type == "ARM"):
            target = "${LINUX_KERNEL_CONFIG_TARGET_ARM}"
        elif(arch_type == "ARM64"):
            target = "${LINUX_KERNEL_CONFIG_TARGET_ARM64}"
        else:
            raise Exception(f"Can't determine config target for architecture '${arch_type}'")

        return target

    def _get_linux_kernel_build_targets(self):
        return self.get_environment_param("LINUX_KERNEL_BUILD_TARGETS")

    def _get_linux_kernel_source(self):
        return self.get_environment_param("LINUX_KERNEL_SOURCE")

    def _get_linux_kernel_version(self):
        return self.get_environment_param("LINUX_KERNEL_VERSION")

class linux_kernel_sync(LinuxKernelDeploymentTask):

    def __init__(self):
        super().__init__()
        self.set_name(linux_kernel_sync.__name__)

    def execute(self):

        self.subprocess_must_succeed(f"mkdir -p {self.DOWNLOAD_PATH}")
        self.subprocess_must_succeed(f"mkdir -p {self.SOURCE_PATH}")
        self.subprocess_must_succeed(f"mkdir -p {self.BUILD_PATH}")
        self.subprocess_must_succeed(f"mkdir -p {self.DEPLOY_PATH}")

        linux_kernel_source = self._get_linux_kernel_source().lower()

        if linux_kernel_source == "git":
            self.subprocess_must_succeed(f"cd {self.SOURCE_PATH} && "
                f"( if [ ! -d .git ]; then rm -rf {self.SOURCE_PATH}; fi; )")
            self.subprocess_must_succeed("( cd ${ROOT}/${LINUX_DEPLOYMENT_DIR}/${SOURCE_DIR}/${ARCH_TYPE} && "
                "git clone -b v${LINUX_KERNEL_VERSION} ${LINUX_KERNEL_GIT_REFERENCE}) && git checkout tags/v${LINUX_KERNEL_VERSION} -b v${LINUX_KERNEL_VERSION} || :"
                f"(cd {self.SOURCE_PATH} && git pull)")
        elif linux_kernel_source == "cdn.kernel.org":
            linux_kernel_version = self._get_linux_kernel_version()
            folder_name = f"linux-{linux_kernel_version}"
            archive_name = f"{folder_name}.tar.xz"
            kernel_link = f"https://cdn.kernel.org/pub/linux/kernel/v{linux_kernel_version[0]}.x/{archive_name}"
            self.subprocess_must_succeed(self._wrap_command_with_file_marker_condition(f"{self.DOWNLOAD_PATH + '/LINUX_KERNEL_ARCHIVE_VERSION'}",
                f"wget -c -P {self.DOWNLOAD_PATH}" + f" {kernel_link}",
                self._get_linux_kernel_version())
            self.subprocess_must_succeed( self._wrap_command_with_file_marker_condition(f"{self.DOWNLOAD_PATH + '/LINUX_KERNEL_EXTRACTED_ARCHIVE_VERSION'}",
                f"rm -rf {self.SOURCE_PATH} " + "&& cd ${ROOT}/${LINUX_DEPLOYMENT_DIR}/${SOURCE_DIR}/${ARCH_TYPE}/ && " + f"tar -xvf {self.DOWNLOAD_PATH}/" +
                f"{archive_name}" + " --checkpoint=100 && mv ${ROOT}/${LINUX_DEPLOYMENT_DIR}/${SOURCE_DIR}/${ARCH_TYPE}/" + f"{folder_name} {self.SOURCE_PATH}",
                self._get_linux_kernel_version()))
        else:
            raise Exception(f"Unknown linux kernel source '{linux_kernel_source}'")

class linux_kernel_clean(LinuxKernelDeploymentTask):

    def __init__(self):
        super().__init__()
        self.set_name(linux_kernel_clean.__name__)

    def execute(self):

        arch_type = self._get_arch_type()
        used_compiler = self._get_compiler()

        self.subprocess_must_succeed(f"cd {self.SOURCE_PATH}; make O={self.BUILD_PATH} -C {self.SOURCE_PATH} ARCH=" +
            arch_type.lower() + " CROSS_COMPILE=" + used_compiler + " distclean",
            communication_mode = CommunicationMode.PIPE_OUTPUT)

class linux_kernel_configure(LinuxKernelDeploymentTask):

    def __init__(self):
        super().__init__()
        self.set_name(linux_kernel_configure.__name__)

    def execute(self):

        arch_type = self._get_arch_type()
        used_compiler = self._get_compiler()
        target = self._get_linux_kernel_config_target()

        self.subprocess_must_succeed(f"cd {self.SOURCE_PATH}; make O={self.BUILD_PATH} -C {self.SOURCE_PATH} ARCH=" + arch_type.lower() +
            " CROSS_COMPILE=" + used_compiler + "- " + target,
            communication_mode = CommunicationMode.PIPE_OUTPUT)

        config_flags_raw = self.get_environment().getVariableValue("LINUX_KERNEL_CONFIG_FLAGS")

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

        config_target = ""

        config_adjustment_mode = self.get_environment_param("LINUX_KERNEL_CONFIG_ADJUSTMENT_MODE")

        if  config_adjustment_mode == "PARAMETERS_ONLY":
            config_target = "savedefconfig"
        elif config_adjustment_mode == "USER_INTERACTIVE":
            config_target = "menuconfig"

        self.subprocess_must_succeed(f"cd {self.SOURCE_PATH}; make O={self.BUILD_PATH} -C {self.SOURCE_PATH} "
            "ARCH=" + arch_type.lower() + " CROSS_COMPILE=" + used_compiler + "- " + config_target,
            communication_mode = CommunicationMode.PIPE_OUTPUT)

class linux_kernel_build(LinuxKernelDeploymentTask):
    def __init__(self):
        super().__init__()
        self.set_name(linux_kernel_build.__name__)

    def execute(self):

        build_targets = self._get_linux_kernel_build_targets()
        arch_type = self._get_arch_type()
        used_compiler = self._get_compiler()

        additional_params = ""

        if build_targets.find("modules_install") :
            # https://www.kernel.org/doc/Documentation/kbuild/modules.txt
            additional_params = additional_params + f" INSTALL_MOD_PATH={self.BUILD_PATH}"
        elif build_targets.find("uImage"):
            additional_params = additional_params + " LOADADDR=0x10000"

        self.subprocess_must_succeed(f"cd {self.SOURCE_PATH}; make O={self.BUILD_PATH} -C {self.SOURCE_PATH} ARCH=" +
            arch_type.lower() + " CROSS_COMPILE=" + used_compiler + "- " + "-j${BUILD_SYSTEM_CORES_NUMBER}" +
            additional_params + " ${LINUX_KERNEL_BUILD_TARGETS}",
            communication_mode = CommunicationMode.PIPE_OUTPUT)

class linux_kernel_deploy(LinuxKernelDeploymentTask):
    def __init__(self):
        super().__init__()
        self.set_name(linux_kernel_deploy.__name__)

    def execute(self):

        self.subprocess_must_succeed(f"rm -rf {self.DEPLOY_PATH}; mkdir -p {self.DEPLOY_PATH};")

        products_folder = "arch/" + self._get_arch_type().lower() + "/boot"

        path_prefix = f"{self.BUILD_PATH}"

        files_list: list = [
            os.path.join( path_prefix, products_folder, "Image" ),
            os.path.join( path_prefix, products_folder, "zImage" ),
            os.path.join( path_prefix, products_folder, "Image.gz" ),
            os.path.join( path_prefix, products_folder, "compressed/vmlinux" ) ]

        for file in files_list:
            self.subprocess_must_succeed(f"cp {file} {self.DEPLOY_PATH}/ || :")

        directories_list: list = [
              os.path.join( path_prefix, products_folder, "dts" )
              ]

        for directory in directories_list:
            self.subprocess_must_succeed(f"cp -r {directory} {self.DEPLOY_PATH}/")

class linux_kernel_run_on_qemu(LinuxKernelDeploymentTask):
    def __init__(self):
        super().__init__()
        self.set_name(linux_kernel_run_on_qemu.__name__)

    def execute(self):
        arch_type = self._get_arch_type()

        if arch_type == "ARM":
            self.subprocess_must_succeed("qemu-system-arm -machine ${ARM_MACHINE_TYPE} "
                "-nographic -smp 1 -m 512M -dtb " + f"{self.DEPLOY_PATH}" + "/${LINUX_KERNEL_DTB_LOCATION_ARM} "
                "-kernel " + f"{self.DEPLOY_PATH}" + "/zImage -append console=ttyAMA0")
        elif arch_type == "ARM64":
            self.subprocess_must_succeed("qemu-system-aarch64 -machine ${ARM64_MACHINE_TYPE} -cpu cortex-a57 -machine type=${ARM64_MACHINE_TYPE} "
                "-nographic -smp 1 -m 512M "
                f"-kernel {self.DEPLOY_PATH}/Image -append console=ttyAMA0")
        else:
            raise Exception(f"Unsupported architecture type '{arch_type}'")
