# -*- coding: utf-8 -*-
"""
Created on Mon Apr 21 10:36:10 2014

@author: eegroopm
"""
from PyQt4.QtGui import QDialog
import sys
sys.path.append("..") #import from parent directory
import gui

###############################################################################
## Various Input Dialogs ##
###############################################################################
class MineralListDialog(QDialog):
    def __init__(self,parent=None):
        QDialog.__init__(self,parent)
        gui.loadUi(__file__,self)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

class NewMineralDialog(QDialog):
    def __init__(self,parent=None):
        QDialog.__init__(self,parent)
        gui.loadUi(__file__,self)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)