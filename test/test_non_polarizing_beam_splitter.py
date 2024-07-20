# -*- coding: utf-8 -*-

import pytest
import simpy
import numpy as np
from ..src.components.non_polarizing_beam_splitter import NonPolarizingBeamSplitter
from ..src.utils.photon_enc import encoding
from ..src.components.photon import Photon
from ..src.components.quantum_state import QuantumState

#Non Polarising Beam Splitter
UID = 'NPBS1'
ENV = simpy.Environment()
RLT = 0.50

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
         self.photon_count = 0
         self.p_net_rcd = []
    
     def receive(self,p_net):
         self.p_net_rcd = p_net
         

def test_init():
    NPBS1 = NonPolarizingBeamSplitter(UID,ENV,RLT)
    assert NPBS1.uID == UID
    assert NPBS1.R == RLT
    
def test_connect():
    S1 = FakeSource()
    S2 = FakeSource()
    S_net = [S1,S2]
    R1 = FakeReceiver()
    R2 = FakeReceiver()
    R_net = [R1,R2]
    NPBS1 = NonPolarizingBeamSplitter(UID,ENV,RLT)
    NPBS1.connect(S_net,R_net)
    assert NPBS1.senders[0] == S1
    assert NPBS1.senders[1] == S2
    assert NPBS1.receivers[0] == R1
    assert NPBS1.receivers[1] == R2
    
def test_set_input_port_connection():
    INPUT_PORT_NET = [2,1]
    NPBS1 = NonPolarizingBeamSplitter(UID,ENV,RLT)
    NPBS1.set_input_port_connection(INPUT_PORT_NET)
    assert NPBS1.input_port_net == INPUT_PORT_NET
    
def test_set_ep_qstate():
    NPBS1 = NonPolarizingBeamSplitter(UID,ENV,RLT)
    ket0 = np.array([[complex(1)],[complex(0)]])
    ket1 = np.array([[complex(0)],[complex(1)]])
    phi_plus = np.array([[complex(1/np.sqrt(2))],[complex(0)],[complex(0)],[complex(1/np.sqrt(2))]])
    phi_minus = np.array([[complex(1/np.sqrt(2))],[complex(0)],[complex(0)],[complex(-1/np.sqrt(2))]])
    psi_plus = np.array([[complex(0)],[complex(1/np.sqrt(2))],[complex(1/np.sqrt(2))],[complex(0)]])
    psi_minus = np.array([[complex(0)],[complex(1/np.sqrt(2))],[complex(-1/np.sqrt(2))],[complex(0)]])
    basisXX = np.array([np.kron(encoding['Polarization'][1][0],encoding['Polarization'][1][0]),np.kron(encoding['Polarization'][1][0],encoding['Polarization'][1][1]),np.kron(encoding['Polarization'][1][1],encoding['Polarization'][1][0]),np.kron(encoding['Polarization'][1][1],encoding['Polarization'][1][1])])
    INIT_EP_QSTATE_COEFFS_NET = [phi_plus,phi_minus,psi_plus,psi_minus]
    FINAL_EP_QSTATE_COEFFS_NET = [[ket0,ket0,ket1,ket1],[ket0,ket0,-ket1,-ket1],[ket1,ket1,ket0,ket0],[ket1,ket1,-ket0,-ket0]]
    RAND_IDX_NET = [0,1,2,3]
    T_QSTATE_COEFFS = ket0
    for i,ep_qstate_coeffs in enumerate(INIT_EP_QSTATE_COEFFS_NET):
        ep_qstate = QuantumState(ep_qstate_coeffs,basisXX)
        for rand_idx in RAND_IDX_NET:
            NPBS1.set_ep_qstate(ep_qstate,T_QSTATE_COEFFS,rand_idx)
            final_ep_qstate_coeffs = FINAL_EP_QSTATE_COEFFS_NET[i][rand_idx]
            assert np.allclose(ep_qstate.coeffs,final_ep_qstate_coeffs)
            ep_qstate = QuantumState(ep_qstate_coeffs,basisXX)
    
def test_receive():
    S = FakeSource()
    R1 = FakeReceiver()
    R2 = FakeReceiver()
    R_net = [R1,R2]
    NPBS1 = NonPolarizingBeamSplitter(UID,ENV,RLT)
    NPBS1.connect([S],R_net)
    INPUT_PORT_NET = [1,2]
    for INPUT_PORT in INPUT_PORT_NET:
        NPBS1.set_input_port_connection([INPUT_PORT])
        
        for i in range(10000):
            p = Photon(UID_P+str(i),WL,TWIDTH,ENC_TYPE,COEFFS,BASIS)
            NPBS1.receive([p])
            if len(R1.p_net_rcd) != 0 and R1.p_net_rcd[0] != None:
                R1.photon_count += 1
            elif len(R2.p_net_rcd) != 0 and R2.p_net_rcd[0] != None:
                R2.photon_count += 1
            R1.p_net_rcd = []
            R2.p_net_rcd = []
        if INPUT_PORT == 1:
            assert ((R1.photon_count/10000) - NPBS1.R) < 5e-2
            assert ((R2.photon_count/10000) - (1-NPBS1.R)) < 5e-2
        elif INPUT_PORT == 2:
            assert ((R2.photon_count/10000) - NPBS1.R) < 5e-2
            assert ((R1.photon_count/10000) - (1-NPBS1.R)) < 5e-2
            
        R1.photon_count = 0
        R2.photon_count = 0