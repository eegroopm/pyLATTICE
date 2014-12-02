# -*- coding: utf-8 -*-
"""
Created on Mon Apr 21 10:32:36 2014

@author: eegroopm
"""
import os
#Try to make IPython work
os.environ['QT_API'] = 'pyqt'
import sip
sip.setapi("QString", 2)
sip.setapi("QVariant", 2)

from PyQt4.QtGui import QWidget
#IPython widget stuff
from IPython.qt.console.rich_ipython_widget import RichIPythonWidget
from IPython.qt.inprocess import QtInProcessKernelManager
#from IPython.lib import guisupport

class IPythonInProcess(object):
    def __init__(self,common,customBanner=None):
        if customBanner!=None: self.banner=customBanner
        self.common = common
        self.kernel_manager = None
        self.kernel = None
        self.control = None
        self.kernel_client = None
        self.init_qtconsole()
        
    def init_qtconsole(self):
        self.main()
    
    def print_process_id(self):
        print('Process ID is:', os.getpid())
    
    
    def main(self):
        # Print the ID of the main process
        #self.print_process_id()
    
        #app = guisupport.get_app_qt4()
    
        # Create an in-process kernel
        # >>> print_process_id()
        # will print the same process ID as the main process
        self.kernel_manager = QtInProcessKernelManager()
        self.kernel_manager.start_kernel()
        self.kernel = self.kernel_manager.kernel
        self.kernel.gui = 'qt4'
        self.kernel.shell.push(self.common.__dict__)
        self.kernel_client = self.kernel_manager.client()
        self.kernel_client.start_channels()
        
        def stop():
            self.kernel_client.stop_channels()
            self.kernel_manager.shutdown_kernel()
            #app.exit()
    
        self.control = RichIPythonWidget(banner = self.banner)
        self.control.kernel_manager = self.kernel_manager
        self.control.kernel_client = self.kernel_client
        self.control.exit_requested.connect(stop)
        
        #start widget with certain inputs:
        #import pylab, which includes all numpy; import pandas as pd
        #second argument is whether the execution is hidden e.g. whether a line is used
        #I have turned on hide.
        
        self.control._execute('import pylab as pl; import pandas as pd',True)
        
    def SHOW(self):
        self.control.show()
    
        #guisupport.start_event_loop_qt4(app)

    def pushVariables(self,variableDict):
        """ Given a dictionary containing name / value pairs, push those variables to the IPython console widget """
        self.kernel_manager.kernel.shell.push(variableDict)
    def clearTerminal(self):
        """ Clears the terminal """
        self._control.clear()
    def printText(self,text):
        """ Prints some plain text to the console """
        self._append_plain_text(text)        
    def executeCommand(self,command):
        """ Execute a command in the frame of the console widget """
        self.control._execute(command,False)
        

class IPythonConsole(QWidget, IPythonInProcess):
    def __init__(self,common,banner=None,parent=None):
        QWidget.__init__(self,parent)
        IPythonInProcess.__init__(self,common,customBanner=banner)
        self.common = common
        
        self.namespace = self.kernel.shell.user_ns
        self.hidden = self.kernel.shell.user_ns_hidden
        self.control.executed.connect(self.refreshCommon)
        
    def refreshCommon(self):
        #"out" copied from ipython who_ls magics
        #update common block with 
        varlist = self.who_ls()
        ns = {k: self.namespace.get(k, None) for k in varlist}
        self.common.__dict__.update(ns)
        
        
    def who_ls(self, parameter_s=''):
        """This is copied from IPython.core.magics.namespace.
        
        Return a sorted list of all interactive variables.

        If arguments are given, only variables of types matching these
        arguments are returned.

        Examples
        --------

        Define two variables and list them with who_ls::

          In [1]: alpha = 123

          In [2]: beta = 'test'

          In [3]: %who_ls
          Out[3]: ['alpha', 'beta']

          In [4]: %who_ls int
          Out[4]: ['alpha']

          In [5]: %who_ls str
          Out[5]: ['beta']
        """

        user_ns = self.namespace
        user_ns_hidden = self.hidden
        nonmatching = object()  # This can never be in user_ns
        out = [ i for i in user_ns
                if not i.startswith('_') \
                and (user_ns[i] is not user_ns_hidden.get(i, nonmatching)) ]

        typelist = parameter_s.split()
        if typelist:
            typeset = set(typelist)
            out = [i for i in out if type(user_ns[i]).__name__ in typeset]

        out.sort()
        return out
