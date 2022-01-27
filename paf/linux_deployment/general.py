'''
Created on Dec 29, 2021

@author: vladyslav_goncharuk
'''

from paf.paf_impl import Task

class LinuxDeploymentTask(Task):

    def _get_arch_type(self):
        return self.get_environment_param("ARCH_TYPE")

    def _get_compiler(self):
        compiler = ""

        arch_type = self._get_arch_type()

        if(arch_type == "ARM"):
            compiler = "${ARM_COMPILER}"
        elif(arch_type == "ARM64"):
            compiler = "${ARM64_COMPILER}"
        else:
            raise Exception("Impossible to determine compiler path for '' architecture!")

        return compiler

    def _get_compiler_path(self):
        compiler_path = ""

        arch_type = self._get_arch_type()

        if(arch_type == "ARM"):
            compiler_path = "${ARM_COMPILER_PATH}"
        elif(arch_type == "ARM64"):
            compiler_path = "${ARM64_COMPILER_PATH}"
        else:
            raise Exception("Impossible to determine compiler path!")

        return compiler_path

class prepare_directories(LinuxDeploymentTask):

    def __init__(self):
        super().__init__()
        self.set_name(prepare_directories.__name__)

    def execute(self):
        if self.get_environment_param("CLEAR") == "True":
            self.subprocess_must_succeed("rm -rf ${ROOT}/${LINUX_DEPLOYMENT_DIR}")

        self.subprocess_must_succeed("mkdir -p ${ROOT}")
        self.subprocess_must_succeed("mkdir -p ${ROOT}/${LINUX_DEPLOYMENT_DIR}")
        self.subprocess_must_succeed("mkdir -p ${ROOT}/${LINUX_DEPLOYMENT_DIR}/${DOWNLOAD_DIR}")
        self.subprocess_must_succeed("mkdir -p ${ROOT}/${LINUX_DEPLOYMENT_DIR}/${SOURCE_DIR}")
        self.subprocess_must_succeed("mkdir -p ${ROOT}/${LINUX_DEPLOYMENT_DIR}/${BUILD_DIR}")
        self.subprocess_must_succeed("mkdir -p ${ROOT}/${LINUX_DEPLOYMENT_DIR}/${DEPLOY_DIR}")

class install_dependencies(LinuxDeploymentTask):

    def __init__(self):
        super().__init__()
        self.set_name(install_dependencies.__name__)

    def execute(self):

        used_compiler = ""

        arch_type = self.get_environment_param("ARCH_TYPE")

        if(arch_type == "ARM"):
            used_compiler = "${ARM_COMPILER}"
        elif(arch_type == "ARM64"):
            used_compiler = "${ARM64_COMPILER}"

        self.subprocess_must_succeed("sudo -S apt-get -y install gcc-" + used_compiler + " libssl-dev qemu-system-arm")
