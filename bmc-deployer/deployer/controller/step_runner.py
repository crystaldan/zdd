'''
Created on Aug 23, 2014

This class is used to run the step on target machine.
Example usage:
1. Run step in non-block mode
python step_runner.py -s steps.install_example_step -n node

2. Check step status in non-block mode
python step_runner.py -s steps.install_example_step -n node -c status

3. Check step status in non-block mode
python step_runner.py -s steps.install_example_step -n node -c progress

4. Check step status in block mode
python step_runner.py -s steps.configure_example_step -n node -m block
'''
import time
import sys
import os
import subprocess

sys.path.append("../")

from step_helper import StepLoader
from step_helper import StepChecker
from utils.deployer_logger import DeployerLoggerFactory as loggerFactory
from utils import argparse

def main():

    loggername = 'step_runner'
    logfiletimestamp = time.strftime("%Y%m%d%H", time.localtime())
    loggerfactory = loggerFactory()
    log_path = '../log/'
    if os.path.exists(log_path) == False :
        os.makedirs(log_path)  
    loggerfactory.createlogger(loggername,
            '../log/%s-%s.log' % (loggername, logfiletimestamp))
    runner_logger = loggerfactory.getlogger()

    runnerparser = argparse.ArgumentParser(
            description='Deployer step runner.')

    # Parameter parser for controller.
    runnerparser.add_argument('-s', '--step', required=True,
            help='step module name to run, shall include package like package.step_module.')
    runnerparser.add_argument('-n', '--node', required=True,
            help='node name to run step on, shall be unique name to identify the node.')
    runnerparser.add_argument('-m', '--mode', required=False,
            choices=['block', 'nb' ], default='nb',
            help='if block, it will return the result until reach terminate status. if nb, means non-block, it will return current status immediately.')
    runnerparser.add_argument('-c', '--check', required=False,
            choices=['status', 'time', 'progress' ], default=None,
            help='if no check, will run step, if provide check, will just check step. if time, will return the time estimation of this step. if progress, will return the percent of whole step progress.')

    args = runnerparser.parse_args()
    if args.mode == 'nb' and args.check == None:
        runner_logger.info("Start to run step %s on node %s in non block mode.", args.step, args.node)
        ret = subprocess.Popen(["python", "step_runner.py", "-s", args.step, "-n" ,args.node, "-m", "block"], shell=True)
        runner_logger.info("Already trigger to run step %s on node %s in block mode.", args.step, args.node)
        return ret

    if args.mode == 'block' and args.check == None:
        step_loader = StepLoader(args.step, args.node)
        step = step_loader.get_step_instance()
        if step == None:
            runner_logger.error("Failed to load the step instance.")
        else:
            runner_logger.info("Start to run step %s on node %s.", args.step, args.node)
            step.run()
            runner_logger.info("End to run step %s on node %s.", args.step, args.node)
        return

    if args.mode == 'block' and args.check =='status':
        step_loader = StepLoader(args.step, args.node)
        step_class = step_loader.get_step_class()
        ret = None
        if step_class == None:
            runner_logger.error("Failed to load the step class.")
        else:
            runner_logger.info("Start to check in block for step %s on node %s.", args.step, args.node)
            stepChecker = StepChecker(args.step, args.node)
            ret = stepChecker.check_status(True, step_class.time_estimate(step_class))
            runner_logger.info("End to check in block for step %s on node %s. The status is %d.", args.step, args.node, ret) 
        return ret;

    if args.mode == 'nb' and args.check =='status':
        runner_logger.info("Start to check in non-block for step %s on node %s.", args.step, args.node)
        stepChecker = StepChecker(args.step, args.node)
        ret = stepChecker.check_status(False)
        runner_logger.info("End to check in non-block for step %s on node %s. The status is %d.", args.step, args.node, ret) 
        return ret

    if args.check == 'progress': #ignore the mode, always be non-block
        runner_logger.info("Start to check progress of step %s on node %s.", args.step, args.node)
        stepChecker = StepChecker(args.step, args.node)
        ret = stepChecker.check_progress()
        runner_logger.info("End to check progress of step %s on node %s. The status is %d.", args.step, args.node, ret) 
        return ret

    if args.check == 'time': #ignore the mode, always be non-block
        step_loader = StepLoader(args.step, args.node)
        step_class = step_loader.get_step_class()
        ret = None
        if step_class == None:
            runner_logger.error("Failed to load the step class.")
        else:
            runner_logger.info("Start to get the time estimation of step %s on node %s.", args.step, args.node)
            ret = step_class.time_estimate(step_class)
            runner_logger.info("End to get the time estimation of step %s on node %s. The time estimation is %d", args.step, args.node, ret) 
        return ret
    
if __name__ == '__main__':
    main()
