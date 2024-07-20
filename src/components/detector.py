# -*- coding: utf-8 -*-

from ..components.component import Component

class Detector(Component):
    
    """
    Models a Single Photon Detector
    
    References: 
        1. R. H. Hadfield, "Single-photon detectors for optical quantum information applications," Nature Photonics, vol. 3, pp. 696–705, 2009
        2. M. Lasota and P. Kolenderski, "Optimal photon pairs for quantum communication protocols," Nature Scientific Reports, vol. 10, no. 20810, 2020
    
    Attributes:
        uID (str) = Unique ID
        env (simpy.Environment) = Simpy Environment for Simulation
        gen (numpy.random.Generator) = Random Number Generator
        dead_time (float) = Dead Time
        det_eff (float) = Intrinsic Detection Efficiency
        coupling_eff (float) = Coupling Efficiency with the Source
        dark_count_rate (float) = Rate of Generation of Dark Counts
        jitter (float) = Standard Deviation in the Time Interval between the Absorption of a Photon and the Generation of an Output Electrical Signal from the Detector
        num (int) = Number to be returned upon the Successful Detection of a Photon
        measured_qs_coeffs (numpy.array) = Measured Quantum State Coefficients of a detected Photon
        set_adaptive_env (bool) = Boolean to control the Adaptive Environment Setting
        next_detection_time (float) = Time at which the Next Detection Event may take place
        next_dark_count_time (float) = Time at which the Next Dark Count is to be registered 
        detect_dark (bool) = True when a Dark Count is to be registered; False otherwise
        photon_count (int) = Number of Photons which have been successfully detected
        sender (Quantum Channel) = Sender of Photons encoded with Quantum Information
        num_net (list[int]) = List of Numbers returned upon the Successful Detection of Photons in a given run
        measured_qs_coeffs_net (List[numpy.array]) = List of Measured Quantum State Coefficients of Photons which have been successfully detected in a given run
        detection_time_net = (list[float]) = List of Time Instants at which Photons have been successfully detected in a given run
        dark_count_time_instants (list[float]) = List of Time Instants at which Dark Counts have been registered in a given run
        dark_count_check_idx (int) = Index from which the Dark Count List 'dark_count_time_instants' is to be checked while performing the detection analysis (see 'node.py')
    """

    def __init__(self,uID,env,dead_time,i_det_eff,dark_count_rate,jitter,num,set_adaptive_env = False): 
        
        """
        Constructor for the Detector class
        
        Arguments:
            uID (str) = Unique ID
            env (simpy.Environment) = Simpy Environment for Simulation
            dead_time (float) = Dead Time
            i_det_eff (float) = Intrinsic Detection Efficiency
            dark_count_rate (float) = Rate of Generation of Dark Counts
            jitter (float) = Standard Deviation in the Time Interval between the Absorption of a Photon and the Generation of an Output Electrical Signal from the Detector
            num (int) = Number to be returned upon the Successful Detection of a Photon
            set_adaptive_env (bool) = Boolean to control the Adaptive Environment Setting
        """
        
        Component.__init__(self,uID,env)
        self.dead_time = dead_time
        self.det_eff = i_det_eff
        self.dark_count_rate = dark_count_rate
        self.jitter = jitter 
        self.next_detection_time = self.env.now
        self.next_dark_count_time = self.env.now
        self.detect_dark = False
        self.photon_count = 0     
        self.num = num 
        self.set_adaptive_env = set_adaptive_env
        self.num_net = []
        self.measured_qs_coeffs_net = []
        self.dark_count_check_idx = 0
        self.dark_count_time_instants = []
        self.detection_time_net = []
        
    def connect(self,sender):
        
        """
        Instance method to connect a detector with the sender of incoming photons
        
        Arguments:
            sender(Quantum Channel) = Sender of Photons encoded with Quantum Information
        """
        
        self.sender = sender
        
    def set_coupling_efficiency(self,coupling_eff):
        
        """
        Instance method to set the coupling efficiency of a detector
        
        Arguments:
            coupling_eff (float) = Coupling Efficiency (with the Source)
        """
        
        self.coupling_eff = coupling_eff
        
    def set_measured_qstate_coeffs(self,m_qs_coeffs):
        
        """
        Instance method to set the quantum state coefficients of a photon as measured by the detector by virtue of the connected experimental setup
        
        Arguments:
            m_qs_coeffs (numpy.array([complex])) = Measured Quantum State Coefficients of the Detected Photon
        """
        
        self.measured_qs_coeffs = m_qs_coeffs
        
    def set_environment(self,env):
        
        """
        Instance method to set the environment of a detector
        
        Arguments:
            env (Simpy.Environment) = Simpy Environment for Timing Control and Synchronisation 
        """
        
        self.env = env
        
    def clear_measurements(self):
        
        """
        Instance method to clear all the measurement records stored by a detector before the next run
        """
        
        self.num_net = []
        self.measured_qs_coeffs_net = []
        self.detection_time_net = []
        
    def schedule_dark_count(self):
        
        """
        Instance method for scheduling a dark count
        
        Details:
            The time interval between dark counts follows an exponential distribution
        """

        dark_count_time_interval = self.gen.exponential(1/self.dark_count_rate)
        self.next_dark_count_time = self.next_dark_count_time + dark_count_time_interval
        
    def register_dark_counts(self):
        
        """
        Instance method for registering dark counts
        """
        
        if self.dark_count_rate > 0:
            
            self.schedule_dark_count()
            self.dark_count_time_instants.append(self.next_dark_count_time)
                    
    def receive(self,p_net): 
        
        """
        Instance method for receiving a photon for detection, measuring its quantum state, and detecting it if the appropriate conditions are satisfied
        
        Arguments:
            p_net (photon) = Incoming Photons 
        """
        
        for p in p_net:
            
            self.flag = False
            
            if p is not None:
                
                if self.set_adaptive_env:
                    self.set_environment(p.env)
                
                # Check if the probability of the photon being coupled into the detector is less than the coupling efficiency and if that is the case, couple it into the detector
                if self.gen.random() < self.coupling_eff:
                    # Check if the photon arrives at the detector at/after the next detection time. If that is the case, the photon may be detected
                    if (self.env.now >= self.next_detection_time): 
                        # Check if the probability of the photon triggering a detection count is less than the detection efficiency of the detector and if that is the case, register a photon count
                        if self.gen.random() < self.det_eff:
                            self.photon_count += 1
                            # Set the next instant of time at which a photon can possibly be detected (Here, the detector's response function has been assumed to be Gaussian)
                            self.next_detection_time = self.env.now + self.jitter*self.gen.standard_normal() + self.dead_time   
                            self.num_net.append(self.num)
                            self.measured_qs_coeffs_net.append(self.measured_qs_coeffs)
                            self.detection_time_net.append(p.env.now)
                            self.flag = True

            
            if not self.flag:
                self.num_net.append(-1)
                self.measured_qs_coeffs_net.append(-1)
                self.detection_time_net.append(-1)
                

        