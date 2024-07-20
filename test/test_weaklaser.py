#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import simpy
import numpy as np
from ..src.components.weaklaser import Weaklaser

ENV = simpy.Environment()

#LASER
UID = 'L1'
PRR = 8e7
WL = 1550e-9
LWIDTH = 0.01e-9
TWIDTH = 100e-15
MU_PHOTONS = 1e5
ENC_TYPE = 'Polarization'
NOISE_LEVEL = 0.02
GAMMA = 0.4
LMDA = 0.3

#VARIABLE ND FILTER
UID = 'NDF1'
MIN_OD = 0
MAX_OD = 4

MAX_NUM_OF_ND_FILTERS = 5

class FakeReceiver():
    
    def __init__(self):
        pass
    
    def receive(self,p_net):
        self.p_net_rcd = p_net

def test_init():
    WeakLaser = Weaklaser(UID,ENV,PRR,WL,LWIDTH,TWIDTH,MU_PHOTONS,ENC_TYPE,NOISE_LEVEL,GAMMA,LMDA,MIN_OD,MAX_OD,MAX_NUM_OF_ND_FILTERS,calc_mu_photons_after_attenuation = False)
    assert WeakLaser.uID == UID
    assert WeakLaser.max_num_of_ND_filters == MAX_NUM_OF_ND_FILTERS
    assert np.allclose(WeakLaser.ND_Filter_Stack,[2.5,2.5])
    assert WeakLaser.mean_transmission_time == 1/PRR
    assert WeakLaser.p_twidth == TWIDTH
    assert WeakLaser.env == ENV
    
def test_connect():
    R = FakeReceiver()
    WeakLaser = Weaklaser(UID,ENV,PRR,WL,LWIDTH,TWIDTH,MU_PHOTONS,ENC_TYPE,NOISE_LEVEL,GAMMA,LMDA,MIN_OD,MAX_OD,MAX_NUM_OF_ND_FILTERS,calc_mu_photons_after_attenuation = False)
    WeakLaser.connect(R)
    assert WeakLaser.receiver == R