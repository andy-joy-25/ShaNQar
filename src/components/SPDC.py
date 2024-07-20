# -*- coding: utf-8 -*-

import numpy as np
import simpy
from iteration_utilities import deepflatten
from ..components.photon import Photon
from ..components.laser import Laser


class EntangledPhotonsSourceSPDC(Laser):
    
    """
    Models a Spontaneous Parametric Down Conversion (SPDC) based Source which emits entangled photons (photons in entangled quantum states with an [optional] intrinsic degree of entanglement [= epsilon])
    
    References: 
        1. A. G. White, D. F. V. James, P. H. Eberhard, and P. G. Kwiat, "Non-maximally entangled states: production, characterization and utilization," Phys. Rev. Lett., vol. 83, no. 16, pp. 3103-3107, 1999
        2. P. G. Kwiat, K. Mattle, H. Weinfurter, A. Zeilinger, A. V. Sergienko, and Y. Shih, "New high-intensity source of polarization-entangled photon pairs," Phys. Rev. Lett., vol. 75, no. 24, pp. 4337 - 4341, 1995
    
    Attributes:
        uID (str) = Unique ID
        env (simpy.Environment) = Simpy Environment for Simulation
        gen (numpy.random.Generator) = Random Number Generator 
        PRR (float) = Pulse Repetition Rate, i.e., the Frequency with which the Photon Pulses are emitted by the Laser
        wl (float) = Wavelength of the Laser
        lwidth (float) = Linewidth of the Laser
        twidth (float) = Temporal Width of the Laser
        mu_photons (int) = Mean Number of Photons emitted by the Laser
        enc_type (str) = Type of Quantum Information Encoding (see 'photon_enc.py') of the Photons emitted by the Laser
        noise_level (float) = Probability of the Quantum State of the Photons emitted by the Laser being altered because of Noise
        gamma (float) = Probability of losing a Photon
        lmda (float) =  Probability of a Photon getting scattered from the System (Without any Loss of Energy)
        SPDC_type (int) = Type of SPDC (1 or 2) which determines the Final Bell/Bell-like State of the emitted Photons
        bell_like_state (str)  = Form of the Entangled Quantum State of the SPDC Photons specified in terms of a Bell State 
        envt_list (list[simpy.Environment]) = List of Simpy Environments to be respectively assigned to each Photon in an emitted Photon Pair
        efficiency (float) = Pair Production Efficiency of the SPDC process (in generated pairs per incident photons)
        chi (float) = Angle of the Pump Laser's Polarization w.r.t. the Vertical Axis
    """

    def __init__(self,uID,env,PRR,wl,lwidth,twidth,mu_photons,enc_type,noise_level,gamma,lmda,SPDC_type,envt_list,efficiency,chi = 45):
        
        """
        Constructor for the EntangledPhotonsSourceSPDC class
        
        Arguments:
            uID (str) = Unique ID
            env (simpy.Environment) = Simpy Environment for Simulation
            PRR (float) = Pulse Repetition Rate, i.e., the Frequency with which the Photon Pulses are emitted by the Laser
            wl (float) = Wavelength of the Laser
            lwidth (float) = Linewidth of the Laser
            twidth (float) = Temporal Width of the Laser
            mu_photons (int) = Mean Number of Photons emitted by the Laser
            enc_type (str) = Type of Quantum Information Encoding (see 'photon_enc.py') of the Photons emitted by the Laser
            noise_level (float) = Probability of the Quantum State of the Photons emitted by the Laser being altered because of Noise
            gamma (float) = Probability of losing a Photon
            lmda (float) =  Probability of a Photon getting scattered from the System (Without any Loss of Energy)
            SPDC_type (int) = Type of SPDC (1 or 2) which determines the Final Bell/Bell-like State of the emitted Photons
            envt_list (list[simpy.Environment]) = List of Simpy Environments to be respectively assigned to each Photon in an emitted Photon Pair
            efficiency (float) = Pair Production Efficiency of the SPDC process (in generated pairs per incident photons)
            chi (float) = Angle of the Pump Laser's Polarization w.r.t. the Vertical Axis
        """
        
        Laser.__init__(self,uID,env,PRR,wl,lwidth,twidth,mu_photons,enc_type,noise_level,gamma,lmda)
        self.uID = uID                   # Unique ID of the Entangled Photons Source based on SPDC
        self.SPDC_type = SPDC_type 
        self.envt_list = envt_list
        self.efficiency = efficiency     
        self.chi = chi                   
        self.mean_transmission_time = 1/PRR
        self.p_twidth = twidth
        if self.SPDC_type == 2:
            self.bell_like_state = 'psi+'
            self.chi = 45 #To ensure entanglement is always maximal
        else:
            self.bell_like_state = 'phi+'
            
    def connect(self,receivers):
        
        """
        Instance method to connect an Entangled Photon Pair Source based on SPDC with its receivers
        
        Arguments:
            receivers (list[QuantumChannel]) = Receivers attached to the Entangled Photon Pair Source to receive and transmit Photon(s)
        """
        
        self.receivers = receivers

    def SPDC_entangled_states(self,p1,p2):
        
        """
        Instance method for setting the quantum states of the photons as the entangled quantum states (with an [optional] intrinsic degree of entanglement) 
        
        Arguments:
            p1 (photon) = First Photon born out of the SPDC Process
            p2 (photon) = Second Photon born out of the SPDC Process
        """
        
        p1.qs.basis = np.array([np.kron(p1.qs.basis[0],p1.qs.basis[0]),np.kron(p1.qs.basis[0],p1.qs.basis[1]),np.kron(p1.qs.basis[1],p1.qs.basis[0]),np.kron(p1.qs.basis[1],p1.qs.basis[1])])
        p2.qs.basis = p1.qs.basis
        chi_rad = np.radians(self.chi)
        epsilon = np.tan(chi_rad)
        norm_den = np.sqrt(1 + np.square(epsilon))
        if self.bell_like_state == 'phi+':
           p1.qs.coeffs = [complex(1/norm_den),complex(0/norm_den),complex((epsilon*0)/norm_den),complex((epsilon*1)/norm_den)]
           p1.qs.coeffs = np.reshape(np.array(p1.qs.coeffs),(len(p1.qs.coeffs),1))
           p2.qs.coeffs = p1.qs.coeffs
           p1.qs.entangle_with(p2.qs)
        elif self.bell_like_state == 'phi-':
           p1.qs.coeffs = [complex(1/norm_den),complex(0/norm_den),complex(-1*(epsilon*0)/norm_den),complex(-1*(epsilon*1)/norm_den)]
           p1.qs.coeffs = np.reshape(np.array(p1.qs.coeffs),(len(p1.qs.coeffs),1))
           p2.qs.coeffs = p1.qs.coeffs
           p1.qs.entangle_with(p2.qs)
        elif self.bell_like_state == 'psi+':
           p1.qs.coeffs = [complex(0/norm_den),complex(1/norm_den),complex((epsilon*1)/norm_den),complex((epsilon*0)/norm_den)]
           p1.qs.coeffs = np.reshape(np.array(p1.qs.coeffs),(len(p1.qs.coeffs),1))
           p2.qs.coeffs = p1.qs.coeffs
           p1.qs.entangle_with(p2.qs)
        elif self.bell_like_state == 'psi-':
           p1.qs.coeffs = [complex(0/norm_den),complex(1/norm_den),complex(-1*(epsilon*1)/norm_den),complex(-1*(epsilon*0)/norm_den)]
           p1.qs.coeffs = np.reshape(np.array(p1.qs.coeffs),(len(p1.qs.coeffs),1))
           p2.qs.coeffs = p1.qs.coeffs
           p1.qs.entangle_with(p2.qs)
        else:
            print('ERROR: Typed the wrong bell like state')


    def emit_pp(self,qs_list,basis,PER):
        
        """
        Instance method for emitting entangled photon pairs generated via the SPDC process
        
        Details:
            The number of pump photons that can successfully undergo SPDC to give rise to pairs of photons is decided by the pair production efficiency of the SPDC process
            Additionally, pump photons are randomly successfully down converted to give rise to pairs of photons
        
        Arguments:
            qs_list (list[list[complex]]) = List of the Sets of Quantum State Coefficients of the Photons emitted by the Laser
            basis (numpy.array(list[list[complex]])) = Basis of the Quantum States of the Photons emitted by the Laser
            PER (float) = Polarization Extinction Ratio, i.e., Transmission Ratio of the Wanted to the Unwanted Component(s) of Polarization
            
        Returned Value:
            ephotons_net (list[list[list[Photon]]]) = List of Entangled Photons born out of the SPDC Process
        """

        ephotons_net = []
        
        laser_photons_net = list(deepflatten(Laser.emit(self,qs_list,basis,PER)))
        
        max_no_of_photon_pairs_gen = int(round(self.efficiency*len(laser_photons_net)))
        flag = 1

        for i,ph in enumerate(laser_photons_net):
            rnum = np.abs(self.gen.normal(loc = self.efficiency,scale = 5*self.efficiency))
            no_of_photon_pairs_gen = int(0.5*len(list(deepflatten(ephotons_net))))
            if no_of_photon_pairs_gen <= max_no_of_photon_pairs_gen:
                if rnum < self.efficiency:
                    epp = []
                    ep1 = Photon(str(ph.uID) + '_E0',ph.wl*2,0,ph.enc_type,ph.qs.coeffs,ph.qs.basis)
                    ep1.set_source_linewidth(self.lwidth)
                    ep2 = Photon(str(ph.uID) + '_E1',ph.wl*2,0,ph.enc_type,ph.qs.coeffs,ph.qs.basis)
                    ep2.set_source_linewidth(self.lwidth)
                    self.SPDC_entangled_states(ep1,ep2)
                    if self.gen.random() < self.noise_level:
                        ep1.qs.dampen_phase_and_amplitude(self.gamma,self.lmda)
                        ep2.qs.dampen_phase_and_amplitude(self.gamma,self.lmda)
                    epp = [ep1,ep2]
                    ephotons_net.append(epp)
                no_of_photon_pairs_gen = int(0.5*len(list(deepflatten(ephotons_net))))
                if no_of_photon_pairs_gen > max_no_of_photon_pairs_gen:
                    flag = 0
                    break
            else:
                break   
        if flag == 0:
            ephotons_net.remove(epp)
        
        for epp in ephotons_net:
            for ep,receiver,envt in zip(epp,self.receivers,self.envt_list):
                envt.timeout(self.env.now)
                envt.run()
                ep.set_environment(envt)
                receiver.receive([ep])
        
        E = simpy.Environment()
        self.env = E
