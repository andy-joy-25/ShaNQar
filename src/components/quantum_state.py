# -*- coding: utf-8 -*-

import numpy as np
import scipy.linalg
import warnings
from ..utils.photon_enc import encoding
warnings.filterwarnings('ignore')

class QuantumState():
    
    """
    Tracks and controls the Quantum State of a Photon
    
    Attributes:
        coeffs (list[complex]) = Coefficients 
        basis (numpy.array(list[list[complex]])) = Basis  
    """

    def __init__(self,coeffs,basis):
        
        """
        Constructor for the QuantumState class
        
        Arguments:
            coeffs (list[complex]) = Coefficients 
            basis (numpy.array(list[list[complex]])) = Basis  
        """
        
        self.coeffs = np.reshape(np.array(coeffs),(len(coeffs),1))
        self.basis = basis
        self.entangled_qs_list = []
        
    def convert_to_coeffs_in_computational_basis(self):
        
        """
        Instance method to convert to coefficients in the computational basis
        """
        
        if self.coeffs.size == 2:
            
            if np.allclose(self.basis,encoding['Polarization'][0]) and (self.basis.shape == encoding['Polarization'][0].shape):
                pass
            elif np.allclose(self.basis,encoding['Polarization'][1]) and (self.basis.shape == encoding['Polarization'][1].shape):
                self.coeffs = np.array([[complex(complex(1/np.sqrt(2))*complex(self.coeffs[0] + self.coeffs[1]))],[complex(complex(1/np.sqrt(2))*complex(self.coeffs[0] - self.coeffs[1]))]])
            elif np.allclose(self.basis,encoding['Polarization'][2]) and (self.basis.shape == encoding['Polarization'][2].shape):
                self.coeffs = np.array([[complex(complex(1/np.sqrt(2))*complex(self.coeffs[0] + self.coeffs[1]))],[complex(0,(complex(1/np.sqrt(2))*complex(self.coeffs[0] - self.coeffs[1])))]])
            
        elif self.coeffs.size == 4:
            
            basisZZ = np.array([np.kron(encoding['Polarization'][0][0],encoding['Polarization'][0][0]),np.kron(encoding['Polarization'][0][0],encoding['Polarization'][0][1]),np.kron(encoding['Polarization'][0][1],encoding['Polarization'][0][0]),np.kron(encoding['Polarization'][0][1],encoding['Polarization'][0][1])])
            basisXX = np.array([np.kron(encoding['Polarization'][1][0],encoding['Polarization'][1][0]),np.kron(encoding['Polarization'][1][0],encoding['Polarization'][1][1]),np.kron(encoding['Polarization'][1][1],encoding['Polarization'][1][0]),np.kron(encoding['Polarization'][1][1],encoding['Polarization'][1][1])])
            basisYY = np.array([np.kron(encoding['Polarization'][2][0],encoding['Polarization'][2][0]),np.kron(encoding['Polarization'][2][0],encoding['Polarization'][2][1]),np.kron(encoding['Polarization'][2][1],encoding['Polarization'][2][0]),np.kron(encoding['Polarization'][2][1],encoding['Polarization'][2][1])])
            
            if np.allclose(self.basis,basisZZ) and self.basis.shape == basisZZ.shape:
                pass
            elif np.allclose(self.basis,basisXX) and self.basis.shape == basisXX.shape:
                self.coeffs = np.array([[complex(complex(1/2)*complex(self.coeffs[0] + self.coeffs[1] + self.coeffs[2] + self.coeffs[3]))],[complex(complex(1/2)*complex(self.coeffs[0] - self.coeffs[1] + self.coeffs[2] - self.coeffs[3]))],[complex(complex(1/2)*complex(self.coeffs[0] + self.coeffs[1] - self.coeffs[2] - self.coeffs[3]))],[complex(complex(1/2)*complex(self.coeffs[0] - self.coeffs[1] - self.coeffs[2] + self.coeffs[3]))]])
            elif np.allclose(self.basis,basisYY) and self.basis.shape == basisYY.shape:
                self.coeffs = np.array([[complex(complex(1/2)*complex(self.coeffs[0] + self.coeffs[1] + self.coeffs[2] + self.coeffs[3]))],[complex(complex(0,(1/2))*complex(self.coeffs[0] - self.coeffs[1] + self.coeffs[2] - self.coeffs[3]))],[complex(complex(0,(1/2))*complex(self.coeffs[0] + self.coeffs[1] - self.coeffs[2] - self.coeffs[3]))],[complex(complex(1/2)*complex(-self.coeffs[0] + self.coeffs[1] + self.coeffs[2] - self.coeffs[3]))]])
            
    def convert_back_to_coeffs_in_original_basis(self):
        
        """
        Instance method to convert back to coefficients in the original basis
        """
        
        if self.coeffs.size == 2:
            
            if np.allclose(self.basis,encoding['Polarization'][0]) and (self.basis.shape == encoding['Polarization'][0].shape):
                pass
            elif np.allclose(self.basis,encoding['Polarization'][1]) and (self.basis.shape == encoding['Polarization'][1].shape):
                self.coeffs = np.array([[complex(complex(1/np.sqrt(2))*complex(self.coeffs[0] + self.coeffs[1]))],[complex(complex(1/np.sqrt(2))*complex(self.coeffs[0] - self.coeffs[1]))]])
            elif np.allclose(self.basis,encoding['Polarization'][2]) and (self.basis.shape == encoding['Polarization'][2].shape):
                self.coeffs = np.array([[(complex(complex(1/np.sqrt(2))*complex(self.coeffs[0]))) - (complex(0,(complex(1/np.sqrt(2))*complex(self.coeffs[1]))))],[(complex(complex(1/np.sqrt(2))*complex(self.coeffs[0]))) + (complex(0,(complex(1/np.sqrt(2))*complex(self.coeffs[1]))))]])
            
        elif self.coeffs.size == 4:
            
            basisZZ = np.array([np.kron(encoding['Polarization'][0][0],encoding['Polarization'][0][0]),np.kron(encoding['Polarization'][0][0],encoding['Polarization'][0][1]),np.kron(encoding['Polarization'][0][1],encoding['Polarization'][0][0]),np.kron(encoding['Polarization'][0][1],encoding['Polarization'][0][1])])
            basisXX = np.array([np.kron(encoding['Polarization'][1][0],encoding['Polarization'][1][0]),np.kron(encoding['Polarization'][1][0],encoding['Polarization'][1][1]),np.kron(encoding['Polarization'][1][1],encoding['Polarization'][1][0]),np.kron(encoding['Polarization'][1][1],encoding['Polarization'][1][1])])
            basisYY = np.array([np.kron(encoding['Polarization'][2][0],encoding['Polarization'][2][0]),np.kron(encoding['Polarization'][2][0],encoding['Polarization'][2][1]),np.kron(encoding['Polarization'][2][1],encoding['Polarization'][2][0]),np.kron(encoding['Polarization'][2][1],encoding['Polarization'][2][1])])
            
            if np.allclose(self.basis,basisZZ) and self.basis.shape == basisZZ.shape:
                pass
            elif np.allclose(self.basis,basisXX) and self.basis.shape == basisXX.shape:
                self.coeffs = np.array([[complex(complex(1/2)*complex(self.coeffs[0] + self.coeffs[1] + self.coeffs[2] + self.coeffs[3]))],[complex(complex(1/2)*complex(self.coeffs[0] - self.coeffs[1] + self.coeffs[2] - self.coeffs[3]))],[complex(complex(1/2)*complex(self.coeffs[0] + self.coeffs[1] - self.coeffs[2] - self.coeffs[3]))],[complex(complex(1/2)*complex(self.coeffs[0] - self.coeffs[1] - self.coeffs[2] + self.coeffs[3]))]])
            elif np.allclose(self.basis,basisYY) and self.basis.shape == basisYY.shape:
                self.coeffs = np.array([[(complex(complex(1/2)*complex(self.coeffs[0] - self.coeffs[3]))) - (complex(0,(complex(1/2)*complex(self.coeffs[1] + self.coeffs[2]))))],[(complex(complex(1/2)*complex(self.coeffs[0] + self.coeffs[3]))) + (complex(0,(complex(1/2)*complex(self.coeffs[1] - self.coeffs[2]))))],[(complex(complex(1/2)*complex(self.coeffs[0] + self.coeffs[3]))) + (complex(0,(complex(1/2)*complex(-self.coeffs[1] + self.coeffs[2]))))],[(complex(complex(1/2)*complex(self.coeffs[0] - self.coeffs[3]))) + (complex(0,(complex(1/2)*complex(self.coeffs[1] + self.coeffs[2]))))]])                
                
    def density_mat(self):
        
        """
        Instance method to compute the density matrix for a given quantum state in ket formalism
        
        Returned Value:
            dmat (numpy.array[complex]) = Density Matrix
        """
        
        self.convert_to_coeffs_in_computational_basis()
        dmat = np.outer(self.coeffs,np.conj(self.coeffs))
        self.convert_back_to_coeffs_in_original_basis()
        return dmat
    
    @staticmethod
    def density_mat_to_ket(dmat):
        
        """
        Static method to convert the density matrix into a possible corresponding state vector (ket)
        
        Argument:
            dmat (numpy.array[complex]) = Density Matrix
            
        Returned Value:
            egvec_with_max_egval (numpy.array[complex]) = State Vector (Ket) [Eigenvector of the Density Matrix with the Maximum Eigenvalue]
        """
        
        egval,egvec = np.linalg.eig(dmat)
        egvec_with_max_egval = egvec[:,np.argmax(egval)]
        egvec_with_max_egval = np.reshape(np.array(egvec_with_max_egval),(len(egvec_with_max_egval),1))
        return egvec_with_max_egval

    def trace_dist(self,qs2):
        
        """
        Instance method to compute the trace distance between the quantum state and another quantum state
        
        Argument:
            qs2 (list[complex]) = Coefficients of the Other Quantum State
            
        Returned Value:
            tdist (float) = Trace Distance between the 2 Quantum States 
        """
        
        assert np.allclose(self.basis,qs2.basis),'The bases of the 2 quantum states must be the same!'
        assert self.basis.shape == qs2.basis.shape,'The bases of the 2 quantum states must have the same dimensions!'
        
        rho = self.density_mat()
        sigma = qs2.density_mat()
        ddiff = rho - sigma
        ddiff_ct = np.transpose(np.conj(ddiff))
        res_mat = np.matmul(ddiff_ct,ddiff)
        res_mat_sq_root = np.abs(scipy.linalg.fractional_matrix_power(res_mat,0.5))
        tdist = 0.5*np.trace(res_mat_sq_root)
        return tdist
   
    def fidelity(self,qs2):
        
        """
        Instance method to compute the fidelity between the quantum state and another quantum state
        
        Argument:
            qs2 (list[complex]) = Coefficients of the Other Quantum State
            
        Returned Value:
            fdlty (float) = Fidelity between the 2 Quantum States
        """
        
        assert np.allclose(self.basis,qs2.basis),'The bases of the 2 quantum states must be the same!'
        assert self.basis.shape == qs2.basis.shape,'The bases of the 2 quantum states must have the same dimensions!'
        
        rho = self.density_mat()
        sigma = qs2.density_mat()
        rho_sq_root = np.abs(scipy.linalg.fractional_matrix_power(rho,0.5))
        res_mat = np.matmul(rho_sq_root,np.matmul(sigma,rho_sq_root))
        res_mat_sq_root = np.abs(scipy.linalg.fractional_matrix_power(res_mat,0.5))
        fdlty = np.trace(res_mat_sq_root)
        return fdlty

    def rotate_polarization(self):
        
        """
        Instance method to rotate the polarization-based quantum state  
        """
        
        rand_angle = np.random.rand()*2*np.pi
        
        self.convert_to_coeffs_in_computational_basis()
        
        if self.coeffs.size == 2:
            
            if np.allclose(self.basis,encoding['Polarization'][0]) and (self.basis.shape == encoding['Polarization'][0].shape):
                R = np.array([[complex(np.exp(complex(0,-0.5*rand_angle))),complex(0)],[complex(0),complex(np.exp(complex(0,0.5*rand_angle)))]])
            elif np.allclose(self.basis,encoding['Polarization'][1]) and (self.basis.shape == encoding['Polarization'][1].shape):
                R = np.array([[complex(np.cos(0.5*rand_angle)),complex(0,(-1*np.sin(0.5*rand_angle)))],[complex(0,(-1*np.sin(0.5*rand_angle))),complex(np.cos(0.5*rand_angle))]])
            elif np.allclose(self.basis,encoding['Polarization'][2]) and (self.basis.shape == encoding['Polarization'][2].shape):
                R = np.array([[complex(np.cos(0.5*rand_angle)),complex(-1*np.sin(0.5*rand_angle))],[complex(np.sin(0.5*rand_angle)),complex(np.cos(0.5*rand_angle))]])
                
        elif self.coeffs.size == 4:
            
            basisZZ = np.array([np.kron(encoding['Polarization'][0][0],encoding['Polarization'][0][0]),np.kron(encoding['Polarization'][0][0],encoding['Polarization'][0][1]),np.kron(encoding['Polarization'][0][1],encoding['Polarization'][0][0]),np.kron(encoding['Polarization'][0][1],encoding['Polarization'][0][1])])
            basisXX = np.array([np.kron(encoding['Polarization'][1][0],encoding['Polarization'][1][0]),np.kron(encoding['Polarization'][1][0],encoding['Polarization'][1][1]),np.kron(encoding['Polarization'][1][1],encoding['Polarization'][1][0]),np.kron(encoding['Polarization'][1][1],encoding['Polarization'][1][1])])
            basisYY = np.array([np.kron(encoding['Polarization'][2][0],encoding['Polarization'][2][0]),np.kron(encoding['Polarization'][2][0],encoding['Polarization'][2][1]),np.kron(encoding['Polarization'][2][1],encoding['Polarization'][2][0]),np.kron(encoding['Polarization'][2][1],encoding['Polarization'][2][1])])
            
            if np.allclose(self.basis,basisZZ) and self.basis.shape == basisZZ.shape:
                R = np.array([[complex(np.exp(complex(0,-0.5*rand_angle))),complex(0)],[complex(0),complex(np.exp(complex(0,0.5*rand_angle)))]])
                R = np.kron(R,R)
            elif np.allclose(self.basis,basisXX) and self.basis.shape == basisXX.shape:
                R = np.array([[complex(np.cos(0.5*rand_angle)),complex(0,(-1*np.sin(0.5*rand_angle)))],[complex(0,(-1*np.sin(0.5*rand_angle))),complex(np.cos(0.5*rand_angle))]])
                R = np.kron(R,R)
            elif np.allclose(self.basis,basisYY) and self.basis.shape == basisYY.shape:
                R = np.array([[complex(np.cos(0.5*rand_angle)),complex(-1*np.sin(0.5*rand_angle))],[complex(np.sin(0.5*rand_angle)),complex(np.cos(0.5*rand_angle))]])
                R = np.kron(R,R)
        
        self.coeffs = np.matmul(R,self.coeffs)
        self.convert_back_to_coeffs_in_original_basis()

    def depolarize(self,prob):

        """
        Instance method to add depolarization (non-dissipative) noise to the quantum state 
        
        Argument:
            prob (float) = Probability of suffering Depolarization
        """

        dmat = self.density_mat()
        
        if self.coeffs.size == 2:
            depol_dm = 0.5*prob*np.eye(2) + (1 - prob)*dmat
        elif self.coeffs.size == 4:
            depol_dm = 0.25*prob*np.eye(4) + (1 - prob)*dmat
        
        self.coeffs = self.density_mat_to_ket(depol_dm)
        self.convert_back_to_coeffs_in_original_basis()

    def dampen_amplitude(self,gamma):

        """
        Instance method to add amplitude damping (dissipative) noise to the quantum state
        
        Argument:
            gamma (float) = Probability of losing a Photon
        """
        
        E = [0,0]
        E[0] = np.array([[complex(1),complex(0)],[complex(0),complex(np.sqrt(1-gamma))]])
        E[1] = np.array([[complex(0),complex(np.sqrt(gamma))],[complex(0),complex(0)]])
        
        if self.coeffs.size == 2:
            amp_damp_dmat = np.zeros((2,2))
            for e in range(len(E)):
                amp_damp_dmat = amp_damp_dmat + np.matmul(E[e],np.matmul(self.density_mat(),np.transpose(E[e].conj())))
        
        elif self.coeffs.size == 4:
            E_N = [[0,0],[0,0]]
            for i in range(2):
                for j in range(2):
                    E_N[i][j] = np.kron(E[i],E[j])
            amp_damp_dmat = np.zeros((4,4))    
            for er in range(2):
                for ec in range(2):
                    amp_damp_dmat = amp_damp_dmat + np.matmul(E_N[er][ec],np.matmul(self.density_mat(),np.transpose(E_N[er][ec].conj())))
         
        self.coeffs = self.density_mat_to_ket(amp_damp_dmat)
        self.convert_back_to_coeffs_in_original_basis()

    def dampen_phase(self,lmda):

        """
        Instance method to add phase damping (dissipative) noise to the quantum state (randomization of phase)
        
        Argument:
            lmda (float) =  Probability of a Photon getting scattered from the System (Without any Loss of Energy) 
        """
        
        E = [0,0]
        E[0] = np.array([[complex(1),complex(0)],[complex(0),complex(np.sqrt(1-lmda))]])
        E[1] = np.array([[complex(0),complex(0)],[complex(0),complex(np.sqrt(lmda))]])
        
        if self.coeffs.size == 2:
            phase_damp_dmat = np.zeros((2,2))
            for e in range(len(E)):
                phase_damp_dmat =  phase_damp_dmat + np.matmul(E[e],np.matmul(self.density_mat(),np.transpose(E[e].conj())))
        
        elif self.coeffs.size == 4:
            E_N = [[0,0],[0,0]]
            for i in range(2):
                for j in range(2):
                    E_N[i][j] = np.kron(E[i],E[j])
            phase_damp_dmat = np.zeros((4,4))        
            for er in range(2):
                for ec in range(2):
                    phase_damp_dmat = phase_damp_dmat + np.matmul(E_N[er][ec],np.matmul(self.density_mat(),np.transpose(E_N[er][ec].conj())))
            
        self.coeffs = self.density_mat_to_ket(phase_damp_dmat)
        self.convert_back_to_coeffs_in_original_basis()
        
    def dampen_phase_and_amplitude(self,gamma,lmda):

        """
        Instance method to add amplitude as well as phase damping (dissipative) noise (complete decoherence) to the quantum state
        
        Arguments:
            gamma (float) = Probability of losing a Photon
            lmda (float) =  Probability of a Photon getting scattered from the System (Without any Loss of Energy)
        """
        
        self.dampen_amplitude(gamma)
        self.dampen_phase(lmda)

    def product_state(self,qs2):
        
        """
        Instance method to form the product state given 2 quantum states
            
        Argument:
            qs2 (qstate) = The Other Quantum State
        """
        
        assert np.allclose(self.basis,qs2.basis),'The bases of the 2 quantum states must be the same!'
        assert self.basis.shape == qs2.basis.shape,'The bases of the 2 quantum states must have the same dimensions!'

        product_state_coeffs = np.array(np.kron(self.coeffs,qs2.coeffs))
        self.coeffs = product_state_coeffs
        self.coeffs = np.reshape(np.array(self.coeffs),(self.coeffs.size,1))
        self.basis = np.array([np.kron(self.basis[0],self.basis[0]),np.kron(self.basis[0],self.basis[1]),np.kron(self.basis[1],self.basis[0]),np.kron(self.basis[1],self.basis[1])])
        qs2.coeffs = product_state_coeffs
        qs2.coeffs = np.reshape(np.array(qs2.coeffs),(qs2.coeffs.size,1))
        qs2.basis = self.basis
        
    def entangle_with(self,qs2):
        
        """
        Instance method to keep track of photons in an entangled pair
        """
        
        self.ep_qubit_num = 1
        qs2.ep_qubit_num = 2
        self.entangled_qs_list.append(qs2)
        qs2.entangled_qs_list.append(self)
            
    def measure_single_qubit_basis(self,mbasis):
        
        """
        Instance method to measure the quantum state of a single photon with a given basis as the measurement basis
        
        Arguments:
            mbasis (numpy.array(list[list[complex]])) = Measurement Basis
        """
        
        if np.allclose(self.basis,mbasis) and (self.basis.shape == mbasis.shape):
            prob_0 = self.coeffs[0]*np.conj(self.coeffs[0])
            rn = np.random.rand()
            if rn < prob_0:
                self.coeffs = encoding['Polarization'][0][0]
                self.coeffs = np.reshape(np.array(self.coeffs),(self.coeffs.size,1))
            else:
                self.coeffs = encoding['Polarization'][0][1]
                self.coeffs = np.reshape(np.array(self.coeffs),(self.coeffs.size,1))
        else:
            v1 = np.transpose(np.array([mbasis[0]], dtype = complex))
            M_0 = np.outer(v1,np.conj(v1))
            
            psi = np.array([[self.coeffs[0]*self.basis[0][0] + self.coeffs[1]*self.basis[1][0]],[self.coeffs[0]*self.basis[0][1] + self.coeffs[1]*self.basis[1][1]]]).reshape((2,1))
            
            prob_0 = ((np.matmul(np.matmul(np.transpose(np.conj(psi)),np.transpose(np.conj(M_0))),np.matmul(M_0,psi))).real.astype(dtype = float)).item()
            
            rn = np.random.rand()
            if rn < prob_0:
                self.coeffs = encoding['Polarization'][0][0]
                self.coeffs = np.reshape(np.array(self.coeffs),(self.coeffs.size,1))
                self.basis = mbasis
            else:
                self.coeffs = encoding['Polarization'][0][1]
                self.coeffs = np.reshape(np.array(self.coeffs),(self.coeffs.size,1))
                self.basis = mbasis
    
    def measure_multiple_qubit_basis_scheme1(self,mbasis):
        
        """
        Instance method implementing the 1st scheme of measurement of a (product/entangled) quantum state in a multiple qubit basis
        
        Details of Scheme 1: Random Projective Measurement to either one of the basis vectors of the given measurement basis
        """
        
        basisZZ = np.array([np.kron(encoding['Polarization'][0][0],encoding['Polarization'][0][0]),np.kron(encoding['Polarization'][0][0],encoding['Polarization'][0][1]),np.kron(encoding['Polarization'][0][1],encoding['Polarization'][0][0]),np.kron(encoding['Polarization'][0][1],encoding['Polarization'][0][1])])
        basisXX = np.array([np.kron(encoding['Polarization'][1][0],encoding['Polarization'][1][0]),np.kron(encoding['Polarization'][1][0],encoding['Polarization'][1][1]),np.kron(encoding['Polarization'][1][1],encoding['Polarization'][1][0]),np.kron(encoding['Polarization'][1][1],encoding['Polarization'][1][1])])
        basisYY = np.array([np.kron(encoding['Polarization'][2][0],encoding['Polarization'][2][0]),np.kron(encoding['Polarization'][2][0],encoding['Polarization'][2][1]),np.kron(encoding['Polarization'][2][1],encoding['Polarization'][2][0]),np.kron(encoding['Polarization'][2][1],encoding['Polarization'][2][1])])
        
        if np.allclose(self.basis,mbasis) and (self.basis.shape == mbasis.shape):
            probs = [np.square(coeff.real).astype(dtype = float).item() for coeff in self.coeffs]
            new_coeffs = basisZZ
            
            gen = np.random.default_rng()
            rand_idx = gen.choice(np.arange(len(probs)),p = probs)
            
            self.coeffs = new_coeffs[rand_idx]
            self.coeffs = np.reshape(np.array(self.coeffs),(self.coeffs.size,1))
        else:
            psi = np.array([[self.coeffs[0]*self.basis[0][0] + self.coeffs[1]*self.basis[1][0] + self.coeffs[2]*self.basis[2][0] + self.coeffs[3]*self.basis[3][0]],[self.coeffs[0]*self.basis[0][1] + self.coeffs[1]*self.basis[1][1] + self.coeffs[2]*self.basis[2][1] + self.coeffs[3]*self.basis[3][1]],[self.coeffs[0]*self.basis[0][2] + self.coeffs[1]*self.basis[1][2] + self.coeffs[2]*self.basis[2][2] + self.coeffs[3]*self.basis[3][2]],[self.coeffs[0]*self.basis[0][3] + self.coeffs[1]*self.basis[1][3] + self.coeffs[2]*self.basis[2][3] + self.coeffs[3]*self.basis[3][3]]]).reshape((4,1))
            
            probs = []
            new_coeffs = basisZZ
            for i,b in enumerate(mbasis):
                v = np.transpose(np.array([b], dtype = complex))
                M = np.outer(v,np.conj(v))
                probs.append(((np.matmul(np.matmul(np.transpose(np.conj(psi)),np.transpose(np.conj(M))),np.matmul(M,psi))).real.astype(dtype = float)).item())

            gen = np.random.default_rng()
            rand_idx = gen.choice(np.arange(len(probs)),p = probs)
            
            self.coeffs = new_coeffs[rand_idx]
            self.coeffs = np.reshape(np.array(self.coeffs),(self.coeffs.size,1))
            self.basis = mbasis
            
    def measure_multiple_qubit_basis_scheme2(self):
        
        """
        Instance method implementing the 2nd scheme of measurement of a (product/entangled) quantum state in a multiple (here, = 2) qubit basis
        
        Details of Scheme 2: Random Projective Measurement based on the probability of the 1st qubit being equal to the 1st basis vector of the computational basis
        """

        basisZZ = np.array([np.kron(encoding['Polarization'][0][0],encoding['Polarization'][0][0]),np.kron(encoding['Polarization'][0][0],encoding['Polarization'][0][1]),np.kron(encoding['Polarization'][0][1],encoding['Polarization'][0][0]),np.kron(encoding['Polarization'][0][1],encoding['Polarization'][0][1])])
        
        self.convert_to_coeffs_in_computational_basis()
        self.basis = basisZZ
      
        v1 = np.transpose(np.array([encoding['Polarization'][0][0]], dtype = complex))
        v2 = np.transpose(np.array([encoding['Polarization'][0][1]], dtype = complex))
        P_0 = np.outer(v1,np.conj(v1))
        P_1 = np.outer(v2,np.conj(v2))
        M_0_sup1 = np.kron(P_0,np.identity(2))
        M_1_sup1 = np.kron(P_1,np.identity(2))
        prob_0_sup1 = ((np.matmul(np.matmul(np.transpose(np.conj(self.coeffs)),np.transpose(np.conj(M_0_sup1))),np.matmul(M_0_sup1,self.coeffs))).real.astype(dtype = float)).item()
        rn = np.random.rand()
        if rn < prob_0_sup1:
            self.coeffs = np.transpose(np.matmul(M_0_sup1,self.coeffs)/np.sqrt(prob_0_sup1))
            self.coeffs = np.reshape(np.array(self.coeffs),(self.coeffs.size,1))
        else:
            self.coeffs = np.transpose(np.matmul(M_1_sup1,self.coeffs)/np.sqrt(1 - prob_0_sup1))
            self.coeffs = np.reshape(np.array(self.coeffs),(self.coeffs.size,1))
            
    def measure_multiple_qubit_basis_scheme3(self):
        
        """
        Instance method implementing the 3rd scheme of measurement of a (product/entangled) quantum state in a multiple (here, = 2) qubit basis
        
        Details of Scheme 3: Random Projective Measurement based on the probability of the 2nd qubit being equal to the 1st basis vector of the computational basis
        """
        
        basisZZ = np.array([np.kron(encoding['Polarization'][0][0],encoding['Polarization'][0][0]),np.kron(encoding['Polarization'][0][0],encoding['Polarization'][0][1]),np.kron(encoding['Polarization'][0][1],encoding['Polarization'][0][0]),np.kron(encoding['Polarization'][0][1],encoding['Polarization'][0][1])])

        self.convert_to_coeffs_in_computational_basis()
        self.basis = basisZZ

        v1 = np.transpose(np.array([encoding['Polarization'][0][0]], dtype = complex))
        v2 = np.transpose(np.array([encoding['Polarization'][0][1]], dtype = complex))
        P_0 = np.outer(v1,np.conj(v1))
        P_1 = np.outer(v2,np.conj(v2))
        M_0_sup2 = np.kron(np.identity(2),P_0)
        M_1_sup2 = np.kron(np.identity(2),P_1)
        prob_0_sup2 = ((np.matmul(np.matmul(np.transpose(np.conj(self.coeffs)),np.transpose(np.conj(M_0_sup2))),np.matmul(M_0_sup2,self.coeffs))).real.astype(dtype = float)).item()
        rn = np.random.rand()
        if rn < prob_0_sup2:
            self.coeffs = np.transpose(np.matmul(M_0_sup2,self.coeffs)/np.sqrt(prob_0_sup2))
            self.coeffs = np.reshape(np.array(self.coeffs),(self.coeffs.size,1))
        else:
            self.coeffs = np.transpose(np.matmul(M_1_sup2,self.coeffs)/np.sqrt(1 - prob_0_sup2))
            self.coeffs = np.reshape(np.array(self.coeffs),(self.coeffs.size,1))


