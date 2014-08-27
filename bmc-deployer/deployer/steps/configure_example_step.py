'''
Created on Aug 19, 2014

'''
__all__ = [
    'Step',
]

import time

from base_step import BaseStep 

class Step(BaseStep):
    '''
    This step is used to install the yum
    '''

    def _pre_check(self):   
        """
        Do pre-check for this step.
        No return value.
        Raise Exception when check failed
        """ 
        time.sleep(1)
        self._log_info("Configure Yum Step pre-check is done.")

    def _execute(self):    
        """
        Execute this step.
        No return value.
        Raise Exception when check failed
        """ 
        time.sleep(10)
        self._record_progress(50)
        time.sleep(10)
        self._record_progress(100)
        self._log_info("Configure Yum Step execution is done.")

    def _post_check(self):    
        """
        Do post-check for this step.
        No return value.
        Raise Exception when check failed
        """ 
        time.sleep(1)
        self._log_info("Configure Yum post-check is done.")
        
    @staticmethod
    def pre_check_time_estimate():   
        """
        Return the time estimation in second of pre-check for this step.
        """ 
        return 1;

    @staticmethod
    def execute_time_estimate():    
        """
        Return the time estimation in second of execution for this step.
        """ 
        return 20;
    
    @staticmethod
    def post_check_time_estimate():    
        """
        Return the time estimation in second of post-check for this step.
        """ 
        return 1;
    