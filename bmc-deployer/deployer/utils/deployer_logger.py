#!/usr/bin/env python
"""
Common logger class for deployer.
Usage: Please give the log file name when you init the class.
    example: bdclogger = BDCLogger("/tmp/youlog.log")

"""
__all__ = [
    'DeployerLoggerFactory',
]


import logging

'''
Use decorator to make the class singleton
'''
def singleton(cls, *args, **kw):
    instances = {}
    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singleton

@singleton
class DeployerLoggerFactory(object):

    __deployer_logger = None
    __logger_name = None


    '''
    Init the logger and it will be the only logger in the instance list
    Please give the logger name and log file path.
    If logfilename is not specified, only console log will be used.
    '''
    def createlogger(self, loggername, logfilename = ""):
        if self.__logger_name != loggername:
            self.__deployer_logger = logging.getLogger(loggername)
            self.__deployer_logger.setLevel(logging.DEBUG)
            self.__addconsolehandler()
            if logfilename:
                self.__addfilehandler(logfilename)


    def __addfilehandler(self, logfilename):
        # create file handler which logs even debug messages
        fh = logging.FileHandler(logfilename)
        fh.setLevel(logging.DEBUG)

        # create formatter and add it to the handlers
        fhFormatter = logging.Formatter('%(asctime)s %(module)s %(lineno)d - %(levelname)s - %(message)s')
        fh.setFormatter(fhFormatter)

        self.__deployer_logger.addHandler(fh)


    def __addconsolehandler(self):
        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # create formatter and add it to the handlers

        chFormatter = logging.Formatter('%(message)s')

        ch.setFormatter(chFormatter)

        # add the handlers to logger
        self.__deployer_logger.addHandler(ch)

    '''
    Get the logger from the singleton class
    Init once use every where :)
    '''
    def getlogger(self):
        if self.__deployer_logger == None:
            defaultloggername = "defualtlogger"
            self.createlogger(defaultloggername)
            self.__deployer_logger.info("Use default settings to create logger. Name: %s" %
                (defaultloggername))

        return self.__deployer_logger

if __name__ == '__main__':

    loggerfactory = DeployerLoggerFactory()
    loggerfactory.getlogger().info("testlog")

    loggerfactory.createlogger("testname", "/tmp/testname.log")
    loggerfactory.getlogger().info("xxxxxxxx")
    loggerfactory1 = DeployerLoggerFactory()
    loggerfactory1.getlogger().info("abc")

