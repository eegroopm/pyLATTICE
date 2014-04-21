#!/usr/bin/python ~/Documents/Research/Spyder\ Projects/pyLATTICE/

""" 
pyLATTICE is...
"""

# define authorship information
__authors__     = ['Evan Groopman', 'Thomas Bernatowicz']
__author__      = ','.join(__authors__)
__credits__     = []
__copyright__   = 'Copyright (c) 2012'
__license__     = 'GPL'

# maintanence information
__maintainer__  = 'Evan Groopman'
__email__       = 'eegroopm@gmail.com'

import numpy as np
import pandas as pd

class Diffraction:
    
    def __init__(self):
        pass
    
    def PlaneAngle(self,p1= np.array([0,0,0]), p2= np.array([0,0,0])):
        """Calculates angle between two planes (h1 k1 l1) & (h2 k2 l2) OR
        between two directions [U1 V1 W1] & [U2 V2 W2].
        
        Returns angle in degrees.
        """
        #numerator = p1[0]*p2[0] + p1[1]*p2[1] + p1[2]*p2[2]
        #denominator = np.sqrt(p1[0]**2 + p1[1]**2 + p1[2]**2)*np.sqrt(p2[0]**2 + p2[1]**2 + p2[2]**2)
        numerator = np.dot(p2,p1)
        #if p2 is a multi-row set of directions, indicate the axis to calculate along
        if len(np.shape(p2)) > 1:
            i = 1
        else:
            i = 0
        denominator = np.linalg.norm(p1) * np.linalg.norm(p2,axis=i)
        angle = np.arccos(numerator/denominator)
        return(angle)
    
    def AngleAmbiguity(self,cos,sin):
        """Resolves angle ambiguity"""
        theta = 0 #removes UnboundLocalError
        if cos > 0 and sin > 0:
            theta = np.arccos(cos)
        elif cos < 0 and sin > 0:
            theta = np.arccos(cos)
        elif cos > 0 and sin < 0:
            theta = 2*np.pi - np.arccos(cos)
        elif cos < 0 and sin < 0:
            theta = 2*np.pi - np.arccos(cos)
        elif cos > 0 and sin == 0:
            theta = 0
        elif cos == 0 and sin > 0:
            theta = np.pi / 2
        elif cos < 0 and sin == 0:
            theta = np.pi
        elif cos == 0 and sin < 0:
            theta = 3 * np.pi / 2
        return(theta)
        
    def timetest(G_inv,u,v,w,hmin,hmax,kmin,kmax,lmin,lmax,conditions):
        d = pd.DataFrame(columns = ['d-space','h','k','l'])
        i=0
        for h in range(int(hmin),int(hmax)+1):
            for k in range(int(kmin),int(kmax)+1):
                for l in range(int(lmin),int(lmax)+1):
                    vector = np.array([h,k,l])
                    dspace_inv = float(np.sqrt(np.mat(vector) * np.mat(G_inv) * np.mat(vector).T))

                    if eval(conditions) and dspace_inv != 0 and (h*u + k*v + l*w == 0):
                        i+=1
                        dspace = dspace_inv**(-1)
                        d.loc[i] = np.array([round(dspace,6),h, k, l])
        return(d)