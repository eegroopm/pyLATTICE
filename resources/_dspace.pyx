# -*- coding: utf-8 -*-
"""
Created on Sun Feb  9 21:44:50 2014

@author: eegroopm

Calculates d-spacings based upon ranges of h,k,l and conditions.

- conditions are strings
"""
import numpy as np
cimport numpy as np
import pandas as pd

DTYPEi = np.int
DTYPEf = np.float
ctypedef np.int_t DTYPEi_t
ctypedef np.float_t DTYPEf_t


def DSpace(np.ndarray Ginv, int u, int v, int w, int hmin,int hmax,int kmin,int kmax,int lmin,int lmax, str conditions,int q):
    assert Ginv.dtype == DTYPEf
    cdef int h,k,l
    cdef int i = 0
    cdef np.ndarray vector = np.zeros([1,3],dtype=DTYPEi)
    cdef DTYPEf_t dspace_inv
    
    DSpaces = pd.DataFrame(columns = ['d-space','h','k','l'])
    
    for h in range(hmin,hmax+1):
        for k in range(kmin,kmax+1):
            for l in range(lmin,lmax+1):
                if eval(conditions) and (h*u + k*v + l*w == 0):
                    vector = np.array([h,k,l])
                    dspace_inv = np.sqrt(vector.dot(Ginv).dot(vector)) #this is the same as matrix multiplication

                    if dspace_inv != 0:
                        i+=1
                        DSpaces.loc[i,'d-space'] = dspace_inv**(-1)
                        DSpaces.loc[i,'h'] = h
                        DSpaces.loc[i,'k'] = k
                        DSpaces.loc[i,'l'] = l
                        
    return(DSpaces)