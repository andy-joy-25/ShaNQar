# -*- coding: utf-8 -*-

import pytest
import simpy
import numpy as np
from ..src.components.laser import Laser
from ..src.utils.photon_enc import encoding
from iteration_utilities import deepflatten

ENV = simpy.Environment()
UID = 'L1'
PRR = 8e7
WL = 1550e-9
LWIDTH = 0.01e-9
TWIDTH = 100e-15
MU_PHOTONS = 0.1
ENC_TYPE = 'Polarization'
NOISE_LEVEL = 0
GAMMA = 0.4
LAMBDA = 0.3

PER = 500

COEFFS = [[complex(1/2),complex(np.sqrt(3)/2)]]
BASIS = encoding['Polarization'][0]

CHK_COEFFS = np.array([[complex(1/2)],[complex(np.sqrt(3)/2)]])

def test_init():
    L1 = Laser(UID,ENV,PRR,WL,LWIDTH,TWIDTH,MU_PHOTONS,ENC_TYPE,NOISE_LEVEL,GAMMA,LAMBDA)
    assert L1.uID == UID
    assert L1.PRR == PRR
    assert L1.wl == WL
    assert L1.lwidth == LWIDTH
    assert L1.twidth == TWIDTH
    assert L1.mu_photons == MU_PHOTONS
    assert L1.enc_type == ENC_TYPE
    assert L1.noise_level == NOISE_LEVEL
    assert L1.gamma == GAMMA
    assert L1.lmda == LAMBDA

def test_mean_number_of_photons():
    L1 = Laser(UID,ENV,PRR,WL,LWIDTH,TWIDTH,MU_PHOTONS,ENC_TYPE,NOISE_LEVEL,GAMMA,LAMBDA)
    n_photons_total = []
    for i in range(10000):
        L1_photons_net = list(deepflatten(L1.emit(COEFFS,BASIS,PER)))
        n_photons_total.append(len(L1_photons_net))
    act_mu_photons = sum(n_photons_total)/len(n_photons_total)
    assert abs(act_mu_photons - MU_PHOTONS) < 5e-2
    
def test_noise_level():
    NOISE_LEVEL = 0.07
    MU_PHOTONS = 1e5
    PER = 1e7
    L1 = Laser(UID,ENV,PRR,WL,LWIDTH,TWIDTH,MU_PHOTONS,ENC_TYPE,NOISE_LEVEL,GAMMA,LAMBDA)
    n_corrupted_photons = 0
    L1_photons_net = list(deepflatten(L1.emit(COEFFS,BASIS,PER)))
    for p in L1_photons_net:
        if not np.allclose(p.qs.coeffs,CHK_COEFFS):
            n_corrupted_photons += 1
    act_corrupted_photons = n_corrupted_photons/len(L1_photons_net)
    assert abs(act_corrupted_photons - NOISE_LEVEL) < 5e-3
    
def test_PER():
    NOISE_LEVEL = 0
    MU_PHOTONS = 1e5
    PER = 500
    L1 = Laser(UID,ENV,PRR,WL,LWIDTH,TWIDTH,MU_PHOTONS,ENC_TYPE,NOISE_LEVEL,GAMMA,LAMBDA)
    n_corrupted_photons = 0
    L1_photons_net = list(deepflatten(L1.emit(COEFFS,BASIS,PER)))
    for p in L1_photons_net:
        if not np.allclose(p.qs.coeffs,CHK_COEFFS):
            n_corrupted_photons += 1
    act_corrupted_photons = n_corrupted_photons/len(L1_photons_net)
    assert abs(act_corrupted_photons - (1/PER)) < 5e-3
    
def test_env_time_post_emission():
    ENV_test = simpy.Environment()
    MU_PHOTONS = 1e5
    L1 = Laser(UID,ENV_test,PRR,WL,LWIDTH,TWIDTH,MU_PHOTONS,ENC_TYPE,NOISE_LEVEL,GAMMA,LAMBDA)
    L1_photons_net = list(deepflatten(L1.emit(COEFFS,BASIS,PER)))
    twidth_net = []
    for p in L1_photons_net:
        twidth_net.append(p.twidth)
    assert abs(L1.env.now - max(twidth_net) - 1/PRR) < 1e-12