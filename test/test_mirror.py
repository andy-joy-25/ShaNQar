# -*- coding: utf-8 -*-

import pytest
import numpy as np
import simpy
from ..src.utils.photon_enc import encoding
from ..src.components.photon import Photon
from ..src.components.mirror import Mirror

ENV = simpy.Environment()
UID = 'M1'
R = 0.75
NOISE_LEVEL = 0
GAMMA = 0.4
LAMBDA = 0.3

#Photon
UID_P = 'p1'
WL = 2e-9
TWIDTH = 0.0
ENC_TYPE = 'Polarization'
COEFFS = np.array([[complex(1/2)],[complex(np.sqrt(3)/2)]])
BASIS = encoding['Polarization'][0]

class FakeSource():
    
    def __init__(self):
        pass

class FakeReceiver():
    
    def __init__(self):
        pass
    
    def receive(self,p_net):
        self.p_net_rcd = p_net

def test_init():
    M1 = Mirror('M1',ENV,R,NOISE_LEVEL,GAMMA,LAMBDA)
    assert M1.uID == UID
    assert M1.reflectivity == R
    assert M1.noise_level == NOISE_LEVEL
    assert M1.gamma == GAMMA
    assert M1.lmda == LAMBDA

def test_connect():
    M1 = Mirror('M1',ENV,R,NOISE_LEVEL,GAMMA,LAMBDA)
    S = FakeSource()
    Rec = FakeReceiver()
    M1.connect(S,Rec)
    assert M1.sender == S
    assert M1.receiver == Rec
    
def test_reflectivity():
    M1 = Mirror('M1',ENV,R,NOISE_LEVEL,GAMMA,LAMBDA)
    S = FakeSource()
    Rec = FakeReceiver()
    M1.connect(S,Rec)
    p_net_ref = 0
    for i in range(10000):
        p = Photon(UID_P+str(i),WL,TWIDTH,ENC_TYPE,COEFFS,BASIS)
        M1.receive([p])
        if Rec.p_net_rcd[0] is not None:
            p_net_ref += 1
        Rec.p_net_rcd = []
    assert abs((p_net_ref/10000) - R) < 5e-2
    
def test_noise_level():
    R = 1
    NOISE_LEVEL = 0.86
    M1 = Mirror('M1',ENV,R,NOISE_LEVEL,GAMMA,LAMBDA)
    S = FakeSource()
    Rec = FakeReceiver()
    M1.connect(S,Rec)
    p_net_corrupted = 0
    for i in range(10000):
        p = Photon(UID_P+str(i),WL,TWIDTH,ENC_TYPE,COEFFS,BASIS)
        M1.receive([p])
        if not np.allclose(Rec.p_net_rcd[0].qs.coeffs,COEFFS):
            p_net_corrupted += 1
        Rec.p_net_rcd = []
    assert abs((p_net_corrupted/10000) - NOISE_LEVEL) < 5e-2