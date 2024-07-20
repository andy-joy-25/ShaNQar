# -*- coding: utf-8 -*-

import warnings
from ..components.quantum_state import QuantumState
warnings.filterwarnings('ignore')

class Photon():
    
    """
    Models a photon
    
    Attributes:
        uID (str) = Unique ID
        wl (float) = Wavelength
        twidth (float) = Temporal Width
        enc_type (str) = Type of Quantum Information Encoding (see 'photon_enc.py') 
        qs (QuantumState) = Quantum State 
        source_lwidth (float) = Linewidth of the Source that generated the Photon
    """

    def __init__(self,uID,wl,twidth,enc_type,coeffs,basis):
        
        """
        Constructor for the Photon class
        
        Arguments:
            uID (str) = Unique ID
            wl (float) = Wavelength
            twidth (float) = Temporal Width
            enc_type (str) = Type of Quantum Information Encoding (see 'photon_enc.py') 
            coeffs (list[complex]) = Quantum State Coefficients 
            basis (numpy.array(list[list[complex]])) = Quantum State Basis 
        """
        
        self.uID = uID
        self.wl = wl                  
        self.twidth = twidth          
        self.enc_type = enc_type       
        self.qs = QuantumState(coeffs,basis) 
        
    def set_source_linewidth(self,s_lwidth):
        
        """
        Instance method to save the linewidth of the source that generated the photon
        
        Arguments:
            s_lwidth (float) = Linewidth of the Source that generated the Photon
        """
        
        self.source_lwidth = s_lwidth
        
    def set_environment(self,env):
        
        """
        Instance method to set the environment of a photon
        
        Arguments:
            env (Simpy.Environment) = Simpy Environment for the timing control and synchronisation of the photon (required when multiple photons are to be sent simultaneously) 
        """
        
        self.env = env
