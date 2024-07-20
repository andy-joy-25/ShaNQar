# -*- coding: utf-8 -*-

import pytest
import numpy as np
import simpy
from ..src.components.photon import Photon
from ..src.utils.photon_enc import encoding

UID = 'p1'
WL = 2e-9
TWIDTH = 0.0
ENC_TYPE = 'Polarization'
COEFFS = np.array([[complex(1/2)],[complex(np.sqrt(3)/2)]])
BASIS = encoding['Polarization'][0]
SOURCE_LINEWIDTH = 0.01e-9

def test_init():
    p1 = Photon(UID,WL,TWIDTH,ENC_TYPE,COEFFS,BASIS)
    assert p1.uID == UID
    assert p1.wl == WL
    assert p1.twidth == TWIDTH
    assert p1.enc_type == ENC_TYPE
    assert np.allclose(p1.qs.coeffs,COEFFS)
    assert p1.qs.coeffs.shape == COEFFS.shape
    assert np.allclose(p1.qs.basis,BASIS)
    assert p1.qs.basis.shape == BASIS.shape
    
def test_set_source_linewidth():
    p1 = Photon(UID,WL,TWIDTH,ENC_TYPE,COEFFS,BASIS)
    p1.set_source_linewidth(SOURCE_LINEWIDTH)
    assert p1.source_lwidth == SOURCE_LINEWIDTH
    
def test_set_environment():
    ENV = simpy.Environment()
    p1 = Photon(UID,WL,TWIDTH,ENC_TYPE,COEFFS,BASIS)
    p1.set_environment(ENV)
    assert p1.env == ENV