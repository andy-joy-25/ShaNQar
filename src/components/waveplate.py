# -*- coding: utf-8 -*-

import numpy as np
from ..components.component import Component

class WavePlate(Component):
    
    """
    Models a General Wave Plate (Can be used as a Half-Wave Plate, Quarter-Wave Plate, etc.)
    
    Attributes:
        uID (str) = Unique ID
        env (simpy.Environment) = Simpy Environment for Simulation
        gen (numpy.random.Generator) = Random Number Generator
        alpha = Relative Phase Retardation introduced between the Fast and Slow Axes of the Birefringent Uniaxial Crystal (in degrees)
        theta = Angle made by the Fast Axis of the Birefringent Uniaxial Crystal with the Horizontal (in degrees)
    """
    
    def __init__(self,uID,env,alpha,theta):
        
        """
        Constructor for the WavePlate class
        
        Arguments:
            uID (str) = Unique ID
            env (simpy.Environment) = Simpy Environment for Simulation
            alpha = Relative Phase Retardation introduced between the Fast and Slow Axes of the Birefringent Uniaxial Crystal (in degrees)
            theta = Angle made by the Fast Axis of the Birefringent Uniaxial Crystal with the Horizontal (in degrees)
        """
        
        Component.__init__(self,uID,env)
        # Convert both angles to radians 
        self.alpha = np.deg2rad(alpha)
        self.theta = np.deg2rad(theta)
        
    def connect(self,sender,receiver):
        
        """
        Instance method to connect a wave plate with its sender and receiver
        
        Arguments:
            sender (QuantumChannel) = Sender of the Photon encoded with Quantum Information
            receiver (QuantumChannel) = Receiver attached to the Wave Plate to receive the transmitted Photon 
        """
        
        self.sender = sender
        self.receiver = receiver
    
    def receive(self,p_net):
        
        """
        Instance method to receive, alter the polarization of, and transmit an incoming photon
        
        Argument:
            p (photon) = Incoming Photon 
        """
        
        for idx,p in enumerate(p_net):
            
            if p is not None:
                
                # Jones Matrix Elements
                global_phase_factor = np.exp(-0.5*complex(0,self.alpha))
                M11 = np.square(np.cos(self.theta)) + np.exp(complex(0,self.alpha))*np.square(np.sin(self.theta))
                M12 = (1 - np.exp(complex(0,self.alpha)))*np.cos(self.theta)*np.sin(self.theta)
                M21 = (1 - np.exp(complex(0,self.alpha)))*np.cos(self.theta)*np.sin(self.theta)
                M22 = np.square(np.sin(self.theta)) + np.exp(complex(0,self.alpha))*np.square(np.cos(self.theta))
                
                # Jones Matrix for the Waveplate
                M = global_phase_factor*np.array([[M11,M12],[M21,M22]])
                
                p.qs.convert_to_coeffs_in_computational_basis()
                
                if p.qs.coeffs.size == 2:
                    p.qs.coeffs = np.matmul(M,p.qs.coeffs)
                elif p.qs.coeffs.size == 4:
                    if p.qs.ep_qubit_num == 1:
                        M = np.kron(M,np.eye(2))
                    else:
                        M = np.kron(np.eye(2),M)
                    p.qs.coeffs = np.matmul(M,p.qs.coeffs)
                    
                p.qs.convert_back_to_coeffs_in_original_basis()
        
        self.receiver.receive(p_net)
        
            
        
        
        