# -*- coding: utf-8 -*-

import numpy as np
from ..components.photon import Photon
from ..components.component import Component

class Laser(Component):
    
    """
    Models a Laser
    
    Attributes:
        uID (str) = Unique ID
        env (simpy.Environment) = Simpy Environment for Simulation
        gen (numpy.random.Generator) = Random Number Generator 
        PRR (float) = Pulse Repetition Rate, i.e., the Frequency with which the Photon Pulses are emitted by the Laser
        wl (float) = Wavelength
        lwidth (float) = Linewidth 
        twidth (float) = Temporal Width
        mu_photons (int) = Mean Number of Photons
        enc_type (str) = Type of Quantum Information Encoding (see 'photon_enc.py') of the emitted Photons
        noise_level (float) = Probability of the Quantum State of the emitted Photons being altered because of Noise
        gamma (float) = Probability of losing a Photon
        lmda (float) =  Probability of a Photon getting scattered from the System (Without any Loss of Energy)
    """
    
    def __init__(self,uID,env,PRR,wl,lwidth,twidth,mu_photons,enc_type,noise_level,gamma,lmda):
        
        """
        Constructor for the Laser class
        
        Arguments:
            uID (str) = Unique ID
            env (simpy.Environment) = Simpy Environment for Simulation 
            PRR (float) = Pulse Repetition Rate, i.e., the Frequency with which the Photon Pulses are emitted by the Laser
            wl (float) = Wavelength
            lwidth (float) = Linewidth 
            twidth (float) = Temporal Width
            mu_photons (int) = Mean Number of Photons
            enc_type (str) = Type of Quantum Information Encoding (see 'photon_enc.py') of the emitted Photons
            noise_level (float) = Probability of the Quantum State of the emitted Photons being altered because of Noise
            gamma (float) = Probability of losing a Photon
            lmda (float) =  Probability of a Photon getting scattered from the System (Without any Loss of Energy)
        """
        
        Component.__init__(self,uID,env)
        self.PRR = PRR             
        self.wl = wl                 
        self.lwidth = lwidth         
        self.twidth = twidth         
        self.mu_photons = mu_photons 
        self.enc_type = enc_type     
        self.noise_level = noise_level 
        self.gamma = gamma
        self.lmda = lmda     
        
    def emit(self,qs_list,basis,PER):

        """
        Instance method for emitting photons
        
        Details:
            The number of photons emitted in every time period of the laser are determined by a Poisson distribution with its mean as the mean number of photons (mu_photons)
            Few photons maybe corrupted by a completely dissipative noise: amplitude and phase damping noise depending on the noise level (noise_level) of the laser
            The time period for pulse emission also factors into account the maximal (out of all the emitted photons) temporal width in the end
        
        Arguments:
            qs_list (list[list[complex]]) = List of the Sets of Quantum State Coefficients
            basis (numpy.array(list[list[complex]])) = Basis of the Quantum States
            PER (float) = Polarization Extinction Ratio, i.e., Transmission Ratio of the Wanted to the Unwanted component(s) of Polarization
            
        Returned Value:
            photons_net (list[list[Photon]]) = List of the Emitted Photons 
        """
        
        time_pd = 1/self.PRR

        photons_net = []

        for i,qs in enumerate(qs_list):
            qs_orig = np.reshape(np.array(qs),(len(qs),1))
            num_of_photons = self.gen.poisson(lam = self.mu_photons)
            qs_photons = []
            t_width_net_qs = []
            for j in range(num_of_photons):
                wl_p = self.wl + self.lwidth*self.gen.standard_normal()
                twidth_p = self.twidth*self.gen.standard_normal()
                t_width_net_qs.append(twidth_p)
                if self.gen.random() < (1/PER):
                    qs = np.ones(qs_orig.shape) - qs_orig
                else:
                    qs = qs_orig
                p = Photon(str(self.uID) + '_' + str(i) + '_' + str(j),wl_p,twidth_p,self.enc_type,qs,basis)
                p.set_source_linewidth(self.lwidth)
                if self.gen.random() < self.noise_level:
                    p.qs.dampen_phase_and_amplitude(self.gamma,self.lmda)
                qs_photons.append(p)
            photons_net.append(qs_photons)
            if len(t_width_net_qs) != 0:
                self.env.timeout(time_pd + max(t_width_net_qs))
            else:
                self.env.timeout(time_pd)
            self.env.run()
       
        return photons_net



