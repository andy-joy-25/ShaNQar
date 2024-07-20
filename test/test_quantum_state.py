# -*- coding: utf-8 -*-

import pytest
import numpy as np
from ..src.utils.photon_enc import encoding
from ..src.components.quantum_state import QuantumState


def test_init():
    COEFFS = np.array([[complex(1/2)],[complex(np.sqrt(3)/2)]])
    BASIS = encoding['Polarization'][0]
    qs1 = QuantumState(COEFFS,BASIS)
    assert np.allclose(qs1.coeffs,COEFFS)
    assert qs1.coeffs.shape == COEFFS.shape
    assert np.allclose(qs1.basis,BASIS)
    assert qs1.basis.shape == BASIS.shape

def test_density_mat():
    COEFFS_LIST = [np.array([[complex(0)],[complex(1)]]),np.array([[complex(1/2)],[complex(np.sqrt(3)/2)]]),np.array([[complex(np.sqrt(3)/2)],[complex(np.sqrt(1)/2)]]),np.array([[complex(1)],[complex(0)]])]
    BASIS = encoding['Polarization'][0]
    DENSITY_MATRICES = [np.array([[complex(0),complex(0)],[complex(0),complex(1)]]),np.array([[complex(1/4),complex(np.sqrt(3)/4)],[complex(np.sqrt(3)/4),complex(3/4)]]),np.array([[complex(3/4),complex(np.sqrt(3)/4)],[complex(np.sqrt(3)/4),complex(1/4)]]),np.array([[complex(1),complex(0)],[complex(0),complex(0)]])]
    for coeffs,dmat in zip(COEFFS_LIST,DENSITY_MATRICES):
        qs1 = QuantumState(coeffs,BASIS)
        density_matrix = qs1.density_mat()
        assert np.allclose(density_matrix,dmat)
        assert density_matrix.shape == dmat.shape
    
def test_density_mat_to_ket():
    COEFFS_LIST = [np.array([[complex(0)],[complex(1)]]),np.array([[complex(1/2)],[complex(np.sqrt(3)/2)]]),np.array([[complex(np.sqrt(3)/2)],[complex(np.sqrt(1)/2)]]),np.array([[complex(1)],[complex(0)]])]
    BASIS = encoding['Polarization'][0]
    for coeffs in COEFFS_LIST:
        qs1 = QuantumState(coeffs,BASIS)
        ket = qs1.density_mat_to_ket(qs1.density_mat())
        assert np.allclose(ket,coeffs)
        assert ket.shape == coeffs.shape
    
def test_product_state():
    COEFFS_LIST = [np.array([[complex(0)],[complex(1)]]),np.array([[complex(1/2)],[complex(np.sqrt(3)/2)]]),np.array([[complex(np.sqrt(3)/2)],[complex(np.sqrt(1)/2)]]),np.array([[complex(1)],[complex(0)]])]
    BASIS = encoding['Polarization'][0]
    PRODUCT_STATE_LIST = [np.array([[complex(0)],[complex(0)],[complex(1/2)],[complex(np.sqrt(3)/2)]]),np.array([[complex(np.sqrt(3)/2)],[complex(0)],[complex(1/2)],[complex(0)]])]
    prod_state_list = []
    for i in range(0,len(COEFFS_LIST),2):
        qs1 = QuantumState(COEFFS_LIST[i],BASIS)
        qs2 = QuantumState(COEFFS_LIST[i+1],BASIS)
        qs1.product_state(qs2)
        prod_state_list.append(qs1.coeffs)
    for prs_calc,prs_act in zip(prod_state_list,PRODUCT_STATE_LIST):
        assert np.allclose(prs_calc,prs_act)
        assert prs_calc.shape == prs_act.shape
        
def test_measure_single_qubit_basis():
    COEFFS_LIST = [np.array([[complex(0)],[complex(1)]]),np.array([[complex(1/2)],[complex(np.sqrt(3)/2)]]),np.array([[complex(np.sqrt(3)/2)],[complex(np.sqrt(1)/2)]])]
    OWN_BASES = [encoding['Polarization'][1],encoding['Polarization'][0],encoding['Polarization'][2]]
    MEASUREMENT_BASES = [[encoding['Polarization'][1],encoding['Polarization'][2],encoding['Polarization'][0]],[encoding['Polarization'][0],encoding['Polarization'][1],encoding['Polarization'][2]],[encoding['Polarization'][2],encoding['Polarization'][0],encoding['Polarization'][1]]]
    THEO_PROB_LIST = [[0,0.5,0.5],[0.25,0.9330,0.5],[0.75,0.9330,0.5]]
    for coeffs,basis,mbases,theo_probs in zip(COEFFS_LIST,OWN_BASES,MEASUREMENT_BASES,THEO_PROB_LIST):
        for mbasis,theo_prob in zip(mbases,theo_probs):
            ctr0 = 0
            for i in range(10000):
                qs1 = QuantumState(coeffs,basis)
                qs1.measure_single_qubit_basis(mbasis)
                cmp_coeffs = np.reshape(np.array(encoding['Polarization'][0][0]),(encoding['Polarization'][0][0].size,1))
                if np.allclose(qs1.coeffs,cmp_coeffs) and np.allclose(qs1.basis,mbasis):
                    ctr0 += 1
            ctr0 /= 10000
            assert abs(ctr0 - theo_prob) <= 5e-2
            
def test_measure_multiple_qubit_basis_scheme1():
    COEFFS_LIST = [np.array([[complex(0)],[complex(0)],[complex(1/2)],[complex(np.sqrt(3)/2)]]),np.array([[complex(1/2)],[complex(1/2)],[complex(1/2)],[complex(1/2)]]),np.array([[complex(np.sqrt(3)/2)],[complex(0)],[complex(1/2)],[complex(0)]])]
    basisZZ = np.array([np.kron(encoding['Polarization'][0][0],encoding['Polarization'][0][0]),np.kron(encoding['Polarization'][0][0],encoding['Polarization'][0][1]),np.kron(encoding['Polarization'][0][1],encoding['Polarization'][0][0]),np.kron(encoding['Polarization'][0][1],encoding['Polarization'][0][1])])
    basisXX = np.array([np.kron(encoding['Polarization'][1][0],encoding['Polarization'][1][0]),np.kron(encoding['Polarization'][1][0],encoding['Polarization'][1][1]),np.kron(encoding['Polarization'][1][1],encoding['Polarization'][1][0]),np.kron(encoding['Polarization'][1][1],encoding['Polarization'][1][1])])
    basisYY = np.array([np.kron(encoding['Polarization'][2][0],encoding['Polarization'][2][0]),np.kron(encoding['Polarization'][2][0],encoding['Polarization'][2][1]),np.kron(encoding['Polarization'][2][1],encoding['Polarization'][2][0]),np.kron(encoding['Polarization'][2][1],encoding['Polarization'][2][1])])
    OWN_BASES = [basisXX,basisYY,basisZZ]
    MEASUREMENT_BASES = [[basisXX,basisYY,basisZZ],[basisYY,basisZZ,basisXX],[basisZZ,basisXX,basisYY]]
    CMP_COEFFS_LIST = [[basisZZ[3],basisZZ[0],basisZZ[2]],[basisZZ[1],basisZZ[0],basisZZ[2]],[basisZZ[0],basisZZ[1],basisZZ[3]]]
    THEO_PROB_LIST = [[0.75,0.25,0.4665],[0.25,1,0.25],[0.75,0.4665,0.25]]       
    for coeffs,basis,mbases,cmp_coeffs_list,theo_probs in zip(COEFFS_LIST,OWN_BASES,MEASUREMENT_BASES,CMP_COEFFS_LIST,THEO_PROB_LIST):
        for mbasis,cmp_coeffs,theo_prob in zip(mbases,cmp_coeffs_list,theo_probs):
            ctr0 = 0
            for i in range(10000):
                qs1 = QuantumState(coeffs,basis)
                qs1.measure_multiple_qubit_basis_scheme1(mbasis)
                cmp_coeffs = np.reshape(np.array(cmp_coeffs),(cmp_coeffs.size,1))
                if np.allclose(qs1.coeffs,cmp_coeffs) and np.allclose(qs1.basis,mbasis):
                    ctr0 += 1
            ctr0 /= 10000
            assert abs(ctr0 - theo_prob) <= 5e-2
                
def test_measure_multiple_qubit_basis_scheme2():
    COEFFS_LIST = [np.array([[complex(0)],[complex(0)],[complex(1/2)],[complex(np.sqrt(3)/2)]]),np.array([[complex(1/2)],[complex(1/2)],[complex(1/2)],[complex(1/2)]]),np.array([[complex(np.sqrt(3)/2)],[complex(0)],[complex(1/2)],[complex(0)]])]
    basisZZ = np.array([np.kron(encoding['Polarization'][0][0],encoding['Polarization'][0][0]),np.kron(encoding['Polarization'][0][0],encoding['Polarization'][0][1]),np.kron(encoding['Polarization'][0][1],encoding['Polarization'][0][0]),np.kron(encoding['Polarization'][0][1],encoding['Polarization'][0][1])])
    basisXX = np.array([np.kron(encoding['Polarization'][1][0],encoding['Polarization'][1][0]),np.kron(encoding['Polarization'][1][0],encoding['Polarization'][1][1]),np.kron(encoding['Polarization'][1][1],encoding['Polarization'][1][0]),np.kron(encoding['Polarization'][1][1],encoding['Polarization'][1][1])])
    basisYY = np.array([np.kron(encoding['Polarization'][2][0],encoding['Polarization'][2][0]),np.kron(encoding['Polarization'][2][0],encoding['Polarization'][2][1]),np.kron(encoding['Polarization'][2][1],encoding['Polarization'][2][0]),np.kron(encoding['Polarization'][2][1],encoding['Polarization'][2][1])])
    BASES = [basisXX,basisYY,basisZZ]     
    CMP_COEFFS_LIST = [np.array([[complex(0.965926)],[complex(-0.258819)],[complex(0)],[complex(0)]]),np.array([[complex(1)],[complex(0)],[complex(0)],[complex(0)]]),np.array([[complex(1)],[complex(0)],[complex(0)],[complex(0)]])]
    THEO_PROB_LIST = [0.5,1.0,0.75]
    for coeffs,basis,cmp_coeffs,theo_prob in zip(COEFFS_LIST,BASES,CMP_COEFFS_LIST,THEO_PROB_LIST):
        ctr0 = 0
        for i in range(10000):
            qs1 = QuantumState(coeffs,basis)
            qs1.measure_multiple_qubit_basis_scheme2()
            if np.allclose(qs1.coeffs,cmp_coeffs) and np.allclose(qs1.basis,basisZZ):
                ctr0 += 1
        ctr0 /= 10000
        assert abs(ctr0 - theo_prob) <= 5e-2
    
                
def test_measure_multiple_qubit_basis_scheme3():
    COEFFS_LIST = [np.array([[complex(0)],[complex(0)],[complex(1/2)],[complex(np.sqrt(3)/2)]]),np.array([[complex(1/2)],[complex(1/2)],[complex(1/2)],[complex(1/2)]]),np.array([[complex(np.sqrt(3)/2)],[complex(0)],[complex(1/2)],[complex(0)]])]
    basisZZ = np.array([np.kron(encoding['Polarization'][0][0],encoding['Polarization'][0][0]),np.kron(encoding['Polarization'][0][0],encoding['Polarization'][0][1]),np.kron(encoding['Polarization'][0][1],encoding['Polarization'][0][0]),np.kron(encoding['Polarization'][0][1],encoding['Polarization'][0][1])])
    basisXX = np.array([np.kron(encoding['Polarization'][1][0],encoding['Polarization'][1][0]),np.kron(encoding['Polarization'][1][0],encoding['Polarization'][1][1]),np.kron(encoding['Polarization'][1][1],encoding['Polarization'][1][0]),np.kron(encoding['Polarization'][1][1],encoding['Polarization'][1][1])])
    basisYY = np.array([np.kron(encoding['Polarization'][2][0],encoding['Polarization'][2][0]),np.kron(encoding['Polarization'][2][0],encoding['Polarization'][2][1]),np.kron(encoding['Polarization'][2][1],encoding['Polarization'][2][0]),np.kron(encoding['Polarization'][2][1],encoding['Polarization'][2][1])])
    BASES = [basisXX,basisYY,basisZZ]     
    CMP_COEFFS_LIST = [np.array([[complex(1/np.sqrt(2))],[complex(0)],[complex(-1/np.sqrt(2))],[complex(0)]]),np.array([[complex(1)],[complex(0)],[complex(0)],[complex(0)]]),np.array([[complex(np.sqrt(3)/2)],[complex(0)],[complex(1/2)],[complex(0)]])]
    THEO_PROB_LIST = [0.933,1.0,1.0]           
    for coeffs,basis,cmp_coeffs,theo_prob in zip(COEFFS_LIST,BASES,CMP_COEFFS_LIST,THEO_PROB_LIST):
        ctr0 = 0
        for i in range(10000):
            qs1 = QuantumState(coeffs,basis)
            qs1.measure_multiple_qubit_basis_scheme3()
            if np.allclose(qs1.coeffs,cmp_coeffs) and np.allclose(qs1.basis,basisZZ):
                ctr0 += 1
        ctr0 /= 10000
        assert abs(ctr0 - theo_prob) <= 5e-2 