# -*- coding: utf-8 -*-

import numpy as np
from ..components.component import Component
from ..components.quantum_channel import QuantumChannel
from ..components.detector import Detector

class Node(Component):
    
    """
    Models a Node in a Quantum Network
    
    Attributes:
        uID (str) = Unique ID
        env (simpy.Environment) = Simpy Environment for Simulation
        gen (numpy.random.Generator) = Random Number Generator
        all_components(Dict[str:str]) = Dictionary of all the Components belonging to the Node, such that, for any Dictionary Item, Key = component.uID and Value = component
    """

    def __init__(self,uID,env):
        
        """
        Constructor for the Node class
        
        Arguments:
            uID (str) = Unique ID
            env (simpy.Environment) = Simpy Environment for Simulation
        """
        
        Component.__init__(self,uID,env)
        self.all_components = {}
        
    def add_components(self,comp_net):
        
        """
        Instance method to allocate component(s) to the node
        
        Arguments:
            comp_net (List[Laser and/or Weaklaser and/or EntangledPhotonsSourceSPDC and/or ClassicalChannel and/or QuantumChannel and/or NonPolarizingBeamSplitter and/or PolarizingBeamSplitter and/or WavePlate and/or Mirror and/or Detector]) = Quantum Hardware Components
        """
        
        for comp in comp_net:
            self.all_components[comp.uID] = comp
            
    def set_coupling_efficiencies(self,coupling_eff_dict):
        
        """
        Instance method to set the coupling efficiencies of the quantum channels and detectors
        
        Arguments:
            coupling_eff_dict (Dict{'QuantumChannel uID':coupling_eff and/or 'Detector uID':coupling_eff}) = Dictionary of Components mapped to their corresponding Coupling Efficiencies (with the Source)
        """
        
        for c_uid,coupling_eff in coupling_eff_dict.items():
            self.all_components[c_uid].set_coupling_efficiency(coupling_eff)
            
    def set_input_port_connections_for_beam_splitters(self,input_port_connection_dict):
        
        """
        Instance method to set the input port configurations of the beam splitters with their respective sources
        
        Arguments:
            input_port_connection_dict (Dict{'NonPolarizingBeamSplitter uID' or 'PolarizingBeamSplitter uID':input_port}) = Dictionary of Beam Splitters mapped to their corresponding Input Port Configurations
        """
        
        for bs_uid,i_port in input_port_connection_dict.items():
            self.all_components[bs_uid].set_input_port_connection(i_port)
            
    def set_measured_qstate_coeffs_for_detectors(self,m_qs_coeffs_dict):
        
        """
        Instance method to set the measured quantum state coefficients of the photons being detected by the detectors
        
        Arguments:
            m_qs_coeffs_dict (Dict{'Detector uID':m_qs_state_coeffs}) = Dictionary of Detectors mapped to their corresponding Measured Quantum State Coefficients
        """
        
        for det_uid,m_qs_coeffs in m_qs_coeffs_dict.items():
            self.all_components[det_uid].set_measured_qstate_coeffs(m_qs_coeffs)
            
    def connect_classical_channels(self,cch_connections):
        
        """
        Instance method to connect classical channels to their receiver nodes
        
        Arguments:
            cch_connections(Dict{'ClassicalChannel uID': Receiver Node}) = Dictionary of Classical Channels mapped to their corresponding Receiver Nodes
        """
        
        for cch_uid,rec_node in cch_connections.items():
            self.all_components[cch_uid].connect(self,rec_node)
        
    def connect_one_way_components(self,oway_connections):
        
        """
        Instance method to connect one way components, i.e., sources and detectors to their receivers and senders (respectively)
        
        Arguments:
            oway_connections(Dict{'Component uID':'QuantumChannel uID' and/or 'Component uID':['QuantumChannel 1 uID', 'QuantumChannel 2 uID']}) = Dictionary mapping One Way Components to their corresponding Receiver(s) or Sender
        """
        
        for comp_uid,connect_det in oway_connections.items():
            if type(connect_det) == str:
                self.all_components[comp_uid].connect(self.all_components[connect_det])
            elif type(connect_det) == list:
                self.all_components[comp_uid].connect([self.all_components[connect_det[0]],self.all_components[connect_det[1]]])
            
    def connect_two_way_internode_components(self,tway_inter_node_connections):
       
        """
        Instance method to connect two way internode components to their senders and receivers
       
        Arguments:
            tway_inter_node_connections(Dict{'Component uID':[Same Node Source uID (str), [Other Node (object of type Node), Other Node Receiver uID (str)]] and/or 'QuantumChannel uID':[[Other Node (object of type Node), Other Node Source uID (str)], Same Node Receiver uID (str)]}) = Dictionary mapping Two Way Internode Components to their Senders and Receivers
        """
       
        for comp_uid,s_d_uids in tway_inter_node_connections.items():
            if len(s_d_uids[1]) == 2:
                self.all_components[comp_uid].connect(s_d_uids[0][0].all_components[s_d_uids[0][1]],s_d_uids[1][0].all_components[s_d_uids[1][1]])
            elif len(s_d_uids[1]) == 4:
                if len(s_d_uids[0]) == 2:
                    self.all_components[comp_uid].connect([s_d_uids[0][0].all_components[s_d_uids[0][1]]],[s_d_uids[1][0].all_components[s_d_uids[1][1]],s_d_uids[1][2].all_components[s_d_uids[1][3]]])
                elif len(s_d_uids[0]) == 4:
                    self.all_components[comp_uid].connect([s_d_uids[0][0].all_components[s_d_uids[0][1]],s_d_uids[0][2].all_components[s_d_uids[0][3]]],[s_d_uids[1][0].all_components[s_d_uids[1][1]],s_d_uids[1][2].all_components[s_d_uids[1][3]]])
                
    def connect_two_way_intranode_components(self,tway_intra_node_connections):
        
        """
        Instance method to connect the two way (completely) intranode components to their senders and receivers
       
        Arguments:
            tway_intra_node_connections(Dict{'Component uID':[Same Node Source uID (str), [Other Node (object of type Node), Other Node Receiver uID (str)]] and/or 'QuantumChannel uID':[[Other Node (object of type Node), Other Node Source uID (str)], Same Node Receiver uID (str)]}) = Dictionary mapping Two Way Intranode Components to their Senders and Receivers
        """
       
        for comp_uid,s_d_uids in tway_intra_node_connections.items():
            if type(s_d_uids[1]) == str: # QC,WP
                self.all_components[comp_uid].connect(self.all_components[s_d_uids[0]],self.all_components[s_d_uids[1]])
            elif type(s_d_uids[1]) == list and type(s_d_uids[0]) != list: # PBS
                self.all_components[comp_uid].connect(self.all_components[s_d_uids[0]],[self.all_components[s_d_uids[1][0]],self.all_components[s_d_uids[1][1]]])
            elif type(s_d_uids[0]) == list and type(s_d_uids[1]) == list: # For NPBS
                if len(s_d_uids[0]) == 1:
                    self.all_components[comp_uid].connect([self.all_components[s_d_uids[0][0]]],[self.all_components[s_d_uids[1][0]],self.all_components[s_d_uids[1][1]]])
                elif len(s_d_uids[0]) == 2:
                    self.all_components[comp_uid].connect([self.all_components[s_d_uids[0][0]],self.all_components[s_d_uids[0][1]]],[self.all_components[s_d_uids[1][0]],self.all_components[s_d_uids[1][1]]])
             
    def send_classical_information(self,cch_uid,info,rec_node):
        
        """
        Instance method to send classical information to the receiver node
        
        Arguments:
            cch_uid (str) = Unique ID of the Classical Channel via which the Information is to be transmitted
            info (str) = Information to be transmitted via the Classical Channel
            rec_node (Node) = Receiver Node 
        """
        
        self.all_components[cch_uid].set_sender_and_receiver(self,rec_node)
        assert self.all_components[cch_uid].sender == self,"Can't send information since you are NOT connected to the channel as a sender node"
        self.all_components[cch_uid].transmit(info)
    
    def receive_classical_information(self,cch_uid,info):
        
        """
        Instance method to receive classical information from the sender node
        
        Arguments:
            cch_uid (str) = Unique ID of the Classical Channel via which the Information has been transmitted
            info (str) = Information transmitted via the Classical Channel
        """
        
        assert self.all_components[cch_uid].receiver == self,"Can't receive information since you are NOT connected to the channel as a receiver node"
        self.classical_info = info
        
    def set_key(self,key):
        
        """
        Instance method to set the key [Used in QKD]
        
        Arguments:
            key (str): String of 0s and 1s
        """
        
        self.key = key
        self.key_int = int(key,2)
        self.key_len = len(key)
        
    def calc_net_transmission_time(self,component_list,lwidth,threshold = 3):
        
        """
        Instance method to compute the minimum and maximum transmission times for a photon in the Node's part of the quantum network
        
        Argument:
            component_list (list[Laser and/or Weaklaser and/or EntangledPhotonsSourceSPDC and/or QuantumChannel]) = Components
            lwidth (float) = Linewidth of the Source
            threshold (int) = Threshold for restricting Outliers (Default: +/- 3 Standard Deviations from the Mean)
        """
        
        self.min_net_transmission_time = 0
        self.max_net_transmission_time = 0
        
        for comp_uID in component_list:
            if isinstance(self.all_components[comp_uID],QuantumChannel): 
                self.all_components[comp_uID].calc_p_twidth(lwidth)
            self.min_net_transmission_time += self.all_components[comp_uID].mean_transmission_time - threshold*self.all_components[comp_uID].p_twidth
            self.max_net_transmission_time += self.all_components[comp_uID].mean_transmission_time + threshold*self.all_components[comp_uID].p_twidth        
    
    def identify_detectors(self):
        
        """
        Instance method to identify the detectors associated with a Node
        """
        
        self.detectors = {}
        
        for comp_uID,comp in self.all_components.items():
            if isinstance(comp,Detector):
                self.detectors[comp_uID] = comp
            
    def detection_analysis(self,min_tr_time,max_tr_time,start_time,setup_end_time):
        
        """
        Instance method to perform single photon detection analysis
        
        Arguments:
            min_tr_time (float) = Minimum Transmission Time for a Photon corresponding to the entire Quantum Network
            max_tr_time (float) = Maximum Transmission Time for a Photon corresponding to the entire Quantum Network
            start_time (float) = Time at which the Run commences
            setup_end_time (float) = Time at which the Run ends
        """
        
        max_tr_time += 1e-9
                
        for det_uID,det in self.detectors.items():
            if len(det.num_net) != 0:
                basis_num = det.num_net[0]
                qs_measured = det.measured_qs_coeffs_net[0]
                break
        
        for det in self.detectors.values():
            det.clear_measurements()
            while start_time + max_tr_time > det.next_dark_count_time:
                det.register_dark_counts()
                
        potential_false_triggers = {}
                
        for det_uID,det in self.detectors.items():
            for i in range(det.dark_count_check_idx,len(det.dark_count_time_instants)):
                if det.dark_count_time_instants[i] >= start_time + min_tr_time and det.dark_count_time_instants[i] <= start_time + max_tr_time:
                    potential_false_triggers[det_uID] = det.dark_count_time_instants[i]
            det.dark_count_check_idx = len(det.dark_count_time_instants) - 1      
       
        potential_false_triggers = dict(sorted(potential_false_triggers.items(),key = lambda i:i[1]))
        
        if len(potential_false_triggers) != 0:
            earliest_potential_false_trigger = list(min(potential_false_triggers.items(),key = lambda i:i[1]))
            # In case no detector actually received (and hence) detected a photon, the detector that triggered the earliest acceptable dark count decides the final measurement result
            if basis_num == -1:
                basis_num = self.detectors[earliest_potential_false_trigger[0]].num
                qs_measured = self.detectors[earliest_potential_false_trigger[0]].measured_qs_coeffs
            
            else:
                if earliest_potential_false_trigger[1] < setup_end_time:
                    basis_num = self.detectors[earliest_potential_false_trigger[0]].num
                    qs_measured = self.detectors[earliest_potential_false_trigger[0]].measured_qs_coeffs
        
        return basis_num,qs_measured
    
    def calc_total_photon_counts(self):
        
        """
        Instance method to compute the total number of photons successfully detected by each of the detectors associated with the Node
        """
        
        for det in self.detectors.values():
            det.photon_count += len(det.dark_count_time_instants)
            
    def bell_state_detection_analysis(self,min_tr_time,max_tr_time,start_time):
        
        """
        Instance method to perform Bell-state detection analysis
        
        Arguments:
            min_tr_time (float) = Minimum Transmission Time for a Photon corresponding to the entire Quantum Network
            max_tr_time (float) = Maximum Transmission Time for a Photon corresponding to the entire Quantum Network
            start_time (float) = Time at which the Run commences
        """
        
        max_tr_time += 1e-9
        
        num_net = []
        end_pt_net = []
        det_to_not_check = []
        det_time_net = []
        flag = 0
        
        for det_uID,det in self.detectors.items():
            if len(det.num_net) != 0:
                chk_det = det
                end_pt_net.append(det.uID)
                num_net.append(det.num_net[0])
                det_time_net.append(det.detection_time_net[0])
                det.num_net.remove(det.num_net[0])
                det.detection_time_net.remove(det.detection_time_net[0])
                for sub_det in self.detectors.values():
                    if sub_det not in det_to_not_check:
                        if len(sub_det.num_net) != 0:
                            end_pt_net.append(sub_det.uID)
                            num_net.append(sub_det.num_net[0])
                            det_time_net.append(sub_det.detection_time_net[0])
                            flag = 1
                            break
                if flag:
                    break
                else:
                    det_to_not_check.append(chk_det)
                    
        for det in self.detectors.values():
            det.clear_measurements()
            while start_time + max_tr_time > det.next_dark_count_time:
                det.register_dark_counts()
                
        potential_false_triggers = {}
                
        for det_uID,det in self.detectors.items():
            for i in range(det.dark_count_check_idx,len(det.dark_count_time_instants)):
                if det.dark_count_time_instants[i] >= start_time + min_tr_time and det.dark_count_time_instants[i] <= start_time + max_tr_time:
                    potential_false_triggers[det_uID] = det.dark_count_time_instants[i]
            det.dark_count_check_idx = len(det.dark_count_time_instants) - 1  
            
        potential_false_triggers = sorted(potential_false_triggers.items(),key = lambda i:i[1])
        
        if len(potential_false_triggers) != 0:
            
            if len(potential_false_triggers) > 2:
                potential_false_triggers = potential_false_triggers[:2]
        
            if len(potential_false_triggers) == 1:
                # The case when none of the detectors are 'truely' triggered and when there is only 1 potential false trigger is not of any value. Only 2 simultaneous detections can be indicative of a Bell state measurement
                if num_net[0] != -1 and num_net[1] == -1:
                    num_net[1] = self.detectors[potential_false_triggers[0][0]].num
                    end_pt_net[1] = potential_false_triggers[0][0]
                elif num_net[0] == -1 and num_net[1] != -1:
                    num_net[0] = self.detectors[potential_false_triggers[0][0]].num
                    end_pt_net[0] = potential_false_triggers[0][0]
            elif len(potential_false_triggers) == 2:
                if np.allclose(num_net,[-1,-1]):
                    for i in range(2):
                        num_net[i] = self.detectors[potential_false_triggers[i][0]].num
                        end_pt_net[i] = potential_false_triggers[i][0]
                else:
                    if (num_net[0] != -1 and num_net[1] == -1):
                        potential_false_triggers.append((end_pt_net[0],det_time_net[0]))
                    elif (num_net[0] == -1 and num_net[1] != -1):
                        potential_false_triggers.append((end_pt_net[1],det_time_net[1]))
                    else:
                        for i in range(2):
                            potential_false_triggers.append((end_pt_net[i],det_time_net[i]))
                    
                    selected_triggers = sorted(potential_false_triggers,key = lambda i:i[1])[:2]
                    end_pt_net = [selected_triggers[0][0],selected_triggers[1][0]]
                    num_net = [self.detectors[end_pt_net[0]].num,self.detectors[end_pt_net[1]].num]
                    
        return end_pt_net,num_net