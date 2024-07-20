# -*- coding: utf-8 -*-

import pytest
import numpy as np
import simpy
from ..src.components.polarizing_beam_splitter import PolarizingBeamSplitter
from ..src.components.photon import Photon
from ..src.utils.photon_enc import encoding

basisZZ = np.array([np.kron(encoding['Polarization'][0][0],encoding['Polarization'][0][0]),np.kron(encoding['Polarization'][0][0],encoding['Polarization'][0][1]),np.kron(encoding['Polarization'][0][1],encoding['Polarization'][0][0]),np.kron(encoding['Polarization'][0][1],encoding['Polarization'][0][1])])
basisXX = np.array([np.kron(encoding['Polarization'][1][0],encoding['Polarization'][1][0]),np.kron(encoding['Polarization'][1][0],encoding['Polarization'][1][1]),np.kron(encoding['Polarization'][1][1],encoding['Polarization'][1][0]),np.kron(encoding['Polarization'][1][1],encoding['Polarization'][1][1])])

UID = 'PBS'
ENV = simpy.Environment()
ER = 1000

class FakeSource():
    
    def __init__(self):
        pass

class FakeReceiver():
    
     def __init__(self):
         self.photon_count = 0
         self.p_net_rcd = []
    
     def receive(self,p_net):
         self.p_net_rcd = p_net

def test_init():
    PBS = PolarizingBeamSplitter(UID,ENV,ER)
    assert PBS.uID == UID
    assert PBS.env == ENV
    assert PBS.ER == ER
    
def test_connect():
    S = FakeSource()
    R1 = FakeReceiver()
    R2 = FakeReceiver()
    R_net = [R1,R2]
    PBS = PolarizingBeamSplitter(UID,ENV,ER)
    PBS.connect(S,R_net)
    assert PBS.sender == S
    assert PBS.receivers[0] == R1
    assert PBS.receivers[1] == R2
    
def test_set_input_port_connection():
    INPUT_PORT = 2
    PBS = PolarizingBeamSplitter(UID,ENV,ER)
    PBS.set_input_port_connection(INPUT_PORT)
    assert PBS.input_port == INPUT_PORT
    
def test_receive():
    ER = np.inf
    PBS = PolarizingBeamSplitter(UID,ENV,ER)
    S = FakeSource()
    R1 = FakeReceiver()
    R2 = FakeReceiver()
    R_net = [R1,R2]
    PBS.connect(S,R_net)
    
    #Photon
    UID_P = 'p1'
    WL = 2e-9
    TWIDTH = 0.0
    ENC_TYPE = 'Polarization'
    COEFFS = np.array([[complex(1/np.sqrt(2))],[complex(1/np.sqrt(2))]])
    BASIS = encoding['Polarization'][1]
    COEFFS_Z_BASIS_EQUIV = np.array([[complex(1)],[complex(0)]])
    
    INPUT_PORT_NET = [1,2]
    
    for INPUT_PORT in INPUT_PORT_NET:
        PBS.set_input_port_connection(INPUT_PORT)
        
        for i in range(10000):
            p = Photon(UID_P,WL,TWIDTH,ENC_TYPE,COEFFS,BASIS)
            PBS.receive([p])
            if len(R1.p_net_rcd) != 0 and R1.p_net_rcd[0] is not None:
                R1.photon_count += 1
            elif len(R2.p_net_rcd) != 0 and R2.p_net_rcd[0] is not None:
                R2.photon_count += 1
            R1.p_net_rcd = []
            R2.p_net_rcd = []
            
        if INPUT_PORT == 1:
            assert PBS.R == np.square(np.abs(COEFFS_Z_BASIS_EQUIV[1]))
            assert np.abs(((R1.photon_count/10000) - PBS.R)) < 5e-2
            assert np.abs(((R2.photon_count/10000) - (1 - PBS.R))) < 5e-2 
        elif INPUT_PORT == 2:
            assert PBS.R == 1 - np.square(np.abs(COEFFS_Z_BASIS_EQUIV[1]))
            assert np.abs(((R2.photon_count/10000) - PBS.R)) < 5e-2
            assert np.abs((R1.photon_count/10000) - (1 - PBS.R)) < 5e-2 
            
        R1.photon_count = 0
        R2.photon_count = 0
    
        
    #Two Qubit States
    COEFFS_LIST2 = [np.array([[complex(1/np.sqrt(2))],[complex(0)],[complex(0)],[complex(1/np.sqrt(2))]]),np.array([[complex(0)],[complex(1/np.sqrt(2))],[complex(-1/np.sqrt(2))],[complex(0)]])]
    BASIS_LIST2 = [basisZZ,basisXX]
    EP_QUBIT_NUMBERS = [2,1]
    CONDENSED_COEFFS_Z_BASIS_EQUIV_LIST = [np.array([[complex(1/np.sqrt(2))],[complex(1/np.sqrt(2))]]),np.array([[complex(-1/np.sqrt(2))],[complex(1/np.sqrt(2))]])]
    
    for INPUT_PORT in INPUT_PORT_NET:
        PBS.set_input_port_connection(INPUT_PORT)
        
        for COEFFS,BASIS,EP_QUBIT_NUM,CONDENSED_COEFFS_Z_BASIS_EQUIV in zip(COEFFS_LIST2,BASIS_LIST2,EP_QUBIT_NUMBERS,CONDENSED_COEFFS_Z_BASIS_EQUIV_LIST):
            
            for i in range(10000):
                p = Photon(UID_P,WL,TWIDTH,ENC_TYPE,COEFFS,BASIS)
                p.qs.ep_qubit_num = EP_QUBIT_NUM
                PBS.receive([p])
                if len(R1.p_net_rcd) != 0 and R1.p_net_rcd[0] is not None:
                    R1.photon_count += 1
                elif len(R2.p_net_rcd) != 0 and R2.p_net_rcd[0] is not None:
                    R2.photon_count += 1
                R1.p_net_rcd = []
                R2.p_net_rcd = []
                
            if INPUT_PORT == 1:
                assert PBS.R == np.square(np.abs(CONDENSED_COEFFS_Z_BASIS_EQUIV[1]))
                assert np.abs(((R1.photon_count/10000) - PBS.R)) < 5e-2
                assert np.abs(((R2.photon_count/10000) - (1 - PBS.R))) < 5e-2 
            elif INPUT_PORT == 2:
                assert PBS.R == 1 - np.square(np.abs(CONDENSED_COEFFS_Z_BASIS_EQUIV[1]))
                assert np.abs(((R2.photon_count/10000) - PBS.R)) < 5e-2
                assert np.abs(((R1.photon_count/10000) - (1 - PBS.R))) < 5e-2 
            R1.photon_count = 0
            R2.photon_count = 0
        
def test_ER():
    
    ER = 1000
    PBS = PolarizingBeamSplitter(UID,ENV,ER)
    S = FakeSource()
    R1 = FakeReceiver()
    R2 = FakeReceiver()
    R_net = [R1,R2]
    PBS.connect(S,R_net)
    INPUT_PORT = 1
    PBS.set_input_port_connection(INPUT_PORT)
    
    #Photon
    UID_P = 'p1'
    WL = 2e-9
    TWIDTH = 0.0
    ENC_TYPE = 'Polarization'
    COEFFS = np.array([[complex(1/np.sqrt(2))],[complex(1/np.sqrt(2))]])
    BASIS = encoding['Polarization'][1]
    
    for i in range(10000):
        p = Photon(UID_P,WL,TWIDTH,ENC_TYPE,COEFFS,BASIS)
        PBS.receive([p])
        if len(R1.p_net_rcd) != 0 and R1.p_net_rcd[0] is not None:
            R1.photon_count += 1
        elif len(R2.p_net_rcd) != 0 and R2.p_net_rcd[0] is not None:
            R2.photon_count += 1
        R1.p_net_rcd = []
        R2.p_net_rcd = []
    
    assert np.abs(((R1.photon_count/10000) - (1/ER))) < 5e-3