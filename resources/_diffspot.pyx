# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 11:53:07 2014

@author: eegroopm
Calculates diffraction spot coordinates, returns x,y,angle
"""

import numpy as np
cimport numpy as np

DTYPEi = np.int
DTYPEf = np.float
ctypedef np.int_t DTYPEi_t
ctypedef np.float_t DTYPEf_t

def CalcSpots(np.ndarray d, np.ndarray Q2, np.ndarray ref, np.ndarray recip_vec, np.ndarray Ginv, np.ndarray dir_vec, DTYPEf_t rotation):
	assert Ginv.dtype == DTYPEf #reciprocal metric tensor
	assert d.dtype == DTYPEf #DSpaces
	assert ref.dtype == DTYPEi #reference vector, also Q1
	assert dir_vec.dtype == DTYPEi #direction vector [u,v,w]
	assert recip_vec.dtype == DTYPEf #reciprocall lattice vector [a*,b*,c*]
	assert Q2.dtype == DTYPEi #array of h,k,l values Q2[:,0] = 'h', etc.
	cdef np.ndarray cos = np.zeros([len(d),1],dtype=DTYPEf)
	cdef np.ndarray sin = np.zeros([len(d),1],dtype=DTYPEf)
	cdef np.ndarray theta = np.zeros([len(d),1],dtype=DTYPEf)
	cdef np.ndarray x = np.zeros([len(d),1],dtype=DTYPEf)
	cdef np.ndarray y = np.zeros([len(d),1],dtype=DTYPEf)
	cdef np.ndarray q1 = np.zeros([1,len(ref)],dtype=DTYPEf) #len(ref) allows for 4-vector hcp
	cdef np.ndarray q2 = np.zeros([len(d),len(ref)],dtype=DTYPEf)

	q1 = ref * recip_vec
	q2 = Q2 * recip_vec

	#cos = np.ravel(ref.dot(Ginv).dot(Q2.T))/(np.linalg.norm(ref)*np.linalg.norm(Q2,axis=1))
	cos = ref.dot(Q2.T)/(np.linalg.norm(ref)*np.linalg.norm(Q2,axis=1))
	sin = np.cross(q1,q2).dot(dir_vec)/(np.linalg.norm(ref)*np.linalg.norm(Q2,axis=1))

	#theta = np.arctan2(sin,cos)
	for i in range(len(cos)):
		if cos[i] > 0 and sin[i] > 0:
			theta[i] = np.arccos(cos[i])
		elif cos[i] < 0 and sin[i] > 0:
			theta[i] = np.arccos(cos[i])
		elif cos[i] > 0 and sin[i] < 0:
			theta[i] = 2*np.pi - np.arccos(cos[i])
		elif cos[i] < 0 and sin[i] < 0:
			theta[i] = 2*np.pi - np.arccos(cos[i])
		elif cos[i] > 0 and sin[i] == 0:
			theta[i] = 0
		elif cos[i] == 0 and sin[i] > 0:
			theta[i] = np.pi / 2
		elif cos[i] < 0 and sin[i] == 0:
			theta[i] = np.pi
		elif cos[i] == 0 and sin[i] < 0:
			theta[i] = 3 * np.pi / 2

		x[i] = np.cos(theta[i])/d[i]
		y[i] = np.sin(theta[i])/d[i]
	#x = np.cos(theta)/d
	#y = np.sin(theta)/d

	#use [[cos -sin],[sin,cos]] matrix to rotate
	if rotation != 0.0:
		print('Rotating by %d degrees' % np.degrees(rotation))
		x,y = (x*np.cos(rotation) - y*np.sin(rotation), x*np.sin(rotation) + y*np.cos(rotation))
	return(theta,x,y)

def CalcSpotsHCP(np.ndarray d, np.ndarray Q2, np.ndarray ref, np.ndarray recip_vec, np.ndarray dir_vec, DTYPEf_t rotation):
	assert d.dtype == DTYPEf #DSpaces
	assert ref.dtype == DTYPEf #reference vector, also Q1
	assert dir_vec.dtype == DTYPEi #reciprocall lattice vector [a*,b*,c*]
	assert recip_vec.dtype == DTYPEf #reciprocall lattice vector [a*,b*,c*]
	assert Q2.dtype == DTYPEf #array of h,k,l values Q2[:,0] = 'h', etc.
	cdef np.ndarray cos = np.zeros([len(d),1],dtype=DTYPEf)
	cdef np.ndarray sin = np.zeros([len(d),1],dtype=DTYPEf)
	cdef np.ndarray theta = np.zeros([len(d),1],dtype=DTYPEf)
	cdef np.ndarray x = np.zeros([len(d),1],dtype=DTYPEf)
	cdef np.ndarray y = np.zeros([len(d),1],dtype=DTYPEf)
	cdef np.ndarray q1 = np.zeros([1,3],dtype=DTYPEf) #len(ref) allows for 4-vector hcp
	cdef np.ndarray q2 = np.zeros([len(d),3],dtype=DTYPEf)

	q1 = ref[:3] * recip_vec
	q2 = Q2[:,:3] * recip_vec

	#cos = np.ravel(ref.dot(Ginv).dot(Q2.T))
	cos = ref.dot(Q2.T)/(np.linalg.norm(ref)*np.linalg.norm(Q2,axis=1))
	sin = np.cross(q1,q2).dot(dir_vec)#/(np.linalg.norm(q1)*np.linalg.norm(q2,axis=1))
	#theta = np.arctan2(sin,cos)
	for i in range(len(cos)):
		if cos[i] > 0 and sin[i] > 0:
			theta[i] = np.arccos(cos[i])
		elif cos[i] < 0 and sin[i] > 0:
			theta[i] = np.arccos(cos[i])
		elif cos[i] > 0 and sin[i] < 0:
			theta[i] = 2*np.pi - np.arccos(cos[i])
		elif cos[i] < 0 and sin[i] < 0:
			theta[i] = 2*np.pi - np.arccos(cos[i])
		elif cos[i] > 0 and sin[i] == 0:
			theta[i] = 0
		elif cos[i] == 0 and sin[i] > 0:
			theta[i] = np.pi / 2
		elif cos[i] < 0 and sin[i] == 0:
			theta[i] = np.pi
		elif cos[i] == 0 and sin[i] < 0:
			theta[i] = 3 * np.pi / 2

		x[i] = np.cos(theta[i])/d[i]
		y[i] = np.sin(theta[i])/d[i]
	#x = np.cos(theta)/d
	#y = np.sin(theta)/d

	#use [[cos -sin],[sin,cos]] matrix to rotate
	if rotation != 0.0:
		print('Rotating by %d degrees' % np.degrees(rotation))
		x,y = (x*np.cos(rotation) - y*np.sin(rotation), x*np.sin(rotation) + y*np.cos(rotation))
	return(theta,x,y)