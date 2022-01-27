'''
Created on Dec 29, 2021

@author: vladyslav_goncharuk
'''

import re
from argparse import ArgumentParser

from paf import paf_impl
from paf.paf_impl import logger

def main():
    parser = ArgumentParser()
    parser.add_argument("-t", "--task", dest="tasks",
                        help="task to be executed", metavar="TASK", action="append")
    parser.add_argument("-s", "--scenario", dest="scenarios",
                        help="scenarios to be executed", metavar="SCENARIO", action="append")
    parser.add_argument("-ph", "--phase", dest="phases",
                        help="phases to be executed", metavar="PHASE", action="append")
    parser.add_argument("-c", "--config", dest="configs",
                        help="configuration files", metavar="CONFIG", action="append")
    parser.add_argument("-p", "--parameter", dest="parameters",
                        help="environment variable", metavar="ENV_VAR", action="append")
    parser.add_argument("-imd", "--import-module-dir", dest="import_module_dirs",
                        help="import module directories", metavar="IMP", action="append")
    parser.add_argument("-ld", "--log-dir", dest="log_dir",
                        help="output of the script will be stored to this directory. If not set - output is not stored.", metavar="LOG_FILE")

    args = parser.parse_args()

    execution_context = paf_impl.ExecutionContext(args.log_dir)

    environment = paf_impl.Environment()

    # Get import module search paths
    import_module_dirs = args.import_module_dirs
    if import_module_dirs:
        execution_context.import_modules(import_module_dirs)

    # From the command line parse the elements, which we need to execute
    tasks = args.tasks
    if tasks:
        for task_name in tasks:
            execution_context.add_execution_element(paf_impl.ExecutionElement.ExecutionElementType_Task, task_name)

    phases = args.phases
    if phases:
        for phase_name in phases:
            execution_context.add_execution_element(paf_impl.ExecutionElement.ExecutionElementType_Phase, phase_name)

    scenarios = args.scenarios
    if scenarios:
        for scenario_name in scenarios:
            execution_context.add_execution_element(paf_impl.ExecutionElement.ExecutionElementType_Scenario, scenario_name)

    # parse configuration files in order to get list of defined scenarios and phases
    configs = args.configs
    if configs:
        for config_path in configs:
            execution_context.parse_config(config_path, execution_context, environment)

    # From the command line parse parameters
    parameters = args.parameters

    if parameters:
        for parameter in parameters:
            splited_parameter = re.compile("[ ]*=[ ]*").split(parameter)
            if len(splited_parameter) == 2:
                environment.setVariableValue(splited_parameter[0], splited_parameter[1])

    execution_context.execute(environment)

    logger.info(f"Last trace ...")

main()