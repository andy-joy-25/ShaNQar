# -*- coding: utf-8 -*-

import pytest
import numpy as np
import simpy
from ..src.utils.photon_enc import encoding
from ..src.components.photon import Photon
from ..src.components.quantum_channel import QuantumChannel

#Quantum Channel
UID = 'QC1'
ENV = simpy.Environment()
LENGTH = 1000
ALPHA = 0.2e-3
N_CORE = 1.50
POL_FIDELITY = 0.25
CHR_DISPERSION = 17e-6
DEPOL_PROB = 0.7

c = 3e8

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
    qc1 = QuantumChannel(UID,ENV,LENGTH,ALPHA,N_CORE,POL_FIDELITY,CHR_DISPERSION,DEPOL_PROB)
    assert qc1.uID == UID
    assert qc1.length == LENGTH
    assert qc1.alpha == ALPHA
    assert qc1.n_core == N_CORE
    assert qc1.pol_fidelity == POL_FIDELITY
    assert qc1.chr_dispersion == CHR_DISPERSION
    assert qc1.depol_prob == DEPOL_PROB
    assert qc1.set_adaptive_env == False
    assert qc1.mean_transmission_time == LENGTH/(c/N_CORE)
    assert qc1.trnmt == 10**((-ALPHA*LENGTH)/10) 
    
def test_connect():
    S = FakeSource()
    R = FakeReceiver()
    qc1 = QuantumChannel(UID,ENV,LENGTH,ALPHA,N_CORE,POL_FIDELITY,CHR_DISPERSION,DEPOL_PROB)
    qc1.connect(S,R)
    assert qc1.sender == S
    assert qc1.receiver == R
    
def test_set_coupling_efficiency():
    qc1 = QuantumChannel(UID,ENV,LENGTH,ALPHA,N_CORE,POL_FIDELITY,CHR_DISPERSION,DEPOL_PROB)
    COUPLING_EFF = 0.86
    qc1.set_coupling_efficiency(COUPLING_EFF)
    assert qc1.coupling_eff == COUPLING_EFF
    
def test_set_env():
    qc1 = QuantumChannel(UID,ENV,LENGTH,ALPHA,N_CORE,POL_FIDELITY,CHR_DISPERSION,DEPOL_PROB)
    ENV_TEST = simpy.Environment()
    qc1.set_environment(ENV_TEST)
    assert qc1.env == ENV_TEST
    
def test_calc_p_twidth():
    qc1 = QuantumChannel(UID,ENV,LENGTH,ALPHA,N_CORE,POL_FIDELITY,CHR_DISPERSION,DEPOL_PROB)
    LWIDTH = 0.01e-9
    qc1.calc_p_twidth(LWIDTH)
    assert qc1.main_source_lwidth == LWIDTH
    assert qc1.p_twidth == CHR_DISPERSION*LWIDTH*LENGTH
    
def test_coupling_efficiency():
    ALPHA = 0
    POL_FIDELITY = 1
    qc1 = QuantumChannel(UID,ENV,LENGTH,ALPHA,N_CORE,POL_FIDELITY,CHR_DISPERSION,DEPOL_PROB)
    COUPLING_EFF = 0.67
    qc1.set_coupling_efficiency(COUPLING_EFF)
    S = FakeSource()
    SOURCE_LINEWIDTH = 0.01e-9
    R = FakeReceiver()
    qc1.connect(S,R)
    p_net_tr = 0
    for i in range(10000):
        p = Photon(UID_P+str(i),WL,TWIDTH,ENC_TYPE,COEFFS,BASIS)
        p.set_source_linewidth(SOURCE_LINEWIDTH)
        p.set_environment(ENV)
        qc1.receive([p])
        if R.p_net_rcd[0] is not None:
            p_net_tr += 1
        R.p_net_rcd = []
    assert abs((p_net_tr/10000) - COUPLING_EFF) < 5e-2

def test_transmittance():
    qc1 = QuantumChannel(UID,ENV,LENGTH,ALPHA,N_CORE,POL_FIDELITY,CHR_DISPERSION,DEPOL_PROB)
    TRANSMITTANCE = 10**((-ALPHA*LENGTH)/10) 
    COUPLING_EFF = 1.0
    qc1.set_coupling_efficiency(COUPLING_EFF)
    S = FakeSource()
    SOURCE_LINEWIDTH = 0.01e-9
    R = FakeReceiver()
    qc1.connect(S,R)
    p_net_tr = 0
    for i in range(10000):
        p = Photon(UID_P+str(i),WL,TWIDTH,ENC_TYPE,COEFFS,BASIS)
        p.set_source_linewidth(SOURCE_LINEWIDTH)
        p.set_environment(ENV)
        qc1.receive([p])
        if R.p_net_rcd[0] is not None:
            p_net_tr += 1
        R.p_net_rcd = []
    assert abs((p_net_tr/10000) - TRANSMITTANCE) < 5e-2
    
def test_polarization_fidelity_and_transmission_time():
    ALPHA = 0
    POL_FIDELITY = 0.78
    qc1 = QuantumChannel(UID,ENV,LENGTH,ALPHA,N_CORE,POL_FIDELITY,CHR_DISPERSION,DEPOL_PROB)
    COUPLING_EFF = 1
    qc1.set_coupling_efficiency(COUPLING_EFF)
    S = FakeSource()
    SOURCE_LINEWIDTH = 0.01e-9
    R = FakeReceiver()
    qc1.connect(S,R)
    p_net_uncorrupted = 0
    for i in range(10000):
        p = Photon(UID_P+str(i),WL,TWIDTH,ENC_TYPE,COEFFS,BASIS)
        p.set_source_linewidth(SOURCE_LINEWIDTH)
        p.set_environment(ENV)
        start_time = ENV.now
        qc1.receive([p])
        end_time = ENV.now
        #99.7% of the normally distributed data lies between 3 standard deviations of the mean. (We take a factor of 5 instead just for some cushioning)
        assert qc1.mean_transmission_time - 5*(CHR_DISPERSION*SOURCE_LINEWIDTH*LENGTH + TWIDTH) <= (end_time - start_time) <= qc1.mean_transmission_time + 5*(CHR_DISPERSION*SOURCE_LINEWIDTH*LENGTH + TWIDTH)
        if R.p_net_rcd[0].qs.coeffs[0][0] == COEFFS[0][0] and R.p_net_rcd[0].qs.coeffs[1][0] == COEFFS[1][0]:
            p_net_uncorrupted += 1
        R.p_net_rcd = []
    assert abs((p_net_uncorrupted/10000) - POL_FIDELITY) < 5e-2
    
def test_adaptive_env_setting():
    ENV = simpy.Environment()
    SET_ADAPTIVE_ENV = True
    SOURCE_LINEWIDTH = 0
    TWIDTH = 0
    ALPHA = 0
    qc1 = QuantumChannel(UID,ENV,LENGTH,ALPHA,N_CORE,POL_FIDELITY,CHR_DISPERSION,DEPOL_PROB,SET_ADAPTIVE_ENV)
    COUPLING_EFF = 1
    qc1.set_coupling_efficiency(COUPLING_EFF)
    S = FakeSource()
    R = FakeReceiver()
    qc1.connect(S,R)
    ENV1 = simpy.Environment()
    ENV1.timeout(1.25e-8)
    ENV1.run()
    ENV2 = simpy.Environment()
    ENV2.timeout(3.75e-8)
    ENV2.run()
    p1 = Photon(UID_P,WL,TWIDTH,ENC_TYPE,COEFFS,BASIS)
    p1.set_source_linewidth(SOURCE_LINEWIDTH)
    p1.set_environment(ENV1)
    UID_P2 = 'p2'
    p2 = Photon(UID_P2,WL,TWIDTH,ENC_TYPE,COEFFS,BASIS)
    p2.set_source_linewidth(SOURCE_LINEWIDTH)
    p2.set_environment(ENV2)
    qc1.receive([p1,p2])
    assert ENV.now == 0
    assert ENV1.now == 1.25e-8 + LENGTH/(c/N_CORE)
    assert ENV2.now == 3.75e-8 + LENGTH/(c/N_CORE)