# -*- coding: utf-8 -*-

import pytest
import numpy as np
import simpy
from ..src.components.detector import Detector
from ..src.components.photon import Photon
from ..src.utils.photon_enc import encoding

#Detector
UID = 'D1'
DEAD_TIME = 1e-8
I_DET_EFF = 0.85
DARK_COUNT_RATE = 100
JITTER = 55e-12
NUMBER_RETURNED = 1

#Photon
UID_P = 'p1'
WL = 2e-9
TWIDTH = 0.0
ENC_TYPE = 'Polarization'
COEFFS = np.array([[complex(1/2)],[complex(np.sqrt(3)/2)]])
BASIS = encoding['Polarization'][0]

ENV = simpy.Environment()

class FakeSource():
    
    def __init__(self):
        pass

def test_init():
    D1 = Detector(UID,ENV,DEAD_TIME,I_DET_EFF,DARK_COUNT_RATE,JITTER,NUMBER_RETURNED)
    assert D1.uID == UID
    assert D1.dead_time == DEAD_TIME
    assert D1.det_eff == I_DET_EFF
    assert D1.dark_count_rate == DARK_COUNT_RATE
    assert D1.jitter == JITTER
    assert D1.num == NUMBER_RETURNED
    assert D1.set_adaptive_env == False
    
def test_connect():
    S = FakeSource()
    D1 = Detector(UID,ENV,DEAD_TIME,I_DET_EFF,DARK_COUNT_RATE,JITTER,NUMBER_RETURNED)
    D1.connect(S)
    assert D1.sender == S
    
def test_set_coupling_efficiency():
    D1 = Detector(UID,ENV,DEAD_TIME,I_DET_EFF,DARK_COUNT_RATE,JITTER,NUMBER_RETURNED)
    COUPLING_EFF = 0.90
    D1.set_coupling_efficiency(COUPLING_EFF)
    assert D1.coupling_eff == COUPLING_EFF
    
def test_set_measured_qstate_coeffs():
    D1 = Detector(UID,ENV,DEAD_TIME,I_DET_EFF,DARK_COUNT_RATE,JITTER,NUMBER_RETURNED)
    MEASURED_QSTATE_COEFFS = np.array([[complex(1)],[complex(0)]])
    D1.set_measured_qstate_coeffs(MEASURED_QSTATE_COEFFS)
    assert np.allclose(D1.measured_qs_coeffs,MEASURED_QSTATE_COEFFS)
    assert D1.measured_qs_coeffs.shape == MEASURED_QSTATE_COEFFS.shape
    
def test_set_environment():
    D1 = Detector(UID,ENV,DEAD_TIME,I_DET_EFF,DARK_COUNT_RATE,JITTER,NUMBER_RETURNED)
    ENV_TEST = simpy.Environment()
    D1.set_environment(ENV_TEST)
    assert D1.env == ENV_TEST
    
def test_clear_measurements():
    D1 = Detector(UID,ENV,DEAD_TIME,I_DET_EFF,DARK_COUNT_RATE,JITTER,NUMBER_RETURNED)
    D1.num_net = [NUMBER_RETURNED]
    D1.measured_qs_coeffs_net = [COEFFS]
    D1.detection_time_net = [1e-6]
    D1.clear_measurements()
    assert D1.num_net == []
    assert D1.measured_qs_coeffs_net == []
    assert D1.detection_time_net == []

def test_detection_efficiency():
    ENV = simpy.Environment()
    DEAD_TIME = 0
    DARK_COUNT_RATE = 0
    JITTER = 0
    D1 = Detector(UID,ENV,DEAD_TIME,I_DET_EFF,DARK_COUNT_RATE,JITTER,NUMBER_RETURNED)
    COUPLING_EFF = 1.0
    D1.set_coupling_efficiency(COUPLING_EFF)
    MEASURED_QSTATE_COEFFS = np.array([[complex(1)],[complex(0)]])
    D1.set_measured_qstate_coeffs(MEASURED_QSTATE_COEFFS)
    for i in range(10000):
        p = Photon(UID_P+str(i),WL,TWIDTH,ENC_TYPE,COEFFS,BASIS)
        p.set_environment(ENV)
        D1.receive([p])
        D1.clear_measurements()
    assert abs((D1.photon_count/10000) - D1.det_eff) < 5e-2
    
def test_coupling_efficiency():
    ENV = simpy.Environment()
    I_DET_EFF = 1
    DEAD_TIME = 0
    DARK_COUNT_RATE = 0
    JITTER = 0
    D1 = Detector(UID,ENV,DEAD_TIME,I_DET_EFF,DARK_COUNT_RATE,JITTER,NUMBER_RETURNED)
    COUPLING_EFF = 0.65
    D1.set_coupling_efficiency(COUPLING_EFF)
    MEASURED_QSTATE_COEFFS = np.array([[complex(1)],[complex(0)]])
    D1.set_measured_qstate_coeffs(MEASURED_QSTATE_COEFFS)
    for i in range(10000):
        p = Photon(UID_P+str(i),WL,TWIDTH,ENC_TYPE,COEFFS,BASIS)
        p.set_environment(ENV)
        D1.receive([p])
        D1.clear_measurements()
    assert abs((D1.photon_count/10000) - D1.coupling_eff) < 5e-2