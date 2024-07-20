# -*- coding: utf-8 -*-

import numpy as np
from ..components.component import Component
from ..utils.photon_enc import encoding

class PolarizingBeamSplitter(Component):
    
    """
    Models a Polarizing Beam Splitter
    
    Attributes:
        uID (str) = Unique ID
        env (simpy.Environment) = Simpy Environment for Simulation
        gen (numpy.random.Generator) = Random Number Generator
        ER (float) = Extinction Ratio (Horizontal Polarization Transmission/Vertical Polarization Transmission)
        R (float) = Reflectance of the Polarizing Beam Splitter (determined via the Polarization State of the incoming Photon)
        input_port (int) = The Input Port of the Polarizing Beam Splitter which receives the incoming Photon
        sender (QuantumChannel) = Sender of the Photon encoded with Quantum Information
        receivers (List[QuantumChannel]) = Receivers attached to the Polarizing Beam Splitter to receive the reflected/transmitted Photon respectively
    """
    
    def __init__(self,uID,env,ER):
        
        """
        Constructor for the PolarizingBeamSplitter class
        
        Arguments:
            uID (str) = Unique ID
            env (simpy.Environment) = Simpy Environment for Simulation
            ER (float) = Extinction Ratio (Horizontal Polarization Transmission/Vertical Polarization Transmission)
        """
        
        Component.__init__(self,uID,env)
        self.ER = ER
        
    def connect(self,sender,receivers):
        
        """
        Instance method to connect a polarizing beam splitter with its sender and receivers
        
        Arguments:
            sender (QuantumChannel) = Sender of the Photon encoded with Quantum Information
            receivers (List[QuantumChannel]) = Receivers attached to the Polarizing Beam Splitter to receive the reflected/transmitted Photon respectively
        """
        
        self.sender = sender
        self.receivers = receivers
        
    def set_input_port_connection(self,input_port):
            
        """
        Instance method to set the input port connection with the source
            
        Arguments:
            input_port (int) = The Input Port of the Polarizing Beam Splitter which receives the incoming Photon
        """
            
        self.input_port = input_port
            
        
    def receive(self,p_net):
        
        """
        Instance method to receive and consequently, direct an incoming photon to one of two attached receivers depending upon the reflectance (and transmittance) of the polarizing beam splitter 
        
        Arguments:
            p_net (photon) = Incoming photon(s)
        """
        
        coeffs_list = [[complex(1),complex(0)],[complex(0),complex(1)]]
        coeffs_list[0] = np.reshape(np.array(coeffs_list[0]),(len(coeffs_list[0]),1))
        coeffs_list[1] = np.reshape(np.array(coeffs_list[1]),(len(coeffs_list[1]),1))
        
        self.receiver_idx_list = []
        
        for p in p_net:
            
            if p is not None:
                
                rn = self.gen.random()
                rn_ER = self.gen.random()
                
                p.qs.convert_to_coeffs_in_computational_basis()
                
                # Dealing with the case when a single photon in an entangled quantum state is incident on the PBS
                if p.qs.coeffs.size == 4:
                    l = np.where(abs(p.qs.coeffs) > 1e-7)[0]
                    if p.qs.ep_qubit_num == 1:
                        p.qs.coeffs = p.qs.coeffs[l]
                    else:
                        if np.allclose(l,[0,3]):# phi_+ and phi_-
                            p.qs.coeffs = p.qs.coeffs[l]
                        elif np.allclose(l,[1,2]):# psi_+ and psi_-
                            p.qs.coeffs = np.flip(p.qs.coeffs[l])
                            
                p.qs.basis = encoding['Polarization'][0]
                self.R = np.square(np.abs(p.qs.coeffs[1]))
                
                if self.input_port == 1:
                    if rn_ER >= 1/self.ER:
                        if rn < self.R:
                            p.qs.coeffs = coeffs_list[1]
                            self.receiver_idx_list.append(0)
                        else:
                            p.qs.coeffs = coeffs_list[0]
                            self.receiver_idx_list.append(1)
                    else:
                        if rn < self.R:
                            p.qs.coeffs = coeffs_list[0]
                            self.receiver_idx_list.append(1)
                        else:
                            p.qs.coeffs = coeffs_list[1]
                            self.receiver_idx_list.append(0)
                            
                elif self.input_port == 2:
                    self.R = 1 - self.R
                    if rn_ER >= 1/self.ER:
                        if rn < self.R:
                            p.qs.coeffs = coeffs_list[0]
                            self.receiver_idx_list.append(1)
                        else:
                            p.qs.coeffs = coeffs_list[1]
                            self.receiver_idx_list.append(0)
                    else:
                        if rn < self.R:
                            p.qs.coeffs = coeffs_list[1]
                            self.receiver_idx_list.append(0)
                        else:
                            p.qs.coeffs = coeffs_list[0]
                            self.receiver_idx_list.append(1)
                        
                else:
                     print('ERROR: Incorrect input port number entered! Please enter either 1 or 2 only') 
                     
            else:
                self.receiver_idx_list.append(self.gen.choice([0,1]))
        
        p_net = np.array(p_net)
        self.receiver_idx_list == np.array(self.receiver_idx_list)
        
        p0 = p_net[np.where(self.receiver_idx_list == 0)[0]]
    
        p1 = p_net[np.where(self.receiver_idx_list == 1)[0]]
        
        if len(p0) == len(p_net):
            self.receivers[0].receive(p_net)
        
        elif len(p1) == len(p_net):
            self.receivers[1].receive(p_net)
        
        else:
            for i in range(len(p_net)):
                self.receivers[self.receiver_idx_list[i]].receive([p_net[i]])