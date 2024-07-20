# -*- coding: utf-8 -*-

import pytest
import numpy as np
import simpy
from ..src.utils.photon_enc import encoding
from ..src.components.SPDC import EntangledPhotonsSourceSPDC

phi_plus = np.array([[complex(1/np.sqrt(2))],[complex(0)],[complex(0)],[complex(1/np.sqrt(2))]])
phi_minus = np.array([[complex(1/np.sqrt(2))],[complex(0)],[complex(0)],[complex(-1/np.sqrt(2))]])
psi_plus = np.array([[complex(0)],[complex(1/np.sqrt(2))],[complex(1/np.sqrt(2))],[complex(0)]])
psi_minus = np.array([[complex(0)],[complex(1/np.sqrt(2))],[complex(-1/np.sqrt(2))],[complex(0)]])

ENV = simpy.Environment()
ENV1 = simpy.Environment()
ENV2 = simpy.Environment()
ENV_LIST = [ENV1,ENV2]
UID = 'EPS1'
PRR = 8e7
WL = 775e-9
LWIDTH = 0.01e-9
TWIDTH = 100e-15
MU_PHOTONS = 1e6
ENC_TYPE = 'Polarization'
NOISE_LEVEL = 0
GAMMA = 0.51
LAMBDA = 0.47
SPDC_TYPE = 2
BELL_LIKE_STATE = 'psi+'
CHI = 45
EFF = 1e-6

PER = 1e8

COEFFS = [[complex(1/2),complex(np.sqrt(3)/2)]]
BASIS = encoding['Polarization'][0]

class FakeReceiver():
    
    def __init__(self):
        self.p_net = []
    
    def receive(self,p):
        self.p_net.append(p)

def test_init():
    EPS1 = EntangledPhotonsSourceSPDC('EPS1',ENV,PRR,WL,LWIDTH,TWIDTH,MU_PHOTONS,ENC_TYPE,NOISE_LEVEL,GAMMA,LAMBDA,SPDC_TYPE,ENV_LIST,EFF)
    assert EPS1.uID == UID
    assert EPS1.SPDC_type == SPDC_TYPE
    assert EPS1.chi == CHI
    assert EPS1.mean_transmission_time == 1/PRR
    assert EPS1.p_twidth == TWIDTH
    assert EPS1.bell_like_state == BELL_LIKE_STATE
    assert EPS1.chi == CHI
    
def test_connect():
    R1 = FakeReceiver()
    R2 = FakeReceiver()
    R_net = [R1,R2]
    EPS1 = EntangledPhotonsSourceSPDC('EPS1',ENV,PRR,WL,LWIDTH,TWIDTH,MU_PHOTONS,ENC_TYPE,NOISE_LEVEL,GAMMA,LAMBDA,SPDC_TYPE,ENV_LIST,EFF)
    EPS1.connect(R_net)
    assert EPS1.receivers[0] == R1
    assert EPS1.receivers[1] == R2
    
def test_eff_and_coeff_values():
    EPS1 = EntangledPhotonsSourceSPDC('EPS1',ENV,PRR,WL,LWIDTH,TWIDTH,MU_PHOTONS,ENC_TYPE,NOISE_LEVEL,GAMMA,LAMBDA,SPDC_TYPE,ENV_LIST,EFF)
    R1 = FakeReceiver()
    R2 = FakeReceiver()
    R_net = [R1,R2]
    EPS1.connect(R_net)
    EPS1.emit_pp(COEFFS,BASIS,PER)
    num_pp = int(0.5*(len(R1.p_net) + len(R2.p_net)))
    assert abs((num_pp - EFF*MU_PHOTONS)) < 1e-5
    assert np.allclose(R1.p_net[0][0].qs.coeffs,psi_plus) and np.allclose(R2.p_net[0][0].qs.coeffs,psi_plus)
    
def test_noise_level():
    NOISE_LEVEL = 0.54
    MU_PHOTONS = 1e2
    EFF = 1e-2
    EPS1 = EntangledPhotonsSourceSPDC('EPS1',ENV,PRR,WL,LWIDTH,TWIDTH,MU_PHOTONS,ENC_TYPE,NOISE_LEVEL,GAMMA,LAMBDA,SPDC_TYPE,ENV_LIST,EFF)
    R1 = FakeReceiver()
    R2 = FakeReceiver()
    R_net = [R1,R2]
    EPS1.connect(R_net)
    corrupted_qs_count = 0
    for i in range(10000):
        EPS1.emit_pp(COEFFS,BASIS,PER)
        if not np.allclose(R1.p_net[0][0].qs.coeffs,psi_plus) and not np.allclose(R2.p_net[0][0].qs.coeffs,psi_plus):
            corrupted_qs_count += 1
        R1.p_net = []
        R2.p_net = []
    assert abs(((corrupted_qs_count/10000) - NOISE_LEVEL)) < 5e-2
    
def test_env_times_post_emission():
    ENV = simpy.Environment()
    ENV1 = simpy.Environment()
    ENV2 = simpy.Environment()
    ENV_LIST = [ENV1,ENV2]
    EPS1 = EntangledPhotonsSourceSPDC('EPS1',ENV,PRR,WL,LWIDTH,TWIDTH,MU_PHOTONS,ENC_TYPE,NOISE_LEVEL,GAMMA,LAMBDA,SPDC_TYPE,ENV_LIST,EFF)
    R1 = FakeReceiver()
    R2 = FakeReceiver()
    R_net = [R1,R2]
    EPS1.connect(R_net)
    EPS1.emit_pp(COEFFS,BASIS,PER)
    min_env_time = (1/PRR) - 5*TWIDTH
    max_env_time = (1/PRR) + 5*TWIDTH
    assert (ENV1.now >= min_env_time) and (ENV1.now <= max_env_time)
    assert (ENV2.now >= min_env_time) and (ENV2.now <= max_env_time)