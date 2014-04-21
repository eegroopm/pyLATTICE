# -*- coding: utf-8 -*-
"""
Created on Mon Apr 21 10:32:36 2014

@author: eegroopm
"""

from PyQt4.QtGui import QWidget
#IPython widget stuff
from IPython.qt.console.rich_ipython_widget import RichIPythonWidget
from IPython.qt.inprocess import QtInProcessKernelManager
from IPython.lib import guisupport

from .pyqtresizer import logit,slResizer,Resizer

import sys
sys.path.append("..") #import from parent directory
import gui

##IPython Widget
class IPythonConsole(QWidget):
    def __init__(self,parent=None):
        QWidget.__init__(self,parent)
        gui.loadUi(__file__,self)
        self.resize=slResizer(self)
    
    #for maximizing/resizing console inside of window
    def resizeEvent(self, ev):
        #when a resize event occurs at all we need to resize
        self.resize.refresh()

    def changeEvent(self, ev):
        if ev.type()==105:
          #on a maximize screen event we need to resize
          self.resize.refresh()

class QIPythonWidget(RichIPythonWidget):
    """ Convenience class for a live IPython console widget. We can replace the standard banner using the customBanner argument"""
    def __init__(self,customBanner=None,*args,**kwargs):
        if customBanner!=None: self.banner=customBanner
        super(QIPythonWidget, self).__init__(*args,**kwargs)
        self.kernel_manager = kernel_manager = QtInProcessKernelManager()
        kernel_manager.start_kernel()
        kernel_manager.kernel.gui = 'qt4'
        self.kernel_client = kernel_client = self._kernel_manager.client()
        kernel_client.start_channels()
        
        
        def stop():
            kernel_client.stop_channels()
            kernel_manager.shutdown_kernel()
            guisupport.get_app_qt4().exit()            
        self.exit_requested.connect(stop)

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
        self._execute(command,False)