'''
Created on Aug 22, 2014

'''
__all__ = [
    'StepLoader',
    'StepChecker',
]

import os
import time

from utils.deployer_logger import DeployerLoggerFactory

'''
This class is used to check step status
'''

STATUS_PATH = "../status"

class FileNotExistError(IOError):
    """
    A 'reload' operation failed.
    This exception is a subclass of ``IOError``.
    """
    def __init__(self, msg):
        IOError.__init__(self, msg)
        
class StepChecker(object):
    '''
    classdocs
    '''

    def __init__(self, step_name, step_on_node):
        self.__step_name = step_name
        self.__step_on_node = step_on_node
        self.__step_on_node = step_on_node
        self.__path = STATUS_PATH + "/" + self.__step_on_node + "/"
        self.__status_file = self.__path + self.__step_name + ".status"
        self.__progress_file = self.__path + self.__step_name + ".progress"

        self.__logger = DeployerLoggerFactory().getlogger()
            
    def check_status(self, isBlock=True, time_estimation=None):
        if isBlock == False:
            return self.__non_block_check()
        if isBlock == True:
            return self.__block_check(time_estimation)

    def check_progress(self):
            return self.__fetch_progress()

    def __block_check(self,time_estimation):
        estimation = 0;
        while (True):
            ret = self.__non_block_check()
            if ret == 0 or ret == 3 or ret == 6 or ret == 8 or ret == 9:
                return ret
            time.sleep(10)
            estimation += 10
            if time_estimation != None and time_estimation != 0 and estimation > 2*time_estimation:
                return 10 # means timeout            
    
    def __non_block_check(self):
        try:
            status = self.__fetch_status()
            self.__logger.info(self.__status_file + " status is " + status)
            if status == "start-pre-check":
                return 1
            if status == "pre-check-ok":
                return 2
            if status == "pre-check-failed":
                return 3
            if status == "start-execute":
                return 4
            if status == "execute-ok":
                return 5
            if status == "pre-check-failed":
                return 6
            if status == "start-post-check":
                return 7
            if status == "post-check-ok":
                return 8
            if status == "post-check-failed":
                return 9
            return 0
        except Exception, e:
            self.__logger.error(e)
            return 0
                      
    def __fetch_status(self):
        if os.path.exists(self.__status_file) == False :
            raise FileNotExistError(self.__status_file + ' is not exist.')
        try:
            status_recorder = open(self.__status_file, 'r')
            return status_recorder.readline()
        finally:
            status_recorder.close()

    def __fetch_progress(self):
        if os.path.exists(self.__progress_file) == False :
            return 0
        try:
            progress_recorder = open(self.__progress_file, 'r')
            return int(progress_recorder.readline())
        except Exception, e:
            self.__logger.error(e)
            return 0
        finally:
            progress_recorder.close()
                            
class StepLoader(object):
    '''
    classdocs
    '''
        
    def __init__(self, step_name, step_on_node):
        self.__step_name = step_name
        self.__step_on_node = step_on_node
        self.__class_name = "Step"
        self.__method_name = "run"
        self.__logger = DeployerLoggerFactory().getlogger()

    def get_step_instance(self):
        try:
            step_module = __import__(self.__step_name, fromlist=[self.__class_name])
        except ImportError, ex:
            self.__logger.info(ex)
            return None
        try:
          
            step_class = getattr(step_module, self.__class_name)
        except AttributeError, ex:
            self.__logger.info(ex)
            self.__logger.info("This step module class name is not 'Step'.")
            return None
        step = step_class(self.__step_name, "../status", self.__step_on_node)
        if step == None :
            self.__logger.info("This step module has no required constructor(name, status_path, node) .")
            return None
        method = getattr(step, self.__method_name)
        if method == None :
            self.__logger.info("This step module has no required method.")
            return None   
        return step   

    def get_step_class(self):
        try:
            step_module = __import__(self.__step_name, fromlist=[self.__class_name])
        except ImportError, ex:
            self.__logger.info(ex)
            return None
        try:
            step_class = getattr(step_module, self.__class_name)
            return step_class
        except AttributeError, ex:
            self.__logger.info(ex)
            self.__logger.info("This step module class name is not 'Step'.")
            return None
