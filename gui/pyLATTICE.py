#!/usr/bin/python ~/Documents/Research/Spyder\ Projects/pyLATTICE/
# -*- coding: utf-8 -*-
""" 
pyLATTICE is...
"""
from __future__ import division #necessary for python2
from __future__ import unicode_literals

# define authorship information
__authors__     = ['Evan Groopman', 'Thomas Bernatowicz']
__author__      = ','.join(__authors__)
__credits__     = []
__copyright__   = 'Copyright (c) 2011-2014'
__license__     = 'GPL'

# maintanence information
__maintainer__  = 'Evan Groopman'
__email__       = 'eegroopm@gmail.com'


"""
Created on Wed Apr 11 14:46:56 2012

@author: Evan Groopman

"""
#Main imports
#import sip
from PyQt4 import QtCore, QtGui, uic
import os, re, sys
import numpy as np
import pandas as pd


#Matplotlib imports
import matplotlib as mpl
mpl.use('Qt4Agg')
#import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar

# Local files in the resource directory
import gui
from resources.TableWidget import TableWidget
from resources.Diffraction import Diffraction
#from resources.pyqtresizer import logit,slResizer,Resizer
from resources.IPythonConsole import IPythonConsole, QIPythonWidget
from resources.common import common
from resources.matplotlibwidget import matplotlibWidget
from resources.Dialogs import MineralListDialog, NewMineralDialog


try:
    from resources.dspace import DSpace
    print('Importing compiled "DSpace"')
except ImportError as error:
    # Attempt autocompilation.
    import pyximport
    pyximport.install()
    from resources._dspace import DSpace
    print('Building "DSpace"')
    
try:
    from resources.diffspot import CalcSpots, CalcSpotsHCP
    print('Importing compiled "DiffSpot"')
except ImportError as error:
    # Attempt autocompilation.
    import pyximport
    pyximport.install()
    from resources._diffspot import CalcSpots, CalcSpotsHCP
    print('Building "DiffSpot"')
    
#need different compiled versions of Cython modules depending on python version
#if sys.version_info[0] == 3:
#    #from resources.dspace import DSpace#Cython function for calculating d-spaces
#    #from resources.diffspot import CalcSpots, CalcSpotsHCP#Cython function for calculating diffraction spot coordinates
#    from resources.pyqtresizer import logit,slResizer,Resizer
#elif sys.version_info[0] == 2:
#    #from resources.dspace_py2 import DSpace#Cython function for calculating d-spaces
#    #from resources.diffspot_py2 import CalcSpots, CalcSpotsHCP#Cython function for calculating diffraction spot coordinates
#    from resources.pyqtresizer_py2 import logit,slResizer,Resizer
    
#from Wulff_net import WULFF
#dealing with unicode characters in windows, which breaks compiled linux rendering
if sys.platform == 'win32':
    mpl.rc('font', **{'sans-serif' : 'Arial Unicode MS','family' : 'sans-serif'})
#elif sys.platform == 'linux':# and os.path.isfile('pyLATTICE'): #on linux AND executable file exists. Does nothing if running from source
#    print('Adjusting font')
#    mpl.rc('font',**{'sans-serif' : 'Bitstream Vera Sans','family' : 'sans-serif'})
#use LaTeX to render symbols
#plt.rc('text', usetex=True)
#mpl.rcParams['mathtext.default'] = 'regular'
##mpl.rcParams['text.latex.preamble'] = [r'\usepackage{textcomp}']
#mpl.rcParams['text.latex.unicode'] = True 

#Other
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

################################################################################
## Gui file ##
# Set up window
class pyLATTICE_GUI(QtGui.QMainWindow):
    
    def __init__(self, parent=None):
        super(pyLATTICE_GUI, self).__init__(parent)
        # load the ui
        gui.loadUi(__file__,self)
        self.version = gui.__version__
        
        self.common = common()
        self.Diffraction = Diffraction()
        self.overline_strings = self.common.overline_strings
        self.DSpaces = self.common.DSpaces
        self.ZoneAxis = self.common.ZoneAxis
        self.u = self.common.u
        self.v = self.common.v
        self.w = self.common.w
        
        #SpaceGroup data
        self.sg = self.common.sg
        self.sghex = self.common.sghex
        self.mineraldb = self.common.mineraldb
        
                
        self.DiffWidget = matplotlibWidget(self.common,self.Diffraction) #mplwidget can access common data
        #self.DiffWidget.setStyleSheet("font-family: 'Arial Unicode MS', Arial, sans-serif; font-size: 15px;")
        self.verticalLayout.addWidget(self.DiffWidget)
        
        self.DiffWidget.distances.connect(self.on_distances_sent)
        
        #self.DiffWidget = self.MplWidget
        self.Plot = self.DiffWidget.canvas.ax
        self.Plot.axis('equal') #locks aspect ratio 1:1, even when zooming
        #matplotlibWidget.setupToolbar(self.DiffWidget.canvas, self.DiffTab)
        # Create the navigation toolbar, tied to the canvas
        self.mpl_toolbar = NavigationToolbar(self.DiffWidget.canvas, self.DiffTab)
        #add widgets to toolbar
        self.comboBox_rotate = QtGui.QComboBox()
        self.checkBox_labels = QtGui.QCheckBox("Labels")
        self.checkBox_labels.setChecked(True)
        self.mpl_toolbar.addWidget(self.comboBox_rotate)
        self.mpl_toolbar.addWidget(self.checkBox_labels)
        #add toolbar to tabs
        self.verticalLayout.addWidget(self.mpl_toolbar)
        
        
        
        #Plot initial zero spot
        self.Plot.plot(0,0, linestyle = '', marker='o', markersize = 10, color = 'black')
        self.Plot.set_xlim([-5,5])
        self.Plot.set_ylim([-5,5])
        #self.Plot.annotate('0 0 0', xy = (0,0), xytext=(0,10),textcoords = 'offset points', ha = 'center', va = 'bottom',
        #bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.01))
        
        
        #Initialize Metric tensor Tables
        self.Gtable_size = (185,195)
        self.Gtable = TableWidget(self.Gwidget)
        self.Gtable.resize(self.Gtable_size[0],self.Gtable_size[1])
        self.G_inv_table = TableWidget(self.Gwidget_inv)
        self.G_inv_table.resize(self.Gtable_size[0],self.Gtable_size[1])
        self.Gtable.setData(np.eye(3))
        self.G_inv_table.setData(np.eye(3))
        for i in range(3):
            self.Gtable.setColumnWidth(i,self.Gtable_size[0]/4)
            self.Gtable.setRowHeight(i,self.Gtable_size[1]/3.5)
            self.G_inv_table.setColumnWidth(i,self.Gtable_size[0]/3.35)
            self.G_inv_table.setRowHeight(i,self.Gtable_size[1]/3.5)
        
        self.a = 1; self.b=1; self.c=1
        
        #Initialize parameter tables
        self.param_table_size = (185,195)
        self.Gparam_table = TableWidget(self.Gparams)
        self.Gparam_inv_table = TableWidget(self.Gparams_inv)
        self.Gparam_table.resize(self.param_table_size[0],self.param_table_size[1])
        self.Gparam_inv_table.resize(self.param_table_size[0],self.param_table_size[1])
        initdat = np.transpose(np.array([[1,1,1,90,90,90]]))
        self.Gparam_table.setData(initdat)
        self.Gparam_inv_table.setData(initdat)
        self.Gparam_table.setHorizontalHeaderLabels(['Parameters'])
        self.Gparam_inv_table.setHorizontalHeaderLabels(['Parameters'])
        self.Gparam_table.setVerticalHeaderLabels([u'a',u'b',u'c',u'\u03B1',u'\u03B2',u'\u03B3'])
        self.Gparam_inv_table.setVerticalHeaderLabels([u'a*',u'b*',u'c*',u'\u03B1*',u'\u03B2*',u'\u03B3*'])
        for i in range(0,6):
            self.Gparam_table.setColumnWidth(i,self.param_table_size[0])
            self.Gparam_table.setRowHeight(i,self.param_table_size[0]/6.7)
            self.Gparam_inv_table.setColumnWidth(i,self.param_table_size[0])
            self.Gparam_inv_table.setRowHeight(i,self.param_table_size[0]/6.7)
        
        #D-spacing table
        self.dspace_table_size = (261,581)
        self.dspace_table = TableWidget(self.dSpace_table)
        self.dspace_table.resize(self.dspace_table_size[0],self.dspace_table_size[1])
        self.dspace_table.setData(np.array([[0,0,0,0]]))
        self.dspace_table.setHorizontalHeaderLabels(['d-space','h','k','l'])
        self.dspace_table.setColumnWidth(0,80)
        for i in range(1,4):
            self.dspace_table.setColumnWidth(i,47)
        
        # Set miller indices
        self.miller_indices = [str(x) for x in range(-6,7)]
        self.comboBox_hmin.addItems(self.miller_indices)
        self.comboBox_kmin.addItems(self.miller_indices)
        self.comboBox_lmin.addItems(self.miller_indices)
        self.comboBox_hmin.setCurrentIndex(4)
        self.comboBox_kmin.setCurrentIndex(4)
        self.comboBox_lmin.setCurrentIndex(4)
        # Miller max indices set to be 1 greater than selected min index
        self.comboBox_hmax.addItems(self.miller_indices)
        self.comboBox_kmax.addItems(self.miller_indices)
        self.comboBox_lmax.addItems(self.miller_indices)
        #self.setMillerMax_h()
        #self.setMillerMax_k()
        #self.setMillerMax_l()
        self.comboBox_hmax.setCurrentIndex(8)
        self.comboBox_kmax.setCurrentIndex(8)
        self.comboBox_lmax.setCurrentIndex(8)
        
        #Set zone axis parameters
        #by default set as [0 0 1]
        zone_indices = [str(x) for x in range(-5,6)]
        self.comboBox_u.addItems(zone_indices)
        self.comboBox_v.addItems(zone_indices)
        self.comboBox_w.addItems(zone_indices)
        self.comboBox_u.setCurrentIndex(5)
        self.comboBox_v.setCurrentIndex(5)
        self.comboBox_w.setCurrentIndex(6)
        
        #set calculator comboboxes
        self.comboBox_h1.addItems(self.miller_indices)
        self.comboBox_h2.addItems(self.miller_indices)
        self.comboBox_k1.addItems(self.miller_indices)
        self.comboBox_k2.addItems(self.miller_indices)
        self.comboBox_l1.addItems(self.miller_indices)
        self.comboBox_l2.addItems(self.miller_indices)
        self.comboBox_h1.setCurrentIndex(7)
        self.comboBox_h2.setCurrentIndex(8)
        self.comboBox_k1.setCurrentIndex(6)
        self.comboBox_k2.setCurrentIndex(6)
        self.comboBox_l1.setCurrentIndex(6)
        self.comboBox_l2.setCurrentIndex(6)
        
        #Initialize mineral database combobox
        self.setMineralList()
        
        #Initialize rotation of diffraction pattern.
        #Will only offer 0,90,180,270 degrees
        rotate_items = ['-180','-150','-120','-90','-60','-30','0','30','60','90','120','150','180']
        self.comboBox_rotate.addItems(rotate_items)
        self.comboBox_rotate.setCurrentIndex(6) #zero by default
        
        
        #get values in energy, cam legnth, cam const. combo boxes
        self.spinBox_beamenergy.setValue(int(self.common.beamenergy))
        self.spinBox_camlength.setValue(int(self.common.camlength))
        self.doubleSpinBox_camconst.setValue(self.common.camconst)
        
        #Initialize signals and slots
        #This needs to go here after setting Miller indices
        #When initializing, it runs Recalculate to do metric tensor and d-spacings
        #must go before setting crystal types, but after setting all of the combo boxes
        #combo boxes recalculate each time their index changes once the signals/slots set up
        #if signals/slots placed before, will recalc d-spacings every time you initialize a combobox value
        self.signals_slots()
        
        # Set crystal type combo box items:
        self.crystaltypes = ['Cubic','Tetragonal','Orthorhombic','Trigonal', 'Hexagonal','Monoclinic','Triclinic']
        self.comboBox_crystaltype.addItems(self.crystaltypes)
        
        #Redo some labels in unicode/greek characters
        self.label_alpha.setText(u'\u03B1')
        self.label_beta.setText(u'\u03B2')
        self.label_gamma.setText(u'\u03B3')
        self.label_dist_recip.setText(u'Reciprocal Distance (\u212B\u207B\u00B9 )')
        self.label_dist_real.setText(u'Real Distance (\u212B)')
        self.label_dist_film.setText(u'Film Distance (cm)')
        self.label_angle.setText(u'Angle (\u00B0)')
        v = self.version.split('.')
        pv = v[0] + '.' + v[1] #only major/minor versions. not bugfixes
        self.label_pyLATTICE.setText(u'pyLATTICE %s' % pv)
    
        #initialize popup IPython console
        #can interact with specific data
        self.initIPython()
        
    @QtCore.pyqtSlot(str,str,str,str)
    def on_distances_sent(self,recip_d, real_d, film_d, angle):
        self.lineEdit_recip_2.setText(recip_d)
        self.lineEdit_real_2.setText(real_d)
        self.lineEdit_film_2.setText(film_d)
        self.lineEdit_angle_3.setText(angle)
    
    def Recalculate(self):
        """Run MetricTensor() and D_Spacigns().  For use when slider hasn't changed"""
        self.MetricTensor()
        self.D_Spacings()
        
    def ReplotDiffraction(self):
        self.Recalculate()
        try:        
            self.PlotDiffraction()
        except UnboundLocalError:
            pass
    
#    def Print(self):
#        """test print fn"""
#        print(self.comboBox_spacegroup.currentIndex())
    
    def signals_slots(self):
        """All of the signals and slots not in .ui file"""
        #Testing
        #QtCore.QObject.connect(self.command_Wulff, QtCore.SIGNAL(_fromUtf8("clicked()")),WULFF)
        
        
        ### Menu actions
        QtCore.QObject.connect(self.actionClose, QtCore.SIGNAL(_fromUtf8("triggered()")), self.close)
        QtCore.QObject.connect(self.actionAbout, QtCore.SIGNAL(_fromUtf8("triggered()")), self.About)
        QtCore.QObject.connect(self.actionHow_to, QtCore.SIGNAL(_fromUtf8("triggered()")), self.HowTo)
        QtCore.QObject.connect(self.actionSave_D_spacings, QtCore.SIGNAL(_fromUtf8("triggered()")), self.SaveDSpace)
        QtCore.QObject.connect(self.actionRemove_DB_Minerals, QtCore.SIGNAL(_fromUtf8("triggered()")), self.removeMinerals)
        QtCore.QObject.connect(self.actionSave_Mineral_Database, QtCore.SIGNAL(_fromUtf8("triggered()")), self.SaveMineralDB)
        QtCore.QObject.connect(self.actionLoad_Mineral_Database, QtCore.SIGNAL(_fromUtf8("triggered()")), self.LoadMineralDB)
        QtCore.QObject.connect(self.actionAppendMineral, QtCore.SIGNAL(_fromUtf8("triggered()")), self.AppendMineral)
        QtCore.QObject.connect(self.actionIPython_Console, QtCore.SIGNAL(_fromUtf8("triggered()")), self.IPY)
        
        ### Command buttons
        QtCore.QObject.connect(self.command_Plot, QtCore.SIGNAL(_fromUtf8("clicked()")),self.PlotDiffraction)
        QtCore.QObject.connect(self.command_recalculate, QtCore.SIGNAL(_fromUtf8("clicked()")),self.Recalculate)
        #QtCore.QObject.connect(self.command_Wulff, QtCore.SIGNAL(_fromUtf8("clicked()")),self.updateIPY)
        
        ### crystal and cell type actions
        QtCore.QObject.connect(self.comboBox_crystaltype, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(QString)")), self.setCellType)
        QtCore.QObject.connect(self.comboBox_celltype, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(QString)")), self.setConditions)
        QtCore.QObject.connect(self.spinBox_spacegroup, QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), self.SpaceGroupLookup)
        QtCore.QObject.connect(self.checkBox_obverse, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.D_Spacings)
        QtCore.QObject.connect(self.comboBox_mineraldb, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(QString)")), self.setMineral)
        #QtCore.QObject.connect(self.comboBox_spacegroup, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(QString)")), self.D_Spacings)
        
        ### Navigation Toolbar buttons
        QtCore.QObject.connect(self.comboBox_rotate, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.PlotDiffraction)
        QtCore.QObject.connect(self.checkBox_labels, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.PlotDiffraction) #labels checkbox
        
        ### Checkboxes and Miller indices
        QtCore.QObject.connect(self.checkBox_samemin, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.sameMin)
        QtCore.QObject.connect(self.checkBox_samemax, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.sameMax)
        QtCore.QObject.connect(self.comboBox_hmin, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.comboBox_kmin,QtCore.SLOT(_fromUtf8("setCurrentIndex(int)")))
        QtCore.QObject.connect(self.comboBox_kmin, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.comboBox_lmin,QtCore.SLOT(_fromUtf8("setCurrentIndex(int)")))
        QtCore.QObject.connect(self.comboBox_lmin, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.comboBox_hmin,QtCore.SLOT(_fromUtf8("setCurrentIndex(int)")))
        QtCore.QObject.connect(self.comboBox_hmax, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.comboBox_kmax,QtCore.SLOT(_fromUtf8("setCurrentIndex(int)")))
        QtCore.QObject.connect(self.comboBox_kmax, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.comboBox_lmax,QtCore.SLOT(_fromUtf8("setCurrentIndex(int)")))
        QtCore.QObject.connect(self.comboBox_lmax, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.comboBox_hmax,QtCore.SLOT(_fromUtf8("setCurrentIndex(int)")))
        QtCore.QObject.connect(self.checkBox_showforbidden, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.PlotDiffraction)
        
        ### Sliders/spin boxes: lattice parameters
        QtCore.QObject.connect(self.hSlider_a, QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), self.slider_to_spindouble)
        QtCore.QObject.connect(self.hSlider_b, QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), self.slider_to_spindouble)
        QtCore.QObject.connect(self.hSlider_c, QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), self.slider_to_spindouble)
        QtCore.QObject.connect(self.hSlider_a, QtCore.SIGNAL(_fromUtf8("sliderReleased()")), self.D_Spacings)
        QtCore.QObject.connect(self.hSlider_b, QtCore.SIGNAL(_fromUtf8("sliderReleased()")), self.D_Spacings)
        QtCore.QObject.connect(self.hSlider_c, QtCore.SIGNAL(_fromUtf8("sliderReleased()")), self.D_Spacings)
        QtCore.QObject.connect(self.doubleSpinBox_a, QtCore.SIGNAL(_fromUtf8("valueChanged(double)")), self.spindouble_to_slider)
        QtCore.QObject.connect(self.doubleSpinBox_b, QtCore.SIGNAL(_fromUtf8("valueChanged(double)")), self.spindouble_to_slider)
        QtCore.QObject.connect(self.doubleSpinBox_c, QtCore.SIGNAL(_fromUtf8("valueChanged(double)")), self.spindouble_to_slider)
        QtCore.QObject.connect(self.doubleSpinBox_a, QtCore.SIGNAL(_fromUtf8("valueChanged(double)")), self.MetricTensor)
        QtCore.QObject.connect(self.doubleSpinBox_b, QtCore.SIGNAL(_fromUtf8("valueChanged(double)")), self.MetricTensor)
        QtCore.QObject.connect(self.doubleSpinBox_c, QtCore.SIGNAL(_fromUtf8("valueChanged(double)")), self.MetricTensor)
        #QtCore.QObject.connect(self.doubleSpinBox_a, QtCore.SIGNAL(_fromUtf8("valueChanged(double)")), self.D_Spacings)
        #QtCore.QObject.connect(self.doubleSpinBox_b, QtCore.SIGNAL(_fromUtf8("valueChanged(double)")), self.D_Spacings)
        #QtCore.QObject.connect(self.doubleSpinBox_c, QtCore.SIGNAL(_fromUtf8("valueChanged(double)")), self.D_Spacings)
        QtCore.QObject.connect(self.hSlider_alpha, QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), self.MetricTensor)
        QtCore.QObject.connect(self.hSlider_beta, QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), self.MetricTensor)
        QtCore.QObject.connect(self.hSlider_gamma, QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), self.MetricTensor)
        QtCore.QObject.connect(self.hSlider_alpha, QtCore.SIGNAL(_fromUtf8("sliderReleased()")), self.D_Spacings)
        QtCore.QObject.connect(self.hSlider_beta, QtCore.SIGNAL(_fromUtf8("sliderReleased()")), self.D_Spacings)
        QtCore.QObject.connect(self.hSlider_gamma, QtCore.SIGNAL(_fromUtf8("sliderReleased()")), self.D_Spacings)
        
        #Spinboxes beam energy, cam length, camconst
        QtCore.QObject.connect(self.spinBox_beamenergy,QtCore.SIGNAL(_fromUtf8("valueChanged(int)")),self.update_common)
        QtCore.QObject.connect(self.spinBox_camlength,QtCore.SIGNAL(_fromUtf8("valueChanged(int)")),self.update_common)
        QtCore.QObject.connect(self.doubleSpinBox_camconst,QtCore.SIGNAL(_fromUtf8("valueChanged(double)")),self.update_common)
        
        #Instances to recalculate metric tensor and d-spacings
        #only enable these once you get miller maxes sorted out so they don't change
        QtCore.QObject.connect(self.checkBox_zoneaxis, QtCore.SIGNAL(_fromUtf8("toggled(bool)")),self.DiffWidget, QtCore.SLOT(_fromUtf8("setEnabled(bool)")))
        QtCore.QObject.connect(self.comboBox_u, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.ReplotDiffraction)
        QtCore.QObject.connect(self.comboBox_v, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.ReplotDiffraction)
        QtCore.QObject.connect(self.comboBox_w, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.ReplotDiffraction)
        QtCore.QObject.connect(self.comboBox_hmax, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.D_Spacings)
        QtCore.QObject.connect(self.comboBox_hmin, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.D_Spacings)
        #QtCore.QObject.connect(self.checkBox_labels, QtCore.SIGNAL(_fromUtf8("toggled(bool)")),self.UpdatePlot)
        #QtCore.QObject.connect(self.comboBox_hmax, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.TempMax)
        #QtCore.QObject.connect(self.comboBox_kmax, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.TempMax)
        #QtCore.QObject.connect(self.comboBox_lmax, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.TempMax)
        #QtCore.QObject.connect(self.comboBox_hmin, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.Recalculate)
        #QtCore.QObject.connect(self.comboBox_kmin, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.Recalculate)
        #QtCore.QObject.connect(self.comboBox_lmin, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.Recalculate)
        #QtCore.QObject.connect(self.comboBox_w, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.ReplotDiffraction)
        
        #Calculator Tab
        QtCore.QObject.connect(self.checkBox_normals, QtCore.SIGNAL(_fromUtf8("toggled(bool)")),self.CalcLabels)
        QtCore.QObject.connect(self.command_angle, QtCore.SIGNAL(_fromUtf8("clicked()")),self.Calculator)
        
    def initIPython(self):
        """Initialize IPython console from which the user can interact with data/files"""
        self.ipywidget = IPythonConsole()
        banner = """Welcome to the IPython Console.
You are here to interact with pyLATTICE data.
Use the 'whos' command for information.

Imported packages include: numpy as np; pandas as pd; pyplot as plt
\n"""
        self.ipyConsole = QIPythonWidget(customBanner=banner)
        self.ipywidget.layout.addWidget(self.ipyConsole)
        self.ipyConsole.executeCommand('import numpy as np;import pandas as pd;import matplotlib.pyplot as plt')

        #data to interact with
        self.updateIPY()
        self.ipyConsole.printText("The variables %s are available." % ', '.join(list(self.ipyvars.keys()))) 
        
        
    
    def IPY(self):
        self.ipywidget.show()
    
    def updateIPY(self):
        self.ipyvars = {"DSpaces":self.DSpaces,
                     "MTensor":self.G,
                     "MTensor_inv":self.G_inv}
        self.ipyConsole.pushVariables(self.ipyvars)
        
    def update_common(self):
        self.common.beamenergy = self.spinBox_beamenergy.value()
        self.common.camlength = self.spinBox_camlength.value()
        self.common.camconst = self.doubleSpinBox_camconst.value()
        self.common.wavelength = self.common.Wavelength(self.common.beamenergy)
    
    def slider_to_spindouble(self,slider):
        """Sliders only send/receive int data.  Converts int to double by dividing by 100."""
        if self.hSlider_a.isSliderDown():
            self.a = self.hSlider_a.value() / 100
            self.doubleSpinBox_a.setValue(self.a)
        elif self.hSlider_b.isSliderDown():
            self.b = self.hSlider_b.value() / 100
            self.doubleSpinBox_b.setValue(self.b)
        elif self.hSlider_c.isSliderDown():
            self.c = self.hSlider_c.value() / 100
            self.doubleSpinBox_c.setValue(self.c)
        
            
    def spindouble_to_slider(self,spinbox):
        """Converts spindouble entry into int for slider (multiply by 100)"""
        #There may be some redundancy in the connections setting values.
        #hopefully this does not slow the program down.
        #without these, some aspect often lags and gives the wrong value
        if self.comboBox_crystaltype.currentText() == 'Cubic':
            self.a = self.doubleSpinBox_a.value()
            self.hSlider_a.setValue(self.a * 100)
            self.hSlider_b.setValue(self.a * 100);self.doubleSpinBox_b.setValue(self.a)
            self.hSlider_c.setValue(self.a * 100);self.doubleSpinBox_c.setValue(self.a)
        elif self.comboBox_crystaltype.currentText() == 'Tetragonal':
            self.a = self.doubleSpinBox_a.value()
            self.hSlider_a.setValue(self.a * 100)
            self.hSlider_b.setValue(self.a * 100); self.doubleSpinBox_b.setValue(self.a)
        elif self.comboBox_crystaltype.currentText() == 'Trigonal':
            self.a = self.doubleSpinBox_a.value()
            self.hSlider_a.setValue(self.a * 100)
            self.hSlider_b.setValue(self.a * 100); self.doubleSpinBox_b.setValue(self.a)
        elif self.comboBox_crystaltype.currentText() == 'Hexagonal':
            self.a = self.doubleSpinBox_a.value()
            self.hSlider_a.setValue(self.a * 100)
            self.hSlider_b.setValue(self.a * 100); self.doubleSpinBox_b.setValue(self.a)
        else:
            self.a = self.doubleSpinBox_a.value()
            self.hSlider_a.setValue(self.a * 100)
            self.b = self.doubleSpinBox_b.value()
            self.hSlider_b.setValue(self.b * 100)
            self.c = self.doubleSpinBox_c.value()
            self.hSlider_c.setValue(self.c * 100)
        
    def setMillerMax_h(self):
        """Sets the items available for the max miller indices to include everything greater than the selected min index"""

        self.miller_max_h = [str(x) for x in range(int(self.comboBox_hmin.currentText()) + 1,7)]
        self.comboBox_hmax.clear()
        self.comboBox_hmax.addItems(self.miller_max_h)

    def setMillerMax_k(self):
        """Sets the items available for the max miller indices to include everything greater than the selected min index"""
        self.miller_max_k = [str(x) for x in range(int(self.comboBox_kmin.currentText()) + 1,7)]
        self.comboBox_kmax.clear()
        self.comboBox_kmax.addItems(self.miller_max_k)
        
    def setMillerMax_l(self):
        """Sets the items available for the max miller indices to include everything greater than the selected min index"""
        self.miller_max_l = [str(x) for x in range(int(self.comboBox_lmin.currentText()) + 1,7)]
        self.comboBox_lmax.clear()
        self.comboBox_lmax.addItems(self.miller_max_l)
        
    def sameMin(self):
        if not self.checkBox_samemin.isChecked():
            #change to value_changed, not index changed.  lengths may be different if checkboxes aren't clicked
            QtCore.QObject.disconnect(self.comboBox_hmin, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.comboBox_kmin,QtCore.SLOT(_fromUtf8("setCurrentIndex(int)")))
            QtCore.QObject.disconnect(self.comboBox_kmin, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.comboBox_lmin,QtCore.SLOT(_fromUtf8("setCurrentIndex(int)")))
            QtCore.QObject.disconnect(self.comboBox_lmin, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.comboBox_hmin,QtCore.SLOT(_fromUtf8("setCurrentIndex(int)")))
        elif self.checkBox_samemin.isChecked(): 
            QtCore.QObject.connect(self.comboBox_hmin, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.comboBox_kmin,QtCore.SLOT(_fromUtf8("setCurrentIndex(int)")))
            QtCore.QObject.connect(self.comboBox_kmin, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.comboBox_lmin,QtCore.SLOT(_fromUtf8("setCurrentIndex(int)")))
            QtCore.QObject.connect(self.comboBox_lmin, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.comboBox_hmin,QtCore.SLOT(_fromUtf8("setCurrentIndex(int)")))
        
    def sameMax(self):
        if not self.checkBox_samemax.isChecked():
            QtCore.QObject.disconnect(self.comboBox_hmax, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.comboBox_kmax,QtCore.SLOT(_fromUtf8("setCurrentIndex(int)")))
            QtCore.QObject.disconnect(self.comboBox_kmax, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.comboBox_lmax,QtCore.SLOT(_fromUtf8("setCurrentIndex(int)")))
            QtCore.QObject.disconnect(self.comboBox_lmax, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.comboBox_hmax,QtCore.SLOT(_fromUtf8("setCurrentIndex(int)")))
        elif self.checkBox_samemax.isChecked(): 
            QtCore.QObject.connect(self.comboBox_hmax, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.comboBox_kmax,QtCore.SLOT(_fromUtf8("setCurrentIndex(int)")))
            QtCore.QObject.connect(self.comboBox_kmax, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.comboBox_lmax,QtCore.SLOT(_fromUtf8("setCurrentIndex(int)")))
            QtCore.QObject.connect(self.comboBox_lmax, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.comboBox_hmax,QtCore.SLOT(_fromUtf8("setCurrentIndex(int)")))
        
    def setMineral(self):
        i = self.comboBox_mineraldb.currentIndex()
        if i == 0:
            pass
        else:
            #disconnect d-space calculations till the end
            QtCore.QObject.disconnect(self.comboBox_crystaltype, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(QString)")), self.setCellType)
            QtCore.QObject.disconnect(self.comboBox_celltype, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(QString)")), self.setConditions)
            QtCore.QObject.disconnect(self.spinBox_spacegroup, QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), self.SpaceGroupLookup)

            m = self.mineraldb.loc[i]
            ind =  ['Cubic','Tetragonal','Orthorhombic','Trigonal','Hexagonal','Monoclinic','Triclinic'].index(m.Crystal)
            self.comboBox_crystaltype.setCurrentIndex(ind)
            self.setCellType()
            ind = self.celltypes.index(m.UnitCell)
            self.comboBox_celltype.setCurrentIndex(ind)            
            self.setConditions()
            ind = self.sgnumbers.index(m.SpaceGroup)
            self.comboBox_spacegroup.setCurrentIndex(ind)
            #now a,b,c paramters
            #print(self.sgnumbers)
            self.doubleSpinBox_a.setValue(m.a)
            self.a = m.a
            if not np.isnan(m.b):
                self.doubleSpinBox_b.setValue(m.b)
                self.b = m.b
            if not np.isnan(m.c):
                self.doubleSpinBox_c.setValue(m.c)
                self.c = m.c
            
            self.MetricTensor()
            #reconnect and calculate
            QtCore.QObject.connect(self.comboBox_crystaltype, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(QString)")), self.setCellType)
            QtCore.QObject.connect(self.comboBox_celltype, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(QString)")), self.setConditions)
            QtCore.QObject.connect(self.spinBox_spacegroup, QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), self.SpaceGroupLookup)
            
            self.D_Spacings()
    
    
    def setCellType(self):
        """Sets the unit cell possibilities based upon the crystal type selected"""
        self.comboBox_celltype.clear()
        self.comboBox_spacegroup.clear()
        self.celltypes = []
        
        
        if self.comboBox_crystaltype.currentText() == 'Cubic':
            self.celltypes = ['Primitive','Face Centered','Body Centered']
            self.length_label = u' a = b = c'
            self.label_lattice_equality.setText(self.length_label)
            
            self.hSlider_b.setDisabled(True); self.hSlider_c.setDisabled(True)
            self.doubleSpinBox_b.setDisabled(True); self.doubleSpinBox_c.setDisabled(True)
            self.angles_label = u' \u03B1 = \u03B2 = \u03B3 = 90°'
            self.label_angle_equality.setText(self.angles_label)
            self.alpha = 90; self.beta = 90; self.gamma = 90
            self.hSlider_alpha.setValue(self.alpha); self.hSlider_beta.setValue(self.beta); self.hSlider_gamma.setValue(self.gamma)
            #disable editing sliders and spinboxes
            self.hSlider_alpha.setDisabled(True); self.hSlider_beta.setDisabled(True); self.hSlider_gamma.setDisabled(True)
            self.spinBox_alpha.setDisabled(True); self.spinBox_beta.setDisabled(True); self.spinBox_gamma.setDisabled(True)
            
            
        elif self.comboBox_crystaltype.currentText() == 'Tetragonal':
            self.celltypes = ['Primitive','Body Centered']
            self.length_label = u' a = b ≠ c'
            self.label_lattice_equality.setText(self.length_label)
            self.hSlider_b.setDisabled(True); self.hSlider_c.setDisabled(False)
            self.doubleSpinBox_b.setDisabled(True); self.doubleSpinBox_c.setDisabled(False)
            
            self.angles_label = u' \u03B1 = \u03B2 = \u03B3 = 90°'
            self.label_angle_equality.setText(self.angles_label)
            self.alpha = 90; self.beta = 90; self.gamma = 90
            self.hSlider_alpha.setValue(self.alpha); self.hSlider_beta.setValue(self.beta); self.hSlider_gamma.setValue(self.gamma)
            #disable editing sliders and spinboxes
            self.hSlider_alpha.setDisabled(True); self.hSlider_beta.setDisabled(True); self.hSlider_gamma.setDisabled(True)
            self.spinBox_alpha.setDisabled(True); self.spinBox_beta.setDisabled(True); self.spinBox_gamma.setDisabled(True)
            
            
        elif self.comboBox_crystaltype.currentText() == 'Orthorhombic':
            self.celltypes = ['Primitive','Face Centered','Body Centered','(001) Base Centered','(100) Base Centered']
            self.length_label = u' a ≠ b ≠ c'
            self.label_lattice_equality.setText(self.length_label)
            self.hSlider_b.setDisabled(False); self.hSlider_c.setDisabled(False)
            self.doubleSpinBox_b.setDisabled(False); self.doubleSpinBox_c.setDisabled(False)
            self.angles_label = u' \u03B1 = \u03B2 = \u03B3 = 90°'
            self.label_angle_equality.setText(self.angles_label)
            self.alpha = 90; self.beta = 90; self.gamma = 90
            self.hSlider_alpha.setValue(self.alpha); self.hSlider_beta.setValue(self.beta); self.hSlider_gamma.setValue(self.gamma)
            #disable editing sliders and spinboxes
            self.hSlider_alpha.setDisabled(True); self.hSlider_beta.setDisabled(True); self.hSlider_gamma.setDisabled(True)
            self.spinBox_alpha.setDisabled(True); self.spinBox_beta.setDisabled(True); self.spinBox_gamma.setDisabled(True)
            
           
        elif self.comboBox_crystaltype.currentText() == 'Trigonal':
            self.celltypes = ['Primitive','Rhombohedral','Rhombohedral, Hexagonal Axes','Hexagonal']
            self.length_label = u' a = b ≠ c'
            self.label_lattice_equality.setText(self.length_label)
            self.hSlider_b.setDisabled(True); self.hSlider_c.setDisabled(False)
            self.doubleSpinBox_b.setDisabled(True); self.doubleSpinBox_c.setDisabled(False)
            self.angles_label = u' \u03B1 = \u03B2 = 90°, \u03B3 = 120°'
            self.label_angle_equality.setText(self.angles_label)
            self.alpha = 90; self.beta = 90; self.gamma = 120
            self.hSlider_alpha.setValue(self.alpha); self.hSlider_beta.setValue(self.beta); self.hSlider_gamma.setValue(self.gamma)
            #disable editing sliders and spinboxes
            self.hSlider_alpha.setDisabled(True); self.hSlider_beta.setDisabled(True); self.hSlider_gamma.setDisabled(True)
            self.spinBox_alpha.setDisabled(True); self.spinBox_beta.setDisabled(True); self.spinBox_gamma.setDisabled(True)
            
            
        elif self.comboBox_crystaltype.currentText() == 'Hexagonal':
            self.celltypes = ['Primitive']
            self.length_label = u' a = b ≠ c'
            self.label_lattice_equality.setText(self.length_label)
            self.hSlider_b.setDisabled(True); self.hSlider_c.setDisabled(False)
            self.doubleSpinBox_b.setDisabled(True); self.doubleSpinBox_c.setDisabled(False)
            self.angles_label = u' \u03B1 = \u03B2 = 90°, \u03B3 = 120°'
            self.label_angle_equality.setText(self.angles_label)
            self.alpha = 90; self.beta = 90; self.gamma = 120
            self.hSlider_alpha.setValue(self.alpha); self.hSlider_beta.setValue(self.beta); self.hSlider_gamma.setValue(self.gamma)
            #disable editing sliders and spinboxes
            self.hSlider_alpha.setDisabled(True); self.hSlider_beta.setDisabled(True); self.hSlider_gamma.setDisabled(True)
            self.spinBox_alpha.setDisabled(True); self.spinBox_beta.setDisabled(True); self.spinBox_gamma.setDisabled(True)
            
            
        elif self.comboBox_crystaltype.currentText() == 'Monoclinic':
            self.celltypes = ['Primitive','(001) Base Centered']
            self.length_label = u' a ≠ b ≠ c'
            self.label_lattice_equality.setText(self.length_label)
            self.hSlider_b.setDisabled(False); self.hSlider_c.setDisabled(False)
            self.doubleSpinBox_b.setDisabled(False); self.doubleSpinBox_c.setDisabled(False)
            self.angles_label = u' \u03B1 = \u03B3 = 90°'
            self.label_angle_equality.setText(self.angles_label)
            self.alpha = 90; self.beta = 90; self.gamma = 90
            self.hSlider_alpha.setValue(self.alpha); self.hSlider_beta.setValue(self.beta); self.hSlider_gamma.setValue(self.gamma)
            #disable editing sliders and spinboxes
            self.hSlider_alpha.setDisabled(True); self.hSlider_beta.setDisabled(True); self.hSlider_gamma.setDisabled(True)
            self.spinBox_alpha.setDisabled(True); self.spinBox_beta.setDisabled(True); self.spinBox_gamma.setDisabled(True)
            
            
        elif self.comboBox_crystaltype.currentText() == 'Triclinic':
            self.celltypes = ['Primitive']
            self.length_label = u' a ≠ b ≠ c'
            self.label_lattice_equality.setText(self.length_label)
            self.hSlider_b.setDisabled(False); self.hSlider_c.setDisabled(False)
            self.doubleSpinBox_b.setDisabled(False); self.doubleSpinBox_c.setDisabled(False)
            self.angles_label = u''
            self.label_angle_equality.setText(self.angles_label)
            #Enable editing sliders and spinboxes
            self.hSlider_alpha.setDisabled(False); self.hSlider_beta.setDisabled(False); self.hSlider_gamma.setDisabled(False)
            self.spinBox_alpha.setDisabled(False); self.spinBox_beta.setDisabled(False); self.spinBox_gamma.setDisabled(False)
        
        self.comboBox_celltype.addItems(self.celltypes)
        #self.Recalculate()
        
    def setConditions(self):
        """Sets conditions based upon which unit cell type is chosen.
        Store equations in strings and then evaluate and solve with eval()"""
        geom = self.comboBox_crystaltype.currentText()
        unit = self.comboBox_celltype.currentText()
        if unit in ['Rhombohedral','Rhombohedral, Hexagonal Axes']:
            self.checkBox_obverse.setDisabled(False)
        else:
            self.checkBox_obverse.setDisabled(True)
        try: #there is a loop I cant find where this tries to calculate conditions before unit cell type is set resulting in index error.
        #this simply supresses the error, as another pass is always fine.
            if unit in ['Rhombohedral, Hexagonal Axes','Hexagonal']:
                rhomhex=True
                self.conditions = np.unique(self.sghex[self.sghex['Unit Cell'] == unit]['Conditions'])[0]
            else:
                rhomhex=False
                self.conditions = np.unique(self.sg[self.sg['Unit Cell'] == unit]['Conditions'])[0] #grab individual condition b/c of repetition
            self.setSpaceGroups(geom,unit,rhomhex)
            #QtCore.QObject.disconnect(self.comboBox_spacegroup, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(QString)")), self.D_Spacings)
            self.comboBox_spacegroup.clear()
            self.comboBox_spacegroup.addItems(self.sgnumlist)
            #QtCore.QObject.connect(self.comboBox_spacegroup, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(QString)")), self.D_Spacings)
            self.Recalculate()
        except IndexError:
            pass
        
    def setSpaceGroups(self,geom,unit,rhomhex=False):
        """Sets the space group options based upon crystal geometry and unit cell type"""
        if rhomhex:
            sg = self.sghex
        elif not rhomhex:
            sg = self.sg
        
        self.sgnumbers = list(sg[(sg['Geometry'] == geom) & (sg['Unit Cell'] == unit)].index)
        self.sglist = list(sg.loc[self.sgnumbers,'Patterson'])
        self.sgnumlist = [str(x) + ':  ' + y for x,y in zip(self.sgnumbers,self.sglist)]


    def SpaceGroupConditions(self,number):
        """Looks up the space-group-specific allowed diffraction spots.
        number is the specific space group number to look up."""
        if not self.checkBox_spacegroup.isChecked():
            sg_conditions = 'True' 
            
        elif self.checkBox_spacegroup.isChecked():
            #make sure number is an integer
            #something is wrong with some FCC crystals
            number = int(number)
            unit = self.comboBox_celltype.currentText()
            if unit in ['Rhombohedral, Hexagonal Axes','Hexagonal']:
                sg = self.sghex
            else:
                sg = self.sg
            sg_conditions = sg.loc[number,'SG Conditions']
  
        return sg_conditions
         
    def SpaceGroupLookup(self):
        """Takes input from slider/spinbox and outputs sapcegroup info into text line"""
        index = self.spinBox_spacegroup.value()
        c = self.sg.loc[index,'Geometry']
        #u = self.sg.loc[index,'Unit Cell']
        sg = self.sg.loc[index,'Patterson']
        text = ': '.join([c,sg])
        self.label_spacegrouplookup.setText(text)
        
        
    def MetricTensor(self):
        """Calculate and show G, the metric tensor, and G*, the inverse metric tensor.
        Also call function that outputs parameters into tables."""
        
        self.G = np.zeros([3,3])
        #self.G_inv 
        #remember, indices start at 0
        #metric tensor is axially symmetric
        self.a = self.doubleSpinBox_a.value()
        self.b = self.doubleSpinBox_b.value()
        self.c = self.doubleSpinBox_c.value()
        self.G[0,0] = self.a**2
        self.G[0,1] = round(self.a * self.b * np.cos(np.radians(self.spinBox_gamma.value())),6)
        self.G[1,0] = self.G[0,1]
        self.G[1,1] = self.b**2
        self.G[0,2] = round(self.a * self.c * np.cos(np.radians(self.spinBox_beta.value())),6)
        self.G[2,0] = self.G[0,2]
        self.G[2,2] = self.doubleSpinBox_c.value()**2
        self.G[1,2] = round(self.c * self.b * np.cos(np.radians(self.spinBox_alpha.value())),6)
        self.G[2,1] = self.G[1,2]
        # calc G inverse, G*
        self.G_inv = np.linalg.inv(self.G)
        self.Gtable.setData(self.G)
        #self.Gtable.resizeColumnsToContents()
        self.G_inv_table.setData(self.G_inv)
        #self.G_inv_table.resizeColumnsToContents()
        for i in range(0,3):
            self.Gtable.setColumnWidth(i,self.Gtable_size[0]/3.35)
            self.Gtable.setRowHeight(i,self.Gtable_size[1]/3.5)
            self.G_inv_table.setColumnWidth(i,self.Gtable_size[0]/3.35)
            self.G_inv_table.setRowHeight(i,self.Gtable_size[1]/3.5)
        
        self.Parameters()
        

    def Parameters(self):
        """Grabs current parameters and outputs them in tables.
        Calculates reciprocal lattice parameters as well.
        Must make it deal with complex numbers, but really only necessary for Triclinic..."""
        self.parameters_direct = np.transpose(np.array([[self.doubleSpinBox_a.value(),self.doubleSpinBox_b.value(),self.doubleSpinBox_c.value(),self.spinBox_alpha.value(),self.spinBox_beta.value(),self.spinBox_gamma.value()]]))
        self.astar = np.sqrt(self.G_inv[0,0]); self.bstar = np.sqrt(self.G_inv[1,1]); self.cstar = np.sqrt(self.G_inv[2,2])
        self.gammastar = np.arccos(self.G_inv[0,1] / (self.astar * self.bstar))*180 / np.pi
        self.betastar = np.arccos(self.G_inv[0,2] / (self.astar * self.cstar))*180 / np.pi
        self.alphastar = np.arccos(self.G_inv[1,2] / (self.cstar * self.bstar))*180 / np.pi
        self.parameters_reciprocal = np.transpose(np.array([[self.astar,self.bstar,self.cstar,self.alphastar,self.betastar,self.gammastar]]))
        self.Gparam_table.setData(self.parameters_direct)
        self.Gparam_inv_table.setData(self.parameters_reciprocal)
        self.Gparam_table.setHorizontalHeaderLabels(['Parameters'])
        self.Gparam_inv_table.setHorizontalHeaderLabels(['Parameters'])
        self.Gparam_table.setVerticalHeaderLabels([u'a',u'b',u'c',u'\u03B1',u'\u03B2',u'\u03B3'])
        self.Gparam_inv_table.setVerticalHeaderLabels([u'a*',u'b*',u'c*',u'\u03B1*',u'\u03B2*',u'\u03B3*'])
        for i in range(0,6):
            self.Gparam_table.setColumnWidth(i,self.param_table_size[0])
            self.Gparam_table.setRowHeight(i,self.param_table_size[0]/6.7)
            self.Gparam_inv_table.setColumnWidth(i,self.param_table_size[0])
            self.Gparam_inv_table.setRowHeight(i,self.param_table_size[0]/6.7)
            
    def D_Spacings(self):
        """Calculates D-spacings using the metric tensor and places them in a table (sorted?)"""
        #grab spacegroup conditions
        #multiple different spacegroup conditions. e.g. eval('h==1 or k==1') returns a True if on is satisfied
        
        #add all conditions together into one string
        #full_conditions = self.conditions + ' and ' + sg_conditions
        if self.checkBox_zoneaxis.isChecked():

            try:
                self.u = int(self.comboBox_u.currentText())
            except ValueError:
                self.u = 0
            try:
                self.v = int(self.comboBox_v.currentText())
            except ValueError:
                self.v = 0
            try:
                self.w = int(self.comboBox_w.currentText())
            except ValueError:
                self.w = 0
            
            #set "q" for rhombohedral obserse/reverse
            
            if self.checkBox_obverse.isChecked():
                q = 1
            elif not self.checkBox_obverse.isChecked():
                q = -1
            else:
                q = 0
            
            #make pandas dataframe with multiindex h,k,l
            #reinitialize dataframe
            self.DSpaces = pd.DataFrame(columns = ['d-space','h','k','l'])
            self.Forbidden = pd.DataFrame(columns = ['d-space','h','k','l'])
            #maybe implement masking instead of loops
            hmin = int(self.comboBox_hmin.currentText())
            hmax = int(self.comboBox_hmax.currentText())
            kmin = int(self.comboBox_kmin.currentText())
            kmax = int(self.comboBox_kmax.currentText())
            lmin = int(self.comboBox_lmin.currentText())
            lmax = int(self.comboBox_lmax.currentText())
            
            gen_conditions = str(self.conditions)
            
            #needs to deal with possibility of conditional special statements, will update dspace.pyx
            #first calculate all general conditions
            self.DSpaces = DSpace(self.G_inv,self.u,self.v,self.w,hmin,hmax,kmin,kmax,lmin,lmax,gen_conditions,q)
            
            #now deal with special spacegroup conditions by removing invalid spots
            sg_conditions = self.SpaceGroupConditions(self.sgnumbers[self.comboBox_spacegroup.currentIndex()])
            self.DSpaces = self.RemoveForbidden(self.DSpaces,sg_conditions)
            
            #sort in descending Dspace order, then by h values, then k, then l...
            self.DSpaces.sort(columns=['d-space','h','k','l'],ascending=False,inplace=True)
            #reset indices for convenience later
            self.DSpaces.index = [x for x in range(len(self.DSpaces))] 
            self.common.DSpaces = self.DSpaces #update DSpaces
            
            
            self.dspace_table.setData(self.DSpaces)
            self.dspace_table.setColumnWidth(0,80) #make d-space column a bit wider
            for i in range(1,4):
                self.dspace_table.setColumnWidth(i,45)
            
        elif not self.checkBox_zoneaxis.isChecked():
            pass
        
        try:
            self.updateIPY()
        except AttributeError: #first go round ipython console hasn't been initialized yet
            pass

    def RemoveForbidden(self,d,sgconditions):
        #h = d['h']; k = d['k']; l = d['l']
        f = pd.DataFrame(columns = ['d-space','h','k','l'])
        try:
            if eval(sgconditions):
                return(d)
        except SyntaxError: #if sgconditions not 'True'
            #d[(h==k) & ~(l%2==0)]
            #d = d.drop(r.index)
            #split multiple conditions up
            conds = sgconditions.split(';')
            for c in conds: #these should be if:then statements, so remove the if:~thens
                c = c.strip()
                if not c.startswith('if'):
                    r = d[eval(c)]
                    d = d.drop(r.index)
                    
                else:
                    c = c.lstrip('if').strip()
                    iff, then = c.split(':') #eval doesnt care about spaces
                    r = d[eval('(' + iff + ')& ~(' + then + ')')]
                    d = d.drop(r.index)
                f = pd.concat([f,r])
            
            f.sort(columns=['d-space','h','k','l'],ascending=False,inplace=True)
            f.index = [x for x in range(len(f))]
            self.common.Forbidden = f
            self.Forbidden = self.common.Forbidden
            return(d)

    def setMineralList(self):
        self.comboBox_mineraldb.clear()
        self.minlist = list(self.mineraldb['Chemical'] + ': ' + self.mineraldb['Name'])
        self.comboBox_mineraldb.addItems(self.minlist)
        
    
    def removeMinerals(self):
        QtCore.QObject.disconnect(self.comboBox_mineraldb, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(QString)")), self.setMineral)
        mindiag = MineralListDialog()
        model = QtGui.QStandardItemModel(mindiag.listView)
        #mindiag.buttonBox.accepted.connect(mindiag.accept)
        #mindiag.buttonBox.rejected.connect(mindiag.reject)
        for mineral in self.minlist[1:]:
            item = QtGui.QStandardItem(mineral)
            item.setCheckable(True)
            item.setEditable(False)
            model.appendRow(item)
        mindiag.listView.setModel(model)
        if mindiag.exec_():
            i=1
            l=[]
            while model.item(i):
                if model.item(i).checkState():
                    l.append(i)
                i += 1
            self.mineraldb = self.mineraldb.drop(self.mineraldb.index[l])
            self.mineraldb.index = list(range(len(self.mineraldb)))
            self.setMineralList()
            QtCore.QObject.connect(self.comboBox_mineraldb, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(QString)")), self.setMineral)
            
            
    def AppendMineral(self):
        QtCore.QObject.disconnect(self.comboBox_mineraldb, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(QString)")), self.setMineral)
        dial = NewMineralDialog()
        if dial.exec_():
            name = dial.lineEdit_name.text()
            sym = dial.lineEdit_sym.text()
            if name == '':
                name = 'Mineral'
            if sym == '':
                sym = 'XX'
            params = {'Name':name, 'Chemical':sym,
                      'Crystal':self.comboBox_crystaltype.currentText(),
                      'UnitCell':self.comboBox_celltype.currentText(),
                      'SpaceGroup':int(self.comboBox_spacegroup.currentText().split(':')[0]),
                      'a':self.doubleSpinBox_a.value(),
                      'b':self.doubleSpinBox_b.value(),
                      'c':self.doubleSpinBox_c.value()}
            self.mineraldb = self.mineraldb.append(params,ignore_index=True)
        
            self.setMineralList()
        QtCore.QObject.connect(self.comboBox_mineraldb, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(QString)")), self.setMineral)
        
    def SaveDSpace(self):
        self.Save(self.DSpaces)
        
    def SaveMineralDB(self):
        self.Save(self.mineraldb)
    
    def LoadMineralDB(self):
        QtCore.QObject.disconnect(self.comboBox_mineraldb, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(QString)")), self.setMineral)
        ftypes = 'HDF (*.h5);;CSV (*.csv);;Excel (*.xlsx)'
        fname,ffilter = QtGui.QFileDialog.getOpenFileNameAndFilter(self,caption='Load Mineral Database',directory=self.common.path,filter=ftypes)
        fname = str(fname)
        ffilter=str(ffilter)
        #print(fname,ffilter)
        name, ext = os.path.splitext(fname)
        self.common.path = os.path.dirname(fname)
        if ffilter.startswith('HDF'):
            item = pd.read_hdf(name + '.h5','table')
        elif ffilter.startswith('CSV'):
            item = pd.read_csv(name + '.csv',sep=',')
        elif ffilter.startswith('Excel'): #allow for different excel formats
            
            sheetname,ok = QtGui.QInputDialog.getText(self,'Input Sheetname','Sheetname')
            if ok and sheetname != '':
                if ext == '.xlsx' or ext == '':
                    item = pd.read_excel(name + '.xlsx',str(sheetname))
                elif ext == '.xls':
                    item = pd.read_excel(name + '.xls',str(sheetname))
                self.mineraldb = item
            else:
                QtGui.QMessageBox.information(self, "Warning!", 'You must specify a sheet name!')
        self.setMineralList()
        QtCore.QObject.connect(self.comboBox_mineraldb, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(QString)")), self.setMineral)
        
    def Save(self,item):
        #item should be pandas dataframe object
        ftypes = 'HDF (*.h5);;CSV (*.csv);;Excel (*.xlsx)'
        fname,ffilter = QtGui.QFileDialog.getSaveFileNameAndFilter(self,caption='Save D-Spacings',directory=self.common.path,filter=ftypes)
        fname = str(fname)
        ffilter=str(ffilter)
        #print(fname,ffilter)
        name, ext = os.path.splitext(fname)
        self.common.path = os.path.dirname(fname)
        print(name + ext)
        if ffilter.startswith('HDF'):
            item.to_hdf(name + '.h5','table')
        elif ffilter.startswith('CSV'):
            item.to_csv(name + '.csv',sep=',')
        elif ffilter.startswith('Excel'): #allow for different excel formats
            if ext == '.xlsx' or ext == '':
                item.to_excel(name + '.xlsx')
            elif ext == '.xls':
                item.to_excel(name + '.xls')
                
################################################################################
############################### Plotting #######################################
################################################################################   
    def PlotDiffraction(self):
        """Plots the current list of spots and d-spacings.
        For each point in self.DSpaces [d-space,h,k,l], determines anlges for plotting."""
        #initialize plot with center spot only
        self.Plot.clear()
        self.common.x2 = False
        self.Plot.set_xlabel(u'Distance (\u212B\u207B\u00B9)')#angstrom^-1
        self.Plot.set_ylabel(u'Distance (\u212B\u207B\u00B9)')
        
        #get values in energy, cam legnth, cam const. combo boxes
        self.energy = self.spinBox_beamenergy.value()
        self.camlength = self.spinBox_camlength.value()
        self.camconst = self.doubleSpinBox_camconst.value()
        
        #self.Plot.plot(0,0, linestyle = '', marker='o', markersize = 10, color = 'black',picker=5, label = u'0 0 0')
        #add some labels
        if self.checkBox_labels.isChecked() == True:
            #center spot
            #self.Plot.annotate(u'0 0 0', xy = (0,0), xytext=(0,10),textcoords = 'offset points', ha = 'center', va = 'bottom',
            #                   bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.01))
            #add crystal structure information in an annotation
            #grab current values
            self.a = self.doubleSpinBox_a.value(); self.b = self.doubleSpinBox_b.value(); self.c = self.doubleSpinBox_c.value()
            alph = self.spinBox_alpha.value(); beta = self.spinBox_beta.value(); gam = self.spinBox_gamma.value()
            plot_label = r'''%s: %s; a = %.2f, b = %.2f, c = %.2f; $\alpha$ = %d$^o$, $\beta$ = %d$^o$, $\gamma$ = %d$^o$''' % (self.comboBox_crystaltype.currentText(),self.comboBox_celltype.currentText(),self.a,self.b,self.c,alph,beta,gam)
            ann = self.Plot.annotate(plot_label, xy=(0.02, 1.02), xycoords='axes fraction',bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.01))
            ann.draggable() #make annotation draggable
        
        #need to choose a reference point with smallest sum of absolute miller indices
        #since self.DSpaces is sorted with largest d-space first, this will be the smallest sum of abs miller indices
        #first point
        rotation = np.radians(float(self.comboBox_rotate.currentText()))
        d = np.array(self.DSpaces['d-space'],dtype=np.float)
        ref = np.array(self.DSpaces.loc[0,['h','k','l']],dtype=np.int)
        Q2 = np.array(self.DSpaces[['h','k','l']],dtype=np.int)
        recip_vec = np.array([self.astar,self.bstar,self.cstar],dtype=np.float)
        dir_vec = np.array([self.u,self.v,self.w],dtype=np.int)
        #add extra factor if hcp unit cell
        t = self.comboBox_crystaltype.currentText()
        #must check that Forbidden dataframe isn't empty for a spcific zone axis
        showf = self.checkBox_showforbidden.isChecked() and not self.Forbidden.empty
        if t in ['Hexagonal','Trigonal']:
            #print('Hexagonal')
            #change dtypes
            ref = np.array(ref,dtype=np.float)
            Q2 = np.array(Q2,dtype=np.float)
            lam = np.sqrt(2/3)*(self.c/self.a)
            ref[2] = ref[2]/lam
            ref = np.hstack([ref,-(ref[0]+ref[1])]) #add i direction, but to the end b/c it doesnt matter
            Q2[:,2] = Q2[:,2]/lam
            Q2 = np.append(Q2,np.array([-Q2[:,0]-Q2[:,1]]).T,axis=1)
            theta,x,y = CalcSpotsHCP(d,Q2,ref,recip_vec,dir_vec,rotation)
            if showf:
                df = np.array(self.Forbidden['d-space'],dtype=np.float)
                Q2f = np.array(self.Forbidden[['h','k','l']],dtype=np.int)
                Q2f = np.array(Q2f,dtype=np.float)
                Q2f[:,2] = Q2f[:,2]/lam
                Q2f = np.append(Q2f,np.array([-Q2f[:,0]-Q2f[:,1]]).T,axis=1)
                thetaf,xf,yf = CalcSpotsHCP(df,Q2f,ref,recip_vec,dir_vec,rotation)
        else:
            theta,x,y = CalcSpots(d,Q2,ref,recip_vec,self.G_inv,dir_vec,rotation)
            if showf:
                df = np.array(self.Forbidden['d-space'],dtype=np.float)
                Q2f = np.array(self.Forbidden[['h','k','l']],dtype=np.int)
                thetaf,xf,yf = CalcSpots(df,Q2f,ref,recip_vec,self.G_inv,dir_vec,rotation)
                
        self.DSpaces['theta'] = np.degrees(theta).round(2); self.DSpaces['x'] = x; self.DSpaces['y'] = y
        if showf:
            self.Forbidden['theta'] = np.degrees(thetaf).round(2); self.Forbidden['x'] = xf; self.Forbidden['y'] = yf
            for i in range(len(self.Forbidden)):
                label = ' '.join([str(int(x)) for x in self.Forbidden.loc[i,['h','k','l']]]) #this is a bit dense, but makes a list of str() hkl values, then concatenates
                #convert negative numbers to overline numbers for visual effect
                for j,num in enumerate(self.overline_strings):
                    match = re.search(u'-%d' % (j+1),label)
                    if match:
                        label = re.sub(match.group(),num,label)
                #add each label and coordinate to DSpace dataframe
    #            self.DSpaces.loc[i,'x'] = coords[0]
    #            self.DSpaces.loc[i,'y'] = coords[1]
                self.Forbidden.loc[i,'label'] = label
            
        #print(self.DSpaces)
        #make label for each spot
        for i in range(len(self.DSpaces)):
            label = ' '.join([str(int(x)) for x in self.DSpaces.loc[i,['h','k','l']]]) #this is a bit dense, but makes a list of str() hkl values, then concatenates
            #convert negative numbers to overline numbers for visual effect
            for j,num in enumerate(self.overline_strings):
                match = re.search(u'-%d' % (j+1),label)
                if match:
                    label = re.sub(match.group(),num,label)
            #add each label and coordinate to DSpace dataframe
#            self.DSpaces.loc[i,'x'] = coords[0]
#            self.DSpaces.loc[i,'y'] = coords[1]
            self.DSpaces.loc[i,'label'] = label
            

        #add 000 spot
        self.DSpaces.loc[len(self.DSpaces),['d-space','h','k','l','x','y','label']] = [0,0,0,0,0,0,'0 0 0']
        #print(self.DSpaces)
        #scatterplots make it difficult to get data back in matplotlibwidget
#        for i in range(len(self.DSpaces)):
        self.Plot.plot(self.DSpaces['x'],self.DSpaces['y'],ls='',marker='o',markersize=10,color='k',picker=5)#,label='%i %i %i' % (self.DSpaces.loc[i,['h']],self.DSpaces.loc[i,['k']],self.DSpaces.loc[i,['l']]))
        if showf:
            self.Plot.plot(self.Forbidden['x'],self.Forbidden['y'],ls='',marker='o',markersize=7,color='gray', alpha=.7)
        
        #xmax = max(self.DSpaces['x']); xmin = min(self.DSpaces['x'])
        #ymax = max(self.DSpaces['y']); ymin = min(self.DSpaces['y'])
        #self.Plot.set_xlim([1.5*xmin,1.5*xmax])
        #self.Plot.set_ylim([1.5*ymin,1.5*ymax])
        if self.checkBox_labels.isChecked() == True:
            for i in range(len(self.DSpaces)):
                #label = self.MathLabels(i)
                label = self.DSpaces.loc[i,'label']
                self.Plot.annotate(label, xy = (self.DSpaces.loc[i,'x'],self.DSpaces.loc[i,'y']), xytext=(0,10),textcoords = 'offset points', ha = 'center', va = 'bottom',
                           bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.01))
            if showf:
                for i in range(len(self.Forbidden)):
                    #label = self.MathLabels(i)
                    label = self.Forbidden.loc[i,'label']
                    self.Plot.annotate(label, xy = (self.Forbidden.loc[i,'x'],self.Forbidden.loc[i,'y']), xytext=(0,10),textcoords = 'offset points', ha = 'center', va = 'bottom',color='gray',
                               bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.01))
        
        if showf:
            self.common.Forbidden = self.Forbidden
        self.common.DSpaces = self.DSpaces
        self.common.a = self.doubleSpinBox_a.value()#for determining arrow size in plot
        
        self.DiffWidget.canvas.draw()
        
    def MathLabels(self,i):
        '''Make labels with overlines instead of minus signs for plotting with matplotlib.
        i is the index for DSpaces'''
        label = r''
        if self.DSpaces.loc[i,'h'] < 0:
            label+=r'$\bar %i$ ' % abs(self.DSpaces.loc[i,'h'])
        else:
            label+=r'%i ' % self.DSpaces.loc[i,'h']
        if self.DSpaces.loc[i,'k'] < 0:
            label+=r'$\bar %i$ ' % abs(self.DSpaces.loc[i,'k'])
        else:
            label+=r'%i ' % self.DSpaces.loc[i,'k']
        if self.DSpaces.loc[i,'l'] < 0:
            label+=r'$\bar %i$' % abs(self.DSpaces.loc[i,'l'])
        else:
            label+=r'%i' % self.DSpaces.loc[i,'l']
        return(label)


################################################################################
############################### Calculator #####################################
################################################################################

    def Calculator(self):
        """Grabs current miller indices or zone directions and calls AngleCalc"""
        h1 = int(self.comboBox_h1.currentText())
        h2 = int(self.comboBox_h2.currentText())
        k1 = int(self.comboBox_k1.currentText())
        k2 = int(self.comboBox_k2.currentText())
        l1 = int(self.comboBox_l1.currentText())
        l2 = int(self.comboBox_l2.currentText())
        angle = round(np.degrees(self.Diffraction.PlaneAngle(p1=[h1,k1,l1],p2=[h2,k2,l2])),2)
        if np.isnan(angle):
            QtGui.QMessageBox.information(self, "Uh, Oh!", 'There is no [0 0 0] direction/plane!')
        else:
            if self.checkBox_normals.isChecked():
                self.lineEdit_angle.setText(u'φ = %.2f°' % angle)
                
            elif not self.checkBox_normals.isChecked():
                self.lineEdit_angle.setText(u'ρ = %.2f°' % angle)
        

    def CalcLabels(self):
        """Rewrite labels for aesthetics"""
        if self.checkBox_normals.isChecked():
            self.label_h2.setText(u'h')
            self.label_k2.setText(u'k')
            self.label_l2.setText(u'l')
            #self.label_h2.setAlignment(0x0004)
            #self.label_k2.setAlignment(0x0004)
            #self.label_l2.setAlignment(0x0004)
            
        elif not self.checkBox_normals.isChecked():
            self.label_h2.setText(u'u')
            self.label_k2.setText(u'v')
            self.label_l2.setText(u'w')
            #self.label_h2.setAlignment(0x0004)
            #self.label_k2.setAlignment(0x0004)
            #self.label_l2.setAlignment(0x0004)

################################################################################
############################### Other ##########################################
################################################################################

    def About(self):
        """Displays the About message"""
        QtGui.QMessageBox.information(self, "About", 
"""pyLATTICE %s:
Written by Evan Groopman
Based upon LATTICE (DOS) by Thomas Bernatowicz
c. 2011-2014
For help contact: eegroopm@gmail.com""" % self.version)

    def HowTo(self):
        """How-to dialog box"""
        howtomessage = (
        """
- Select crystal type, unit cell type, and lattice parameters to calculate the metric tensor.
- OR select a mineral from the database.
- D-spacings will be calculated between the selected Miller indices.
- Select zone axis and press "Plot" to show diffraction pattern.
- Select two diffraction spots to measure distance and angle.

Note: pyLATTICE only includes general reflection conditions for each space group. It does not includes special conditions based upon multiplcity, site symmetry, etc. EXCEPT for FCC diamond #227.
        """)
        QtGui.QMessageBox.information(self, "How to use", 
                                      howtomessage)


    