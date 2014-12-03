# -*- coding: utf-8 -*-
"""
Created on Mon Apr 21 10:34:18 2014

@author: eegroopm
"""
import os, sys
import pandas as pd
import numpy as np

class common:
    def __init__(self):
        self.path = os.path.expanduser('~')
        #\u0305 is unicode overline character
        #self._overline_strings = [u'1\u0305', u'2\u0305' ,u'3\u0305', u'4\u0305', u'5\u0305', u'6\u0305', u'7\u0305',u'8\u0305',u'9\u0305']
        #use matplotlib's mathtex rendering for overline strings
        self._overline_strings = [r'\\bar{1}',r'\\bar{2}',r'\\bar{3}',
                                  r'\\bar{6}',r'\\bar{5}',r'\\bar{6}',
                                  r'\\bar{7}',r'\\bar{8}',r'\\bar{9}']
        self.DSpaces = pd.DataFrame(columns = ['d-space','h','k','l']) #Msum is sum of absolute miller indices, neede for plotting pattern
        self.Forbidden = pd.DataFrame(columns = ['d-space','h','k','l'])
        self.u = 0
        self.v = 0
        self.w = 1
        self.ZoneAxis = np.array([self.u,self.v,self.w])
        
        self.beamenergy = 200 #keV
        self.camlength = 100 #cm
        self.camconst = 1.0
        self.wavelength = self.Wavelength(self.beamenergy) #angstroms
        
        self._x2 = False
        self.a = 1
        self.b = 1
        self.c = 1
        self.astar = 1
        self.bstar = 1
        self.cstar = 1
        self.alpha = 90 #degrees
        self.beta = 90
        self.gamma = 90
        self.alphastar = 90
        self.betastar = 90
        self.gammastar = 90
        
        #SpaceGroup data
        #DataFrame in the form SG Number, Patterson symbol, Geometry,Unit Cell Type, Unit Cell Conditions , Spacegroup conditions
        #e.g.
        #sg.loc[218] yields:
            #Patterson    P-43n
            #Conditions   (h==k and l == 2*n) or (h == 2*n and k==0 and ...
            #Name: 218, dtype: object
        if sys.version_info[0] == 3: #python3 and python2 pickle h5 files differently. GAH!!
            self.sg = pd.read_hdf('resources/SpaceGroups.h5','table')
            self.sghex = pd.read_hdf('resources/SpaceGroupsHex.h5','table') #for trigonal crystals with rhombohedral or hexagonal centering
            self.mineraldb = pd.read_hdf('resources/MineralDatabase.h5','table')
        elif sys.version_info[0] == 2:
            self.sg = pd.read_hdf('resources/SpaceGroups_py2.h5','table')
            self.sghex = pd.read_hdf('resources/SpaceGroupsHex_py2.h5','table')
            self.mineraldb = pd.read_hdf('resources/MineralDatabase_py2.h5','table')
        
        self.manualConds = [] #empty list of strings for manual conditions
            
    def Wavelength(self,E):
        hbar = 6.626E-34 #m^2 kg/s
        me = 9.109E-31 #kg
        c = 3E8 #m/s
        e = 1.602E-19 #Coulombs
        E = E*1000 #turn to eV
        wavelength = hbar/np.sqrt(2*me*e*E)/np.sqrt(1 + (e*E)/(2*me*c**2))*(10**10) #angstroms. relativistic formula
        return(wavelength)