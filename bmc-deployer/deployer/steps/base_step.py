'''
Created on Aug 19, 2014

This is step base class.
All steps need to drive from this base class.
'''
__all__ = [
    'BaseStep',
]

import os
import shutil
import logging
import sys

sys.path.append("../utils")

from abc import ABCMeta, abstractmethod

from utils.deployer_logger import DeployerLoggerFactory

class BaseStep(object):
    '''
    This is base step class, all specific sub class shall derive from this class.
    Here name means step name, path means record status path, node means node id.
    '''
    __metaclass__ = ABCMeta

    def __init__(self, name, status_path, node):
        self.__node = node
        self.__name = name
        self.__path = status_path + "/" + self.__node + "/"
        self.__status_file = self.__path + self.__name + ".status"
        self.__status_temp = self.__path + self.__name + ".stat"
        self.__progress_file = self.__path + self.__name + ".progress"
        self.__progress_temp = self.__path + self.__name + ".prog"
        self.__step_log = self.__path + self.__name + ".log"
        self.__step_logger = None
        self.__step_logger_handler = None
        self.__deployer_logger = None
        self.__status_recorder = None

    def __del__(self):
        self.__clean_resource()

    def __init_resource(self):
        self.__remove_file(self.__status_file)
        self.__remove_file(self.__status_temp)
        self.__remove_file(self.__progress_file)
        self.__remove_file(self.__progress_temp)
        self.__remove_file(self.__step_log)
        #set the step trace file
        self.__make_dir(self.__path)
        self.__step_logger_handler=logging.FileHandler(self.__step_log)
        formatter = logging.Formatter('%(asctime)s %(module)s %(lineno)d - %(levelname)s - %(message)s')
        self.__step_logger_handler.setFormatter(formatter)
        self.__step_logger = logging.getLogger()
        self.__step_logger.addHandler(self.__step_logger_handler)
        #set the deployer logger
        self.__deployer_logger = DeployerLoggerFactory().getlogger()
        
    def __clean_resource(self):
        if self.__status_recorder != None:
            self.__status_recorder.close()
        if self.__step_logger != None:
            self.__step_logger.removeHandler(self.__step_logger_handler)
        if self.__step_logger_handler != None:    
            self.__step_logger_handler.close()
        
    def __remove_file(self, status_file):
        if os.path.exists(status_file):
            os.remove(status_file)
            
    def __make_dir(self, status_path):
        if os.path.exists(status_path) == False :
            os.makedirs(status_path)    
                
    def run(self):
        try:
            self.__init_resource()
            if (False == self.__do_pre_check()):
                return
            if (False == self.__do_execute()):
                return
            self.__do_post_check()
        finally:
            self.__clean_resource()
    
    def _log_debug(self, msg):
        self.__step_logger.debug(msg)
        self.__deployer_logger.debug(msg);

    def _log_info(self, msg):
        self.__step_logger.info(msg)
        self.__deployer_logger.info(msg)
    
    def _log_warn(self, msg):
        self.__step_logger.warn(msg)
        self.__deployer_logger.warn(msg)
    
    def _log_error(self, msg):
        self.__step_logger.error(msg)
        self.__deployer_logger.error(msg)
    
    def _log_fatal(self, msg):
        self.__step_logger.fatal(msg)
        self.__deployer_logger.fatal(msg)

    def _record_progress(self,progress):
        """
        private method to record step progress, input argument progress is percent number.
        For instance progress=90, means 90% of whole step procedure is done
        """
        self.__status_recorder = open(self.__progress_temp, 'w')
        self.__status_recorder.write(str(progress))
        self.__status_recorder.flush()
        self.__status_recorder.close()
        shutil.move(self.__progress_temp,self.__progress_file)

    def __record_status(self,status):
        """
        private method to record step status.
        """
        self.__status_recorder = open(self.__status_temp, 'w')
        self.__status_recorder.write(status)
        self.__status_recorder.flush()
        self.__status_recorder.close()
        shutil.move(self.__status_temp,self.__status_file)
    
    def __do_pre_check(self):
        try:
            self._log_info(self.__node + " start to pre-check for step " + self.__name + " .")
            self.__record_status("start-pre-check")
            self._pre_check()  
            self.__record_status("pre-check-ok")
            self._log_info(self.__node + " complete pre-check for step " + self.__name + " .")
            return True        
        except Exception,ex:
            self._log_error(ex)
            self.__record_status("pre-check-failed")
            self._log_error(self.__node + " fail to pre-check for step " + self.__name + " .")
            return False
        
    def __do_execute(self):    
        try:
            self._log_info(self.__node + " start to execute step " + self.__name + ".")
            self.__record_status("start-execute")
            self._execute()  
            self.__record_status("execute-ok")
            self._log_info(self.__node + " complete execute step " + self.__name + " .")
            return True        
        except Exception,ex:
            self._log_error(ex)
            self.__record_status("execute-failed")
            self._log_error(self.__node + " fail to execute step " + self.__name + " .")
            return False

    def __do_post_check(self):    
        try:
            self._log_info(self.__node + " start to post-check for step " + self.__name + " .")
            self.__record_status("start-post-check")
            self._post_check()  
            self.__record_status("post-check-ok")
            self._log_info(self.__node + " complete post-check for step " + self.__name + " .")
            self._record_progress(100)
            return True        
        except Exception,ex:
            self._log_error(ex)
            self.__record_status("post-check-failed")
            self._log_error(self.__node + " fail to post-check for step " + self.__name + " .")
            return False
            

    '''
    This is class static method to estimate the step duration.
    If the pre_check_time_estimate, execute_time_estimate, post_check_time_estimate not implemented in subclass, the return value will be 0;
    '''
    @staticmethod
    def time_estimate(clazz):
        time_logger = DeployerLoggerFactory().getlogger()
        pre_check_time_estimation = 0
        execute_time_estimation = 0
        post_check_time_estimation = 0
        try:
            pre_check_time_estimation = clazz.pre_check_time_estimate()
        except Exception ,e:
            pre_check_time_estimation = 0
            time_logger.warn(clazz.__module__ + e.message)

        try:
            execute_time_estimation = clazz.execute_time_estimate()
        except Exception ,e:
            execute_time_estimation = 0
            time_logger.warn(clazz.__module__ + e.message)

        try:
            post_check_time_estimation = clazz.post_check_time_estimate()
        except Exception ,e:
            post_check_time_estimation = 0
            time_logger.warn(clazz.__module__ + e.message)
        
        return pre_check_time_estimation + execute_time_estimation + post_check_time_estimation
    
    @abstractmethod
    def _pre_check(self):   
        """
        Do pre-check for this step.
        No return value.
        Raise Exception when check failed
        """ 
        raise NotImplementedError

    @abstractmethod
    def _execute(self):    
        """
        Execute this step.
        No return value.
        Raise Exception when check failed
        """ 
        raise NotImplementedError

    @abstractmethod
    def _post_check(self):    
        """
        Do post-check for this step.
        No return value.
        Raise Exception when check failed
        """ 
        raise NotImplementedError
    
    @staticmethod
    def pre_check_time_estimate():   
        """
        Return the time estimation in second of pre-check for this step.
        """ 
        raise NotImplementedError(" static method pre_check_time_estimate is not implemented.")

    @staticmethod
    def execute_time_estimate():    
        """
        Return the time estimation in second of execution for this step.
        """ 
        raise NotImplementedError(" static method execute_time_estimate is not implemented.")

    @staticmethod
    def post_check_time_estimate():    
        """
        Return the time estimation in second of post-check for this step.
        """ 
        raise NotImplementedError(" static method post_check_time_estimate is not implemented.")