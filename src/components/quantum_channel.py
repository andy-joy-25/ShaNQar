# -*- coding: utf-8 -*-

from ..components.component import Component

class QuantumChannel(Component):
    
    """
    Models a Quantum Channel (Fiber for the transmission of Quantum Information)
    
    Attributes:
        uID (str) = Unique ID
        env (simpy.Environment) = Simpy Environment for Simulation
        gen (numpy.random.Generator) = Random Number Generator
        length (float) = Length (in m)
        alpha (float) = Attenuation Coefficient (in dB/m)
        n_core (float) = Refractive Index of the Core
        pol_fidelity (float) = Polarization Fidelity (Probability of not undergoing Depolarization)
        chr_dispersion (float) = Chromatic Dispersion (in s/m-m)
        depol_prob (float) = Probability of suffering Depolarization
        sender (Laser or Weaklaser or EntangledPhotonsSourceSPDC) = Sender of Photons encoded with Quantum Information
        receiver (NonPolarizingBeamSplitter or PolarizingBeamSplitter or Mirror or WavePlate or Detector) = Receiver of the transmitted Photons
        coupling_eff (float) = Coupling Efficiency of the Source with the Quantum Channel
        set_adaptive_env (bool) = Boolean to control the Adaptive Environment Setting
        mean_transmission_time (float) = Mean Time taken by a Photon to cross the Length of the Quantum Channel
        trnmt (float) = Transmittance
    """

    def __init__(self,uID,env,length,alpha,n_core,pol_fidelity,chr_dispersion,depol_prob,set_adaptive_env = False):
        
        """
        Constructor for the QuantumChannel class
        
        Arguments:
            uID (str) = Unique ID
            env (simpy.Environment) = Simpy Environment for Simulation
            length (float) = Length (in m)
            alpha (float) = Attenuation Coefficient (in dB/m)
            n_core (float) = Refractive Index of the Core
            pol_fidelity (float) = Polarization Fidelity (Probability of not undergoing Depolarization)
            chr_dispersion (float) = Chromatic Dispersion (in s/m-m)
            depol_prob (float) = Probability of suffering Depolarization
            set_adaptive_env (bool) = Boolean to control the Adaptive Environment Setting
        """
        
        Component.__init__(self,uID,env)
        self.length = length                  
        self.alpha = alpha                  
        self.n_core = n_core                 
        self.pol_fidelity = pol_fidelity      
        self.chr_dispersion = chr_dispersion  
        self.depol_prob = depol_prob
        self.set_adaptive_env = set_adaptive_env
        c = 3e8
        self.mean_transmission_time = self.length/(c/self.n_core)
        self.trnmt = 10**((-self.alpha*self.length)/10)   
        
    def connect(self,sender,receiver):
        
        """
        Instance method to connect a quantum channel with its source and destination
        
        Arguments:
            sender (Laser or Weaklaser or EntangledPhotonsSourceSPDC) = Sender of Photons encoded with Quantum Information
            receiver (NonPolarizingBeamSplitter or PolarizingBeamSplitter or Mirror or WavePlate or Detector) = Receiver of the transmitted Photons
        """
        
        self.sender = sender
        self.receiver = receiver
        
    def set_coupling_efficiency(self,coupling_eff):
        
        """
        Instance method to set the coupling efficiency of a quantum channel
        
        Arguments:
            coupling_eff (float) = Coupling Efficiency (with the Source)
        """
        
        self.coupling_eff = coupling_eff
        
    def set_environment(self,env):
        
        """
        Instance method to set the environment of a quantum channel
        
        Arguments:
            env (Simpy.Environment) = Simpy Environment for Timing Control and Synchronisation 
        """
        
        self.env = env
        
    def calc_p_twidth(self,lwidth):
        
        """
        Instance method to compute the temporal width of a photon passing through a quantum channel
        """
        
        self.main_source_lwidth = lwidth
        self.p_twidth = self.chr_dispersion*self.main_source_lwidth*self.length 
        
    def receive(self,p_net):
        
        """
        Instance method to receive and consequently, transmit the photons emitted by the source
        
        Arguments:
            p (photon) = Photon emitted by the Source
        """
        
        for idx,p in enumerate(p_net):
            
            self.flag = False
            
            if p is not None:
                
                if self.set_adaptive_env:
                    self.set_environment(p.env)
                
                
                # Calculation of the temporal width of a transmitted photon
                self.p_twidth_qch = self.chr_dispersion*p.source_lwidth*self.length
                
                p.twidth += self.p_twidth_qch
                
                # Actual time taken by a photon to cross the length of the quantum channel (considering the effect of chromatic dispersion)
                transmission_time = self.mean_transmission_time + self.p_twidth_qch*self.gen.standard_normal()
               
                
                # Check if the probability of the photon being coupled into the fiber is less than the coupling efficiency and if that is the case, couple it into the fiber
                if self.gen.random() < self.coupling_eff:
                    # Check if the probability of the photon being transmitted by the fiber is less than the transmittance and if that is the case, transmit it
                    if self.gen.random() < self.trnmt:
                        # Check if the photon uses the polarization encoding scheme of quantum information and if the probability of the photon's polarization remaining unchanged due to noise is less than the polarization fidelity and if that is the case, return it without corrupting it with noise
                        if (p.enc_type != 'Polarization') or ((p.enc_type == 'Polarization') and (self.gen.random() < self.pol_fidelity)):
                            self.env.timeout(transmission_time)
                            self.env.run()
                            self.flag = True
                        else:
                            if self.gen.random() < 0.5:
                                # Rotate the polarization of the photon before transmitting it
                                p.qs.rotate_polarization()
                            else:
                                # Depolarize the photon before transmitting it
                                p.qs.depolarize(self.depol_prob)
                            self.env.timeout(transmission_time)
                            self.env.run()
                            self.flag = True
                    else:
                        self.env.timeout(transmission_time)
                        self.env.run()
                
                
                if not self.flag:
                    p_net[idx] = None
        
        self.receiver.receive(p_net)