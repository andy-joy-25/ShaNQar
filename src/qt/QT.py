# -*- coding: utf-8 -*-

import numpy as np
import simpy

from ..components.node import Node
from ..components.SPDC import EntangledPhotonsSourceSPDC
from ..components.quantum_channel import QuantumChannel
from ..components.classical_channel import ClassicalChannel
from ..components.non_polarizing_beam_splitter import NonPolarizingBeamSplitter
from ..components.polarizing_beam_splitter import PolarizingBeamSplitter
from ..utils.photon_enc import encoding
from ..components.detector import Detector
from ..components.weaklaser import Weaklaser

phi_plus = np.array([[complex(1/np.sqrt(2))],[complex(0)],[complex(0)],[complex(1/np.sqrt(2))]])
phi_minus = np.array([[complex(1/np.sqrt(2))],[complex(0)],[complex(0)],[complex(-1/np.sqrt(2))]])
psi_plus = np.array([[complex(0)],[complex(1/np.sqrt(2))],[complex(1/np.sqrt(2))],[complex(0)]])
psi_minus = np.array([[complex(0)],[complex(1/np.sqrt(2))],[complex(-1/np.sqrt(2))],[complex(0)]])

X = np.array([[complex(0),complex(1)],[complex(1),complex(0)]])
Z = np.array([[complex(1),complex(0)],[complex(0),complex(-1)]])

env = simpy.Environment()
env1 = simpy.Environment()
env2 = simpy.Environment()
env3 = simpy.Environment()
        
Alice = Node('A',env)
Bob = Node('B',env)
    
# Channels linking Alice to Bob
QC_EPS2 = QuantumChannel('QC_EPS2',env,1000,0.2e-3,1.47,0.90,17e-6,0.3,set_adaptive_env = True) 
CC = ClassicalChannel('CC',env,1000,1.47)

# Alice's Hardware Stack
QC_EPS1 = QuantumChannel('QC_EPS1',env,100,0.2e-3,1.47,0.90,17e-6,0.3,set_adaptive_env = True)
QC_WL = QuantumChannel('QC_WL',env3,100,0.2e-3,1.47,0.90,17e-6,0.3)

WeakLaser = Weaklaser('WL',env3,76e6,1550e-9,0.01e-9,200e-15,1e5,'Polarization',0.01,0.3,0.45,0,4,5)
print(f'The mean number of photons emitted by the weaklaser are: {WeakLaser.mu_photons_after_attenuation}')

EPS = EntangledPhotonsSourceSPDC('EPS',env,76e6,775e-9,0.01e-9,200e-15,1e6,'Polarization',0.01,0.3,0.45,2,[env1,env2],1e-6)
EPS_coeffs_type = EPS.bell_like_state

NPBS = NonPolarizingBeamSplitter('NPBS',env,0.50)

QC_PBS1 = QuantumChannel('QC_PBS1',env,0.5,0.2e-3,1.47,0.90,17e-6,0.3,set_adaptive_env = True)
QC_PBS2 = QuantumChannel('QC_PBS2',env,0.5,0.2e-3,1.47,0.90,17e-6,0.3,set_adaptive_env = True)

PBS1 = PolarizingBeamSplitter('PBS1',env,1000)
PBS2 = PolarizingBeamSplitter('PBS2',env,1000)

QC_Det1 = QuantumChannel('QC_D1',env,0.15,0.2e-3,1.47,0.90,17e-6,0.3,set_adaptive_env = True)
Det1 = Detector('D1',env,1e-8,0.90,1000,55e-12,1,set_adaptive_env = True)
QC_Det2 = QuantumChannel('QC_D2',env,0.15,0.2e-3,1.47,0.90,17e-6,0.3,set_adaptive_env = True)
Det2 = Detector('D2',env,1e-8,0.90,1000,55e-12,0,set_adaptive_env = True)
QC_Det3 = QuantumChannel('QC_D3',env,0.15,0.2e-3,1.47,0.90,17e-6,0.3,set_adaptive_env = True)
Det3 = Detector('D3',env,1e-8,0.90,1000,55e-12,0,set_adaptive_env = True)
QC_Det4 = QuantumChannel('QC_D4',env,0.15,0.2e-3,1.47,0.90,17e-6,0.3,set_adaptive_env = True)
Det4 = Detector('D4',env,1e-8,0.90,1000,55e-12,1,set_adaptive_env = True)

# Bob's Hardware Stack
PBS_T = PolarizingBeamSplitter('PBST',env,1000)
QC_Det_T1 = QuantumChannel('QC_DT1',env,0.15,0.2e-3,1.47,0.90,17e-6,0.3,set_adaptive_env = True)
Det_T1 = Detector('DT1',env,1e-8,0.90,1000,55e-12,1,set_adaptive_env = True)
QC_Det_T2 = QuantumChannel('QC_DT2',env,0.15,0.2e-3,1.47,0.90,17e-6,0.3,set_adaptive_env = True)
Det_T2 = Detector('DT2',env,1e-8,0.90,1000,55e-12,0,set_adaptive_env = True)

Alice.add_components([WeakLaser,EPS,QC_WL,QC_EPS1,QC_EPS2,CC,NPBS,QC_PBS1,QC_PBS2,PBS1,PBS2,QC_Det1,Det1,QC_Det2,Det2,QC_Det3,Det3,QC_Det4,Det4])
Bob.add_components([QC_EPS2,CC,PBS_T,QC_Det_T1,Det_T1,QC_Det_T2,Det_T2])

Alice.set_coupling_efficiencies({'QC_WL':0.95,'QC_EPS1':0.95,'QC_EPS2':0.95,'QC_PBS1':0.95,'QC_PBS2':0.95,'QC_D1':0.95,'QC_D2':0.95,'QC_D3':0.95,'QC_D4':0.95,'D1':0.95,'D2':0.95,'D3':0.95,'D4':0.95})
Bob.set_coupling_efficiencies({'QC_DT1':0.95,'QC_DT2':0.95,'DT1':0.95,'DT2':0.95})

Alice.set_input_port_connections_for_beam_splitters({'NPBS':[1,2],'PBS1':1,'PBS2':1})
Bob.set_input_port_connections_for_beam_splitters({'PBST':1})

m_qs_coeffs_1 = np.array([[complex(1)],[complex(0)]])
m_qs_coeffs_2 = np.array([[complex(0)],[complex(1)]])
Alice.set_measured_qstate_coeffs_for_detectors({'D1':m_qs_coeffs_2,'D2':m_qs_coeffs_1,'D3':m_qs_coeffs_1,'D4':m_qs_coeffs_2})
Bob.set_measured_qstate_coeffs_for_detectors({'DT1':m_qs_coeffs_2,'DT2':m_qs_coeffs_1})

Bob.connect_classical_channels({'CC':Alice})

Alice.connect_one_way_components({'WL':'QC_WL','EPS':['QC_EPS1','QC_EPS2'],'D1':'QC_D1','D2':'QC_D2','D3':'QC_D3','D4':'QC_D4'})
Bob.connect_one_way_components({'DT1':'QC_DT1','DT2':'QC_DT2'})

Alice.connect_two_way_internode_components({'QC_EPS2':[[Alice,'EPS'],[Bob,'PBST']]})

Alice.connect_two_way_intranode_components({'QC_EPS1':['EPS','NPBS'],'QC_WL':['WL','NPBS'],'NPBS':[['QC_WL','QC_EPS1'],['QC_PBS1','QC_PBS2']],'QC_PBS1':['NPBS','PBS1'],'QC_PBS2':['NPBS','PBS2'],'PBS1':['QC_PBS1',['QC_D1','QC_D2']],'PBS2':['QC_PBS2',['QC_D4','QC_D3']],'QC_D1':['PBS1','D1'],'QC_D2':['PBS1','D2'],'QC_D3':['PBS2','D3'],'QC_D4':['PBS2','D4']})
Bob.connect_two_way_intranode_components({'PBST':['QC_EPS2',['QC_DT1','QC_DT2']],'QC_DT1':['PBST','DT1'],'QC_DT2':['PBST','DT2']})

Alice.identify_detectors()
Bob.identify_detectors()

Alice.calc_net_transmission_time(['WL','QC_WL','QC_PBS1','QC_D1'],Alice.all_components['WL'].lwidth,5)
total_net_min_transmission_time_BSM = Alice.min_net_transmission_time
total_net_max_transmission_time_BSM = Alice.max_net_transmission_time
print(f'The MINIMUM total transmission time through the BSM setup is {total_net_min_transmission_time_BSM} s')
print(f'The MAXIMUM total transmission time through the BSM setup is {total_net_max_transmission_time_BSM} s')
tol_time = 1e-13
total_net_max_transmission_time_BSM += tol_time

Alice.calc_net_transmission_time(['EPS'],Alice.all_components['EPS'].lwidth,5)
Bob.calc_net_transmission_time(['QC_EPS2','QC_DT1'],Alice.all_components['EPS'].lwidth,5)
total_net_min_transmission_time_Bob_side = Alice.min_net_transmission_time + Bob.min_net_transmission_time
total_net_max_transmission_time_Bob_side = Alice.max_net_transmission_time + Bob.max_net_transmission_time
print(f"The MINIMUM total transmission time through the QT network at Bob's end is {total_net_min_transmission_time_Bob_side} s")
print(f"The MAXIMUM total transmission time through the QT network at Bob's end is {total_net_max_transmission_time_Bob_side} s")
tol_time = 1e-13
total_net_max_transmission_time_Bob_side += tol_time

#TODO: Set target quantum state coefficients
WL_coeffs = [[complex(0)],[complex(1)]]
WL_coeffs = np.reshape(np.array(WL_coeffs),(len(WL_coeffs),1))
print(f'The coefficients of the target quantum state (to be teleported) are {WL_coeffs}')

coeffs_list = [[complex(1),complex(0)],[complex(0),complex(1)]]
coeffs_list[0] = np.reshape(np.array(coeffs_list[0]),(len(coeffs_list[0]),1))
coeffs_list[1] = np.reshape(np.array(coeffs_list[1]),(len(coeffs_list[1]),1))

ket0_count = 0
ket1_count = 0
classical_info_sent = 0

# START TELEPORATION
for i in range(2500):
    
    start_time = env3.now
    
    Alice.all_components['WL'].emit_and_attenuate([WL_coeffs],encoding['Polarization'][0],1e6)
    Alice.all_components['EPS'].emit_pp([[complex(1),complex(0)]],encoding['Polarization'][0],1e6)
    
    setup_end_time_Bob_side = env2.now
    
    num_net = []
    end_pt_net = []

    end_pt_net,num_net = Alice.bell_state_detection_analysis(total_net_min_transmission_time_BSM,total_net_max_transmission_time_BSM,start_time)

    if env1.now > env3.now:
        Alice.all_components['CC'].set_environment(env1)
    else:
        Alice.all_components['CC'].set_environment(env3)
    
    if num_net[0] != -1 and num_net[1] != -1:
        
        if (end_pt_net == ['D1','D2']) or (end_pt_net == ['D2','D1']) or (end_pt_net == ['D3','D4']) or (end_pt_net == ['D4','D3']):
            Alice.send_classical_information('CC','0',Bob)
            assert Bob.classical_info == '0' 
            classical_info_sent = 1
        elif (end_pt_net == ['D1','D3']) or (end_pt_net == ['D3','D1']) or (end_pt_net == ['D2','D4']) or (end_pt_net == ['D4','D2']):
            Alice.send_classical_information('CC','1',Bob)
            assert Bob.classical_info == '1'
            classical_info_sent = 1
         
    basis_num,qs_measured = Bob.detection_analysis(total_net_min_transmission_time_Bob_side,total_net_max_transmission_time_Bob_side,start_time,setup_end_time_Bob_side)
    
    if (type(qs_measured) != int) and (classical_info_sent == 1):
        
        if Bob.classical_info == '0':
            
            if EPS_coeffs_type == 'phi+':
                qs_measured = np.matmul(X,qs_measured)
            elif EPS_coeffs_type == 'phi-':
                qs_measured = np.matmul(X,np.matmul(Z,qs_measured))
            elif EPS_coeffs_type == 'psi-':
                qs_measured = np.matmul(X,np.matmul(Z,np.matmul(X,qs_measured)))
            
            if np.allclose(np.abs(qs_measured),np.abs(coeffs_list[0])) and qs_measured.shape == coeffs_list[0].shape:
                ket0_count += 1
            elif np.allclose(np.abs(qs_measured),np.abs(coeffs_list[1])) and qs_measured.shape == coeffs_list[1].shape:
                ket1_count += 1
                
        elif Bob.classical_info == '1':
            
            if EPS_coeffs_type == 'phi+':
                qs_measured = np.matmul(Z,np.matmul(X,qs_measured))
            elif EPS_coeffs_type == 'phi-':
                qs_measured = np.matmul(Z,np.matmul(X,np.matmul(Z,qs_measured)))
            elif EPS_coeffs_type == 'psi+':
                qs_measured = np.matmul(Z,qs_measured)
            elif EPS_coeffs_type == 'psi-':
                qs_measured = np.matmul(Z,np.matmul(X,np.matmul(Z,np.matmul(X,qs_measured))))
            
            if np.allclose(np.abs(qs_measured),np.abs(coeffs_list[0])) and qs_measured.shape == coeffs_list[0].shape:
                ket0_count += 1
            elif np.allclose(np.abs(qs_measured),np.abs(coeffs_list[1])) and qs_measured.shape == coeffs_list[1].shape:
                ket1_count += 1
        
        
    if (env2.now > env1.now) and (env2.now > env3.now):
        env1.timeout(env2.now - env1.now)
        env1.run()
        env3.timeout(env2.now - env3.now)
        env3.run()
    elif (env1.now > env2.now) and (env1.now > env3.now):
        env2.timeout(env1.now - env2.now)
        env2.run()
        env3.timeout(env1.now - env3.now)
        env3.run()
    elif (env3.now > env1.now) and (env3.now > env2.now):
        env1.timeout(env3.now - env1.now)
        env1.run()
        env2.timeout(env3.now - env2.now)
        env2.run()
    
    classical_info_sent = 0

Alice.calc_total_photon_counts()
Bob.calc_total_photon_counts()

print('Measured Quantum State Counts')
print(f'ket0_count = {ket0_count}')
print(f'ket1_count = {ket1_count}')