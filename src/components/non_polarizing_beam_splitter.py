# -*- coding: utf-8 -*-

import numpy as np
from ..components.component import Component
from ..utils.photon_enc import encoding

class NonPolarizingBeamSplitter(Component):
    
    """
    Models a Non-Polarizing Beam Splitter
    
    Attributes:
        uID (str) = Unique ID
        env (simpy.Environment) = Simpy Environment for Simulation
        gen (numpy.random.Generator) = Random Number Generator
        R (float) = Reflectance of the Non-Polarizing Beam Splitter
        input_port_net (list[int]) = List of Input Port Numbers (only 1 and/or 2) of the Non-Polarizing Beam Splitter corresponding to the incoming Photons
        sender (QuantumChannel) = Sender of the Photon encoded with Quantum Information
        receivers (List[QuantumChannel]) = Receivers attached to the Non-Polarizing Beam Splitter to receive the reflected/transmitted Photon respectively
    """
    
    def __init__(self,uID,env,R):
        
        """
        Constructor for the NonPolarizingBeamSplitter class
        
        Arguments:
            uID (str) = Unique ID
            env (simpy.Environment) = Simpy Environment for Simulation
            R (float) = Reflectance of the Non-Polarizing Beam Splitter
        """
        
        Component.__init__(self,uID,env)
        self.R = R
        self.recd_p_net = []
        self.receival_complete = True
        
    def connect(self,senders,receivers):
        
        """
        Instance method to connect a non-polarizing beam splitter with its sender and receivers
        
        Arguments:
            sender (QuantumChannel) = Sender of the Photon encoded with Quantum Information
            receivers (List[QuantumChannel]) = Receivers attached to the Non-Polarizing Beam Splitter to receive the reflected/transmitted Photon respectively
        """
        
        self.senders = senders
        self.receivers = receivers
        if len(self.senders) == 2:
            self.receival_complete = False
        
    def set_input_port_connection(self,input_port_net):
            
        """
        Instance method to set the input port connection with the source
            
        Arguments:
            input_port_net (list[int]) = List of Input Port Numbers (only 1 and/or 2) of the Non-Polarizing Beam Splitter corresponding to the incoming Photons
        """
            
        self.input_port_net = input_port_net
    
    @staticmethod
    def set_ep_qstate(ep_qstate,t_qstate_coeffs,rand_idx):
        
        """
        Static method to set the quantum state of Bob's half of the Bell state post-BSM
        
        Arguments:
            ep_qstate (QuantumState) = Quantum State of Bob's half of the Bell State
            t_qstate_coeffs (numpy.array) = Coefficients of the Target Quantum State (State being teleported by Alice)
            rand_idx (int) = Index indicating the Bell State obtained via BSM
        """
        
        ep_qstate.basis = encoding['Polarization'][0]
        
        phi_plus = np.array([[complex(1/np.sqrt(2))],[complex(0)],[complex(0)],[complex(1/np.sqrt(2))]])
        phi_minus = np.array([[complex(1/np.sqrt(2))],[complex(0)],[complex(0)],[complex(-1/np.sqrt(2))]])
        psi_plus = np.array([[complex(0)],[complex(1/np.sqrt(2))],[complex(1/np.sqrt(2))],[complex(0)]])
        psi_minus = np.array([[complex(0)],[complex(1/np.sqrt(2))],[complex(-1/np.sqrt(2))],[complex(0)]])
        
        X = np.array([[complex(0),complex(1)],[complex(1),complex(0)]])
        Z = np.array([[complex(1),complex(0)],[complex(0),complex(-1)]])

        if np.allclose(ep_qstate.coeffs,phi_plus):
            
            if rand_idx == 0:
                ep_qstate.coeffs = t_qstate_coeffs
            elif rand_idx == 1:
                ep_qstate.coeffs = np.matmul(Z,t_qstate_coeffs)
            elif rand_idx == 2:
                ep_qstate.coeffs = np.matmul(X,t_qstate_coeffs)
            else:
                ep_qstate.coeffs = np.matmul(X,np.matmul(Z,t_qstate_coeffs))
        
        elif np.allclose(ep_qstate.coeffs,phi_minus):
            
            if rand_idx == 0:
                ep_qstate.coeffs = np.matmul(Z,t_qstate_coeffs)
            elif rand_idx == 1:
                ep_qstate.coeffs = t_qstate_coeffs
            elif rand_idx == 2:
                ep_qstate.coeffs = np.matmul(Z,np.matmul(X,t_qstate_coeffs))
            else:
                ep_qstate.coeffs = np.matmul(Z,np.matmul(X,np.matmul(Z,t_qstate_coeffs)))
                
        elif np.allclose(ep_qstate.coeffs,psi_plus):
            
            if rand_idx == 0:
                ep_qstate.coeffs = np.matmul(X,t_qstate_coeffs)
            elif rand_idx == 1:
                ep_qstate.coeffs = np.matmul(X,np.matmul(Z,t_qstate_coeffs))
            elif rand_idx == 2:
                ep_qstate.coeffs = t_qstate_coeffs
            else:
                ep_qstate.coeffs = np.matmul(Z,t_qstate_coeffs)
                
        elif np.allclose(ep_qstate.coeffs,psi_minus):
            
            if rand_idx == 0:
                ep_qstate.coeffs = np.matmul(X,np.matmul(Z,t_qstate_coeffs)) 
            elif rand_idx == 1:
                ep_qstate.coeffs = np.matmul(X,t_qstate_coeffs)
            elif rand_idx == 2:
                ep_qstate.coeffs = np.matmul(X,np.matmul(Z,np.matmul(X,t_qstate_coeffs)))
            else:
                ep_qstate.coeffs = np.matmul(X,np.matmul(Z,np.matmul(X,np.matmul(Z,t_qstate_coeffs))))
                     
    def receive(self,p_net):
        
        """
        Instance method to receive and consequently, direct incoming photon(s) to attached receiver(s) depending upon the reflectance (and transmittance) of the non-polarizing beam splitter 
        
        Arguments:
            p_net (photon) = Incoming Photon(s)
        """
        
        if len(self.senders) == 1:
            self.receival_complete = True
        
        if len(self.senders) == 2 and not self.receival_complete: # Photons (from the 2 senders) must arrive at the same time at the 2 input ports of the NPBS
           assert len(p_net) == 1
           self.recd_p_net.append(p_net[0])
           if len(self.recd_p_net) == 2:
               self.receival_complete = True
               self.receive(self.recd_p_net)
           else:
               self.receival_complete = False
        
        if self.receival_complete:
            
            self.recd_p_net = []
            self.receival_complete = False
            
            if len(p_net) == 1 or ((len(p_net) == 2) and ((((p_net[0] == None) or (p_net[1] == None))) or (((p_net[0] == None) and (p_net[1] == None))))): 
                
                pos = 2
                for i in range(len(p_net)):
                    if p_net[i] is not None:
                        pos = i
                
                rn = self.gen.random()
                if self.input_port_net[i] == 1:
                    if rn < self.R:
                        self.receivers[0].receive(p_net)
                    else:
                        self.receivers[1].receive(p_net)
                elif self.input_port_net[i] == 2:
                    if rn < self.R:
                        self.receivers[1].receive(p_net)
                    else:
                        self.receivers[0].receive(p_net)
                else:
                     print('ERROR: Incorrect input port number entered! Please enter either 1 or 2 only') 
                
            
            elif (len(p_net) == 2) and (p_net[0] != None) and (p_net[1] != None):
                
                assert self.input_port_net[0] != self.input_port_net[1]
                # Check whether the 2nd photon's quantum state is a 2 qubit state or not
                if len(p_net[1].qs.coeffs) == 4:
                    # Conversion to Z Basis for easier manipulation
                    p_net[1].qs.convert_to_coeffs_in_computational_basis()
                    # Ensure that the 2nd photon's quantum state is essentially an entangled state of the form of a Bell state
                    l = np.where(abs(p_net[1].qs.coeffs) > 1e-7)[0]
                    assert len(l) == 2
                    # Condense the entangled state to the state of only the 1st photon which is to be measured (for simulation purposes)
                    p_net[1].qs.coeffs = p_net[1].qs.coeffs[l]
                    p_net[1].qs.basis = encoding['Polarization'][0]
                
                # Conversion to Z Basis for easier manipulation
                p_net[0].qs.convert_to_coeffs_in_computational_basis()
                p_net[0].qs.basis = encoding['Polarization'][0]
                
                initial_tstate_qs_coeffs = p_net[0].qs.coeffs
                
                p_net[0].qs.product_state(p_net[1].qs)
                
                # Computation of the Bell State Probabilities
                phi_plus_prob = 0.5*np.square(np.abs(p_net[0].qs.coeffs[0][0] + p_net[0].qs.coeffs[3][0]))
                phi_minus_prob = 0.5*np.square(np.abs(p_net[0].qs.coeffs[0][0] - p_net[0].qs.coeffs[3][0]))
                psi_plus_prob = 0.5*np.square(np.abs(p_net[0].qs.coeffs[1][0] + p_net[0].qs.coeffs[2][0]))
                psi_minus_prob = 1 - (phi_plus_prob + phi_minus_prob + psi_plus_prob)
                
                probs = [phi_plus_prob,phi_minus_prob,psi_plus_prob,psi_minus_prob]
                
                rand_idx = self.gen.choice(np.arange(len(probs)),p = probs)
                
                coeffs_list = [[complex(1),complex(0)],[complex(0),complex(1)]]
                coeffs_list[0] = np.reshape(np.array(coeffs_list[0]),(len(coeffs_list[0]),1))
                coeffs_list[1] = np.reshape(np.array(coeffs_list[1]),(len(coeffs_list[1]),1))
                
                p_net[0].qs.basis = encoding['Polarization'][0]
                p_net[1].qs.basis = encoding['Polarization'][0]
                
                rn = self.gen.random()
                
                # phi_+ and phi_-
                if rand_idx == 0 or rand_idx == 1:
                    
                    sub_probs = [0.25,0.25,0.25,0.25]
                    rand_sub_idx = self.gen.choice(np.arange(len(sub_probs)),p = sub_probs)
                    
                    if rand_sub_idx == 0:
                        p_net[0].qs.coeffs = coeffs_list[0]
                        p_net[1].qs.coeffs = coeffs_list[0]
                        self.set_ep_qstate(p_net[1].qs.entangled_qs_list[0],initial_tstate_qs_coeffs,rand_idx)
                        self.receivers[0].receive(p_net)
                    elif rand_sub_idx == 1:
                        p_net[0].qs.coeffs = coeffs_list[0]
                        p_net[1].qs.coeffs = coeffs_list[0]
                        self.set_ep_qstate(p_net[1].qs.entangled_qs_list[0],initial_tstate_qs_coeffs,rand_idx)
                        self.receivers[1].receive(p_net)
                    elif rand_sub_idx == 2:
                        p_net[0].qs.coeffs = coeffs_list[1]
                        p_net[1].qs.coeffs = coeffs_list[1]
                        self.set_ep_qstate(p_net[1].qs.entangled_qs_list[0],initial_tstate_qs_coeffs,rand_idx)
                        self.receivers[0].receive(p_net)
                    else:
                        p_net[0].qs.coeffs = coeffs_list[1]
                        p_net[1].qs.coeffs = coeffs_list[1]
                        self.set_ep_qstate(p_net[1].qs.entangled_qs_list[0],initial_tstate_qs_coeffs,rand_idx)
                        self.receivers[1].receive(p_net)
                
                # psi_+
                elif rand_idx == 2:
                    
                    if rn < 0.50:
                        p_net[0].qs.coeffs = coeffs_list[0]
                        p_net[1].qs.coeffs = coeffs_list[1]
                        self.set_ep_qstate(p_net[1].qs.entangled_qs_list[0],initial_tstate_qs_coeffs,rand_idx)
                        self.receivers[0].receive(p_net)
                    else:
                        p_net[0].qs.coeffs = coeffs_list[0]
                        p_net[1].qs.coeffs = coeffs_list[1]
                        self.set_ep_qstate(p_net[1].qs.entangled_qs_list[0],initial_tstate_qs_coeffs,rand_idx)
                        self.receivers[1].receive(p_net)
                        
                # psi_-
                else:
                    
                    if rn < 0.50:
                        p_net[0].qs.coeffs = coeffs_list[0]
                        p_net[1].qs.coeffs = coeffs_list[1]
                        self.set_ep_qstate(p_net[1].qs.entangled_qs_list[0],initial_tstate_qs_coeffs,rand_idx)
                        for i in range(len(p_net)):
                            self.receivers[i].receive([p_net[i]])
                    else:
                        p_net[0].qs.coeffs = coeffs_list[0]
                        p_net[1].qs.coeffs = coeffs_list[1]
                        self.set_ep_qstate(p_net[1].qs.entangled_qs_list[0],initial_tstate_qs_coeffs,rand_idx)
                        for i in range(len(p_net)):
                            self.receivers[i].receive([p_net[-1-i]])
