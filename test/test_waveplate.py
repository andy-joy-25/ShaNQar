# -*- coding: utf-8 -*-

import pytest
import numpy as np
import simpy
from ..src.components.waveplate import WavePlate
from ..src.components.photon import Photon
from ..src.utils.photon_enc import encoding

UID = 'HWP'
ALPHA = 180
THETA = 22.5
ENV = simpy.Environment()

basisZZ = np.array([np.kron(encoding['Polarization'][0][0],encoding['Polarization'][0][0]),np.kron(encoding['Polarization'][0][0],encoding['Polarization'][0][1]),np.kron(encoding['Polarization'][0][1],encoding['Polarization'][0][0]),np.kron(encoding['Polarization'][0][1],encoding['Polarization'][0][1])])
basisXX = np.array([np.kron(encoding['Polarization'][1][0],encoding['Polarization'][1][0]),np.kron(encoding['Polarization'][1][0],encoding['Polarization'][1][1]),np.kron(encoding['Polarization'][1][1],encoding['Polarization'][1][0]),np.kron(encoding['Polarization'][1][1],encoding['Polarization'][1][1])])


class FakeSource():
    
    def __init__(self):
        pass

class FakeReceiver():
    
    def __init__(self):
        pass
    
    def receive(self,p_net):
        self.p_net_rcd = p_net

def test_init():
    WP = WavePlate(UID,ENV,ALPHA,THETA)
    assert WP.uID == UID
    assert WP.env == ENV
    assert WP.alpha == np.deg2rad(ALPHA)
    assert WP.theta == np.deg2rad(THETA)
    
def test_connect():
    S = FakeSource()
    R = FakeReceiver()
    WP = WavePlate(UID,ENV,ALPHA,THETA)
    WP.connect(S,R)
    assert WP.sender == S
    assert WP.receiver == R

def test_receive():
    S = FakeSource()
    R = FakeReceiver()
    WP = WavePlate(UID,ENV,ALPHA,THETA)
    WP.connect(S,R)
    
    #Photon
    UID_P = 'p1'
    WL = 2e-9
    TWIDTH = 0.0
    ENC_TYPE = 'Polarization'
    COEFFS = [[complex(1)],[complex(0)]]
    COEFFS = np.reshape(np.array(COEFFS),(len(COEFFS),1))
    BASIS = encoding['Polarization'][0]
    
    #Test Cases for a Half Wave Plate with Theta = 22.5 (~ Hadamard Gate)
    COEFFS_LIST = [np.array([[complex(1)],[complex(0)]]),np.array([[complex(0)],[complex(1)]])]
    BASIS_LIST = [encoding['Polarization'][0],encoding['Polarization'][1]]
    TRANSFORMED_COEFFS_LIST = [np.array([[complex(0,-1/np.sqrt(2))],[complex(0,-1/np.sqrt(2))]]),np.array([[complex(0,-1/np.sqrt(2))],[complex(0,1/np.sqrt(2))]])]
    for basis in BASIS_LIST:
        for coeffs,transformed_coeffs in zip(COEFFS_LIST,TRANSFORMED_COEFFS_LIST):
            p = Photon(UID_P,WL,TWIDTH,ENC_TYPE,coeffs,basis)
            WP.receive([p])
            WP.p_net_rcd = []
            assert np.allclose(p.qs.coeffs,transformed_coeffs)
            
    COEFFS_LIST2 = [np.array([[complex(1/np.sqrt(2))],[complex(0)],[complex(0)],[complex(1/np.sqrt(2))]]),np.array([[complex(0)],[complex(1/np.sqrt(2))],[complex(-1/np.sqrt(2))],[complex(0)]])]
    BASIS_LIST2 = [basisZZ,basisXX]
    EP_QUBIT_NUMBERS = [2,1]
    TRANSFORMED_COEFFS_LIST2 = [np.array([[complex(0,-1/2)],[complex(0,-1/2)],[complex(0,-1/2)],[complex(0,1/2)]]),np.array([[complex(0,1/2)],[complex(0,-1/2)],[complex(0,-1/2)],[complex(0,-1/2)]])]
    for coeffs,basis,ep_qnum,transformed_coeffs in zip(COEFFS_LIST2,BASIS_LIST2,EP_QUBIT_NUMBERS,TRANSFORMED_COEFFS_LIST2):
        p = Photon(UID_P,WL,TWIDTH,ENC_TYPE,coeffs,basis)
        p.qs.ep_qubit_num = ep_qnum
        WP.receive([p])
        WP.p_net_rcd = []
        assert np.allclose(p.qs.coeffs,transformed_coeffs)