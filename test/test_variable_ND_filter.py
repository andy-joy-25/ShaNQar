# -*- coding: utf-8 -*-


import pytest
import numpy as np
import simpy
from ..src.utils.photon_enc import encoding
from ..src.components.variable_ND_filter import NDFilter
from ..src.components.photon import Photon

ENV = simpy.Environment()
UID = 'NDF1'
MIN_OD = 0
MAX_OD = 4

#PHOTON
P_UID = 'p1'
WL = 2e-9
TWIDTH = 0.0
ENC_TYPE = 'Polarization'
COEFFS = np.array([[complex(1/2)],[complex(np.sqrt(3)/2)]])
BASIS = encoding['Polarization'][0]
SOURCE_LINEWIDTH = 0.01e-9

def test_init():
    NDF1 = NDFilter(UID,ENV,MIN_OD,MAX_OD)
    assert NDF1.uID == UID
    assert NDF1.env == ENV
    assert NDF1.min_OD == MIN_OD
    assert NDF1.max_OD == MAX_OD
    
def test_set_OD():
    NDF1 = NDFilter(UID,ENV,MIN_OD,MAX_OD)
    OD = 2
    NDF1.set_OD(OD)
    assert NDF1.OD == OD
    
def test_attenuate():
    h = 6.626e-34
    c = 3e8
    NDF1 = NDFilter(UID,ENV,MIN_OD,MAX_OD)
    OD_net = np.arange(MIN_OD+1,MAX_OD+1,dtype=np.float64)
    for OD in OD_net:
        NDF1.set_OD(OD)
        p = Photon(UID,WL,TWIDTH,ENC_TYPE,COEFFS,BASIS)
        ph_net = []
        E_net_input = 0
        for i in range(100):
            ph_net.append(p)
        for ph in ph_net:
            E_net_input += ((h*c)/(ph.wl))
        new_ph_net = NDF1.attenuate(ph_net)
        E_net_output = 0
        for ph in new_ph_net:
            E_net_output += ((h*c)/(ph.wl))
        T = 10**(-OD)
        assert abs(T*E_net_input - E_net_output) < ((h*c)/(WL))