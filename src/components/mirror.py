# -*- coding: utf-8 -*-

from ..components.component import Component

class Mirror(Component):
    
    """
    Models a Mirror
    
    Attributes:
        uID (str) = Unique ID
        env (simpy.Environment) = Simpy Environment for Simulation
        gen (numpy.random.Generator) = Random Number Generator
        reflectivity (float) = Reflectivity of the Mirror
        noise_level (float) = Probability of the Quantum State of the incoming Photon being altered because of Noise
        gamma (float) = Probability of losing a Photon
        lmda (float) =  Probability of a Photon getting scattered from the System (Without any Loss of Energy)
    """
    
    def __init__(self,uID,env,reflectivity,noise_level,gamma,lmda):
        
        """
        Constructor for the Mirror class
        
        Arguments:
            uID (str) = Unique ID
            env (simpy.Environment) = Simpy Environment for Simulation
            reflectivity (float) = Reflectivity of the Mirror
            noise_level (float) = Probability of the Quantum State of the incoming Photon being altered because of Noise
            gamma (float) = Probability of losing a Photon
            lmda (float) =  Probability of a Photon getting scattered from the System (Without any Loss of Energy)
        """
        
        Component.__init__(self,uID,env)
        self.reflectivity = reflectivity
        self.noise_level = noise_level
        self.gamma = gamma
        self.lmda = lmda
        
    def connect(self,sender,receiver):
         
        """
        Instance method to connect a mirror with its sender and receiver
         
        Arguments:
            sender (QuantumChannel) = Sender of the Photon encoded with Quantum Information
            receiver (QuantumChannel) = Receiver attached to the Mirror to receive the reflected Photon 
        """
         
        self.sender = sender
        self.receiver = receiver
        
    def receive(self,p_net):
        
        """
        Instance method to receive and reflect the incoming photon
        
        Argument:
            p (photon) = Incoming Photon 
        """
        
        for idx,p in enumerate(p_net):
            
            self.flag = False
            
            if p is not None:
                
                # Check if the probability of the photon being reflected by the mirror is less than its reflectivity and if that is the case, reflect it
                if self.gen.random() < self.reflectivity:
                    # Check if the probability of the photon's quantum state being corrupted by dissipative noise is less than its noise level and if that is the case, corrupt its quantum state with dissipative noise
                    if self.gen.random() < self.noise_level:
                        p.qs.dampen_phase_and_amplitude(self.gamma,self.lmda)
                        self.flag = True
                    else:
                        self.flag = True
            
                if not self.flag:
                    p_net[idx] = None
                
        self.receiver.receive(p_net)
            
        
                
                