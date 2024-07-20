# -*- coding: utf-8 -*-

import math
import numpy as np
import simpy
import itertools as it
from iteration_utilities import deepflatten
from ..utils.photon_enc import encoding
from ..components.laser import Laser
from ..components.variable_ND_filter import NDFilter

class Weaklaser(Laser,NDFilter):
    
    """
    Models a Weak Laser [Laser + ND Filter(s)]
    
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
        min_OD (float) = Minimum Value of the Optical Density (OD) that the ND Filter can be set to
        max_OD (float) = Maximum Value of the Optical Density (OD) that the ND Filter can be set to
        max_num_of_ND_filters (int) = Maximum Number of ND Filters which can be used for attentuation of the Laser's Output
        ND_filter_stack (list[float]) = OD(s) of the ND Filter(s) to be used for attentuating the Laser's Output to Single Photon Levels
    """

    def __init__(self,uID,env,PRR,wl,lwidth,twidth,mu_photons,enc_type,noise_level,gamma,lmda,min_OD,max_OD,max_num_of_ND_filters,calc_mu_photons_after_attenuation = True):
        
        """
        Constructor for the Weaklaser class
        
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
            min_OD (float) = Minimum Value of the Optical Density (OD) that the ND Filter can be set to
            max_OD (float) = Maximum Value of the Optical Density (OD) that the ND Filter can be set to
            max_num_of_ND_filters (int) = Maximum Number of ND Filters which can be used for attentuation of the Laser's Output
            calc_mu_photons_after_attenuation (bool) = Boolean to determine whether to compute the Mean Number of Photons emitted by the Weak Laser or Not
        """
        
        Laser.__init__(self,uID,env,PRR,wl,lwidth,twidth,mu_photons,enc_type,noise_level,gamma,lmda)
        NDFilter.__init__(self,uID,env,min_OD,max_OD)
        self.uID = uID
        self.max_num_of_ND_filters = max_num_of_ND_filters
        self.ND_Filter_Stack = []
        self.set_ND_Filter_stack()
        self.mean_transmission_time = 1/PRR
        self.p_twidth = twidth
        act_env = self.env
        if calc_mu_photons_after_attenuation:
            temp_env = simpy.Environment()
            self.set_environment(temp_env)
            self.find_mu_photons_after_attenuation()
        self.set_environment(act_env)

    def connect(self,receiver):
        
        """
        Instance method to connect a weak laser with its receiver 
        
        Arguments:
            receiver (QuantumChannel) = Receiver attached to the Weak Laser to receive and transmit a Photon
        """
        
        self.receiver = receiver
        
    def set_environment(self,env):
        
        """
        Instance method to set the environment of a weak laser
        
        Arguments:
            env (Simpy.Environment) = Simpy Environment for Timing Control and Synchronisation 
        """
        
        self.env = env
        
    def set_ND_Filter_stack(self):
        
        """
        Instance method which determines the number of ND Filters and their corresponding ODs required for attentuating the output of the laser
        
        Details:
            The OD to which the ND Filter is to be set (so as to attentuate the laser's output to single photon levels) is decided on the basis of the mean number of photons emitted by the laser
            If this required OD value > maximum OD of a single ND Filter, then a stack of ND Filters are used to achieve the required OD value upto a pre-specified level of tolerance 
            The stack of ND Filters (if required) is preferably chosen in such a manner that the OD of each ND Filter is the same and the sum of the ODs equals the required OD upto a pre-specified level of tolerance 
        """
        
        self.ND_Filter_Stack = []

        avg_transmittance_reqd = 1/self.mu_photons
        avg_OD_reqd = np.round(np.log10(1/avg_transmittance_reqd),decimals = 1)

        if (avg_OD_reqd >= self.min_OD) and (avg_OD_reqd <= self.max_OD):
            self.ND_Filter_Stack.append(avg_OD_reqd)
        
        elif avg_OD_reqd > self.max_OD:

            OD_base = 0
            OD_multiplier = 0
            tol = 0.1

            search_flag = 0
            searched_OD_stack = {}

            for i in np.round(np.arange(self.min_OD,self.max_OD + 0.1,0.1),1):
                for j in range(2,self.max_num_of_ND_filters + 1,1):
                    if round(abs((i*j) - avg_OD_reqd),1) < tol:
                        searched_OD_stack[i] = j
                        search_flag = 1
            
            
            if search_flag == 1:
                OD_base = min(searched_OD_stack,key = searched_OD_stack.get)
                OD_multiplier = searched_OD_stack[OD_base]
                for l in range(1,OD_multiplier+1,1):
                    self.ND_Filter_Stack.append(OD_base)

        
            if search_flag != 1:

                num_of_ND_filters = math.ceil(avg_OD_reqd/self.max_OD)
                
                if num_of_ND_filters <= self.max_num_of_ND_filters:
                    
                    net_OD_combinations_list = list(it.combinations_with_replacement(np.round(np.arange(self.min_OD,self.max_OD + 0.1,0.1),1),num_of_ND_filters))
                    
                    summed_net_ODs = np.round(list(map(sum,net_OD_combinations_list)),1)

                    tol_flag = 0

                    for sumv in summed_net_ODs:
                        if round(abs(round(sumv,1) - avg_OD_reqd),1) < 0.1:
                            tol_flag = 1
                            idx_reqd = np.min(np.where(summed_net_ODs == sumv))
                            self.ND_Filter_Stack = list(net_OD_combinations_list[idx_reqd])
                            break
                    if tol_flag == 0:
                        for sumv in summed_net_ODs:
                            if round(abs(round(sumv,1) - avg_OD_reqd),1) < 0.2:
                                tol_flag = 2
                                idx_reqd = np.min(np.where(summed_net_ODs == sumv))
                                self.ND_Filter_Stack = list(net_OD_combinations_list[idx_reqd])
                                break
                    if tol_flag == 0:
                        for sumv in summed_net_ODs:
                            if round(abs(round(sumv,1) - avg_OD_reqd),1) < 0.3:
                                tol_flag = 3
                                idx_reqd = np.min(np.where(summed_net_ODs == sumv))
                                self.ND_Filter_Stack = list(net_OD_combinations_list[idx_reqd])
                                break

                else:         
                    print(f'ERROR: NOT possible to attenuate to ~ single photon levels...use more than {self.max_num_of_ND_filters} ND Filters!') 


    def emit_and_attenuate(self,qs_list,basis,PER):
        
        """
        Instance method which attentuates the output of the laser to ~ single photon levels using ND Filter(s)
        
        Arguments:
            qs_list (list[list[complex]]) = List of the Sets of Quantum State Coefficients of the Photons emitted by the Laser
            basis (numpy.array(list[list[complex]])) = Basis of the Quantum States of the Photons emitted by the Laser
            PER (float) = Polarization Extinction Ratio, i.e., Transmission Ratio of the Wanted to the Unwanted Component(s) of Polarization
            
        Returned Value:
            NDfilter_photons_net (list[photon]) = List of the Photons emitted by the Weak Laser
        """

        if len(self.ND_Filter_Stack) == 1:
            NDFilter.set_OD(self,self.ND_Filter_Stack[0])
            laser_photons_net = list(deepflatten(Laser.emit(self,qs_list,basis,PER)))
            NDfilter_photons_net = NDFilter.attenuate(self,laser_photons_net)
            
            NDfilter_photons_net = list(deepflatten(NDfilter_photons_net))
            if len(NDfilter_photons_net) != 0:
                for p in NDfilter_photons_net:
                    p.set_environment(self.env)
                    self.receiver.receive([p])
            else:
                self.receiver.receive([None])

                

        else:
            laser_photons_net = list(deepflatten(Laser.emit(self,qs_list,basis,PER)))
            for OD_val in self.ND_Filter_Stack:
                NDFilter.set_OD(self,OD_val)
                NDfilter_photons_net = NDFilter.attenuate(self,laser_photons_net)
                laser_photons_net = NDfilter_photons_net

            NDfilter_photons_net = list(deepflatten(NDfilter_photons_net))
            if len(NDfilter_photons_net) != 0:
                for p in NDfilter_photons_net:
                    p.set_environment(self.env)
                    self.receiver.receive([p])
            else:
                self.receiver.receive([None])
                
    def find_mu_photons_after_attenuation(self):
        
        """
        Instance method to find the mean number of photons emitted by the weak laser, i.e., the mean number of photons emitted by the laser after attenuation via the usage of the ND Filter(s)
        """
        
        class TestReceiver():
            
            def __init__(self):
                pass
            
            def receive(self,p):
                self.photon = p[0]

        R = TestReceiver()
        self.connect(R)
        
        n_photons_total = []
        for i in range(1000):
            self.emit_and_attenuate([[complex(1),complex(0)]],encoding['Polarization'][0],1e6)
            if R.photon is None:
                WL_photon = 0
            else:
                WL_photon = 1
            n_photons_total.append(WL_photon)
       
        self.mu_photons_after_attenuation = sum(n_photons_total)/len(n_photons_total)
        
        self.connect(None)
