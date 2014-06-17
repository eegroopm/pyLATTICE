# -*- coding: utf-8 -*-
"""
Created on Mon Apr 21 10:36:10 2014

@author: eegroopm
"""
from PyQt4.QtGui import QDialog, QListWidgetItem
from PyQt4.QtCore import Qt
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
        
class ManualConditionsDialog(QDialog):
    """Allows for the user to input special reflection conditions manually.
    
    This is a simple interface where the user can choose if:then conditions for
    combinations of h,k,l. The results are then converted to python/pandas syntax
    from where they can be parsed by pylattice"""
    
    def __init__(self,conditions= [], parent= None):
        QDialog.__init__(self,parent)
        gui.loadUi(__file__,self)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        
        self.manualConds = conditions
        
        #self.manualCondList.addItems(self.manualConds)
        for c in self.manualConds:
            self.newItem(c)
            
        
        self.Disable(True)
        
        self.signals_slots()
    
    def newItem(self,text):
        """Make a new item for the item list"""
        item = QListWidgetItem(text)
        item.setFlags(Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        self.manualCondList.addItem(item)
    
    def Disable(self,bool):
        #set items disabled to start
        for item in [self.IF2, self.IF3,self.ifVal1,self.ifVal2,self.ifVal3,
                     self.label_3,self.label_4,self.label_5,self.THEN2,self.THEN3,
                     self.pm1,self.pm2,self.ifAND1,self.ifAND2]:
            item.setDisabled(bool)
    
    def signals_slots(self):
        self.addCond.clicked.connect(self.parse)
        self.IF1.currentIndexChanged.connect(self.toggleON)
        self.deleteButton.clicked.connect(self.deleteCond)
        
    def deleteCond(self):
        """remove selected conditions"""
        for item in self.manualCondList.selectedItems():
            ind = self.manualCondList.row(item)
            d = self.manualCondList.takeItem(ind)
                
    
    def toggleON(self):
        """Enabled/disables if options based upon first combo box choice."""
        if self.IF1.currentIndex() == 0:
            self.Disable(True)

        else:
            self.ifVal1.setEnabled(True)
            self.label_3.setEnabled(True)
            self.ifAND1.setEnabled(True)
            self.ifAND2.setEnabled(True)
        
    def parse(self):
        """Parses current options and converts them into python/pandas syntax"""
        cond = 'if '
        if1 = self.IF1.currentText()
        ifVal1 = self.ifVal1.value()
        ifand1 = self.ifAND1.isChecked()
        ifand2 = self.ifAND2.isChecked()
        
        #Parse 'if' statements
        if if1 == 'True':
            cond += (if1 + ': ')
        
        else:
            cond += '(%s == %i)' % (if1,ifVal1)
            if ifand1:
                cond += ' & (%s == %i)' % (self.IF2.currentText(),ifVal2.value())
            if ifand2:
                cond += ' & (%s == %i)' % (self.IF3.currentText(),ifVal3.value())
            cond += ': '
        
        then1 = self.THEN1.currentText()
        N = self.THENN.value()
        cond += '(%s' % then1
        if self.thenAND1.isChecked():
            cond += ' %s %s' % (self.pm1.currentText(),self.THEN2.currentText())
        if self.thenAND2.isChecked():
            cond += ' %s %s' % (self.pm2.currentText(),self.THEN3.currentText())
        
        cond += (')%' + '%i == 0' % N)
        
        self.newItem(cond)
        