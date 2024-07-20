# -*- coding: utf-8 -*-

import numpy as np
import simpy

from ..components.node import Node
from ..components.weaklaser import Weaklaser
from ..components.quantum_channel import QuantumChannel
from ..components.classical_channel import ClassicalChannel
from ..components.non_polarizing_beam_splitter import NonPolarizingBeamSplitter
from ..components.polarizing_beam_splitter import PolarizingBeamSplitter
from ..components.waveplate import WavePlate
from ..utils.photon_enc import encoding
from ..components.detector import Detector
from ..utils.classical_info_list import classical_info_list
from ..qkd.cascade import Cascade
from ..qkd.toeplitz_matrix import privacy_amplification

#TODO: Define SEED and MAIN_LEN (in meters)
SEED = 0
MAIN_LEN = 1000

env = simpy.Environment()
Alice = Node('A',env)
Bob = Node('B',env)

# Alice's Hardware Stack
WeakLaser = Weaklaser('WL',env,8e7,1550e-9,0.01e-9,100e-15,1e5,'Polarization',0.01,0.3,0.45,0,4,5)
print(f'The mean number of photons emitted by the weaklaser are: {WeakLaser.mu_photons_after_attenuation}')

#Channels linking Alice's Node to Bob's Node
QC = QuantumChannel('QC',env,MAIN_LEN,0.2e-3,1.47,0.90,17e-6,0.3)
CC = ClassicalChannel('CC',env,MAIN_LEN,1.47)

#Bob's Hardware Stack
NPBS = NonPolarizingBeamSplitter('NPBS',env,0.50)
QC_PBS_HV_Connection = QuantumChannel('QC_PBS_HV',env,0.5,0.2e-3,1.47,0.90,17e-6,0.3)
PBS_HV = PolarizingBeamSplitter('PBS_HV',env,1000)
QC_HWP_Connection = QuantumChannel('QC_HWP',env,0.25,0.2e-3,1.47,0.90,17e-6,0.3)
HWP = WavePlate('HWP',env,180,22.5)
QC_PBS_DA_Connection = QuantumChannel('QC_PBS_DA',env,0.25,0.2e-3,1.47,0.90,17e-6,0.3)
PBS_DA = PolarizingBeamSplitter('PBS_DA',env,1000)
QC_Det1_Connection = QuantumChannel('QC_D1',env,0.15,0.2e-3,1.47,0.90,17e-6,0.3)
Det1 = Detector('D1',env,1e-8,0.90,100,55e-12,0)
QC_Det2_Connection = QuantumChannel('QC_D2',env,0.15,0.2e-3,1.47,0.90,17e-6,0.3)
Det2 = Detector('D2',env,1e-8,0.90,100,55e-12,0)
QC_Det3_Connection = QuantumChannel('QC_D3',env,0.15,0.2e-3,1.47,0.90,17e-6,0.3)
Det3 = Detector('D3',env,1e-8,0.90,100,55e-12,1)
QC_Det4_Connection = QuantumChannel('QC_D4',env,0.15,0.2e-3,1.47,0.90,17e-6,0.3)
Det4 = Detector('D4',env,1e-8,0.90,100,55e-12,1)

Alice.add_components([WeakLaser,QC,CC])
Bob.add_components([QC,CC,NPBS,QC_PBS_HV_Connection,PBS_HV,QC_HWP_Connection,HWP,QC_PBS_DA_Connection,PBS_DA,QC_Det1_Connection,Det1,QC_Det2_Connection,Det2,QC_Det3_Connection,Det3,QC_Det4_Connection,Det4])

Alice.set_coupling_efficiencies({'QC':0.85})
Bob.set_coupling_efficiencies({'QC_PBS_HV':0.85,'QC_HWP':0.85,'QC_PBS_DA':0.85,'QC_D1':0.85,'QC_D2':0.85,'QC_D3':0.85,'QC_D4':0.85,'D1':0.90,'D2':0.90,'D3':0.90,'D4':0.90})

Bob.set_input_port_connections_for_beam_splitters({'NPBS':[1],'PBS_HV':1,'PBS_DA':2})

m_qs_coeffs_1 = np.array([[complex(1)],[complex(0)]])
m_qs_coeffs_2 = np.array([[complex(0)],[complex(1)]])
Bob.set_measured_qstate_coeffs_for_detectors({'D1':m_qs_coeffs_1,'D2':m_qs_coeffs_2,'D3':m_qs_coeffs_1,'D4':m_qs_coeffs_2})

Bob.connect_classical_channels({'CC':Alice})

Alice.connect_one_way_components({'WL':'QC'})
Bob.connect_one_way_components({'D1':'QC_D1','D2':'QC_D2','D3':'QC_D3','D4':'QC_D4'})

Alice.connect_two_way_internode_components({'QC':[[Alice,'WL'],[Bob,'NPBS']]})
Bob.connect_two_way_internode_components({'NPBS':[[Alice,'QC'],[Bob,'QC_PBS_HV',Bob,'QC_HWP']]})

Bob.connect_two_way_intranode_components({'QC_PBS_HV':['NPBS','PBS_HV'],'QC_HWP':['NPBS','HWP'],'HWP':['QC_HWP','QC_PBS_DA'],'QC_PBS_DA':['HWP','PBS_DA'],'PBS_HV':['QC_PBS_HV',['QC_D2','QC_D1']],'PBS_DA':['QC_PBS_DA',['QC_D4','QC_D3']],'QC_D1':['PBS_HV','D1'],'QC_D2':['PBS_HV','D2'],'QC_D3':['PBS_DA','D3'],'QC_D4':['PBS_DA','D4']})

Bob.identify_detectors()

Alice.calc_net_transmission_time(['WL'],Alice.all_components['WL'].lwidth,5)
Bob.calc_net_transmission_time(['QC','QC_PBS_HV','QC_D1'],Alice.all_components['WL'].lwidth,5)
total_net_min_transmission_time = Alice.min_net_transmission_time + Bob.min_net_transmission_time
total_net_max_transmission_time = Alice.max_net_transmission_time + Bob.max_net_transmission_time
print(f'The MINIMUM total transmission time through the QKD network is {total_net_min_transmission_time} s')
print(f'The MAXIMUM total transmission time through the QKD network is {total_net_max_transmission_time} s')
tol_time = 1e-13
total_net_max_transmission_time += tol_time

# START BB84
Bob.send_classical_information('CC',classical_info_list[0],Alice)

assert Alice.classical_info == classical_info_list[0]

desired_raw_bit_string_length = 128
transmission_bit_string_length = int(np.ceil(2.2*(desired_raw_bit_string_length/WeakLaser.mu_photons_after_attenuation)))

Alice_coeffs_list = Alice.gen.integers(2,size = transmission_bit_string_length)
Alice_basis_list = Alice.gen.integers(2,size = transmission_bit_string_length)

coeffs_list = [[complex(1),complex(0)],[complex(0),complex(1)]]
coeffs_list[0] = np.reshape(np.array(coeffs_list[0]),(len(coeffs_list[0]),1))
coeffs_list[1] = np.reshape(np.array(coeffs_list[1]),(len(coeffs_list[1]),1))

Bob_coeffs_list = []
Bob_basis_list = []

i = 0
Alice.send_classical_information('CC',classical_info_list[1],Bob)
assert Bob.classical_info == classical_info_list[1]

for a,b in zip(Alice_coeffs_list,Alice_basis_list):
    start_time = env.now
    
    Alice.all_components['WL'].emit_and_attenuate([coeffs_list[a]],encoding['Polarization'][b],1e6)
    setup_end_time = env.now
    
    basis_num,qs_measured = Bob.detection_analysis(total_net_min_transmission_time,total_net_max_transmission_time,start_time,setup_end_time)
    
    if type(qs_measured) != int:
        if np.allclose(qs_measured,coeffs_list[0]) and qs_measured.shape == coeffs_list[0].shape:
            qs_measured = 0
        elif np.allclose(qs_measured,coeffs_list[1]) and qs_measured.shape == coeffs_list[1].shape:
            qs_measured = 1
            
    Bob_coeffs_list.append(qs_measured)
    Bob_basis_list.append(basis_num)
    i += 1
    
Bob.calc_total_photon_counts()
    
Bob_coeffs_list = np.array(Bob_coeffs_list)
Bob_basis_list = np.array(Bob_basis_list)    

assert len(Alice_coeffs_list) == len(Bob_coeffs_list)
assert len(Alice_basis_list) == len(Bob_basis_list)

Alice.send_classical_information('CC',classical_info_list[2],Bob)
assert Bob.classical_info == classical_info_list[2]
Bob.send_classical_information('CC',classical_info_list[3],Alice)
assert Alice.classical_info == classical_info_list[3]

nz_count = 0

for i in range(len(Bob_basis_list)):
    if Bob_basis_list[i] != -1:
        nz_count += 1

raw_kgr = nz_count/env.now
print(f'The raw key generation rate is {raw_kgr} bits/s')

# SIFTING 
Alice.send_classical_information('CC',str(Alice_basis_list),Bob)
assert Bob.classical_info == str(Alice_basis_list)

same_basis_indices = []
for i in range(len(Alice_basis_list)):
    if Alice_basis_list[i] == Bob_basis_list[i]:
        same_basis_indices.append(i)
same_basis_indices_str = ' '.join(str(idx) for idx in same_basis_indices)
Bob.send_classical_information('CC',same_basis_indices_str,Alice)
assert Alice.classical_info == same_basis_indices_str
        
Alice.send_classical_information('CC',classical_info_list[4],Bob)
assert Bob.classical_info == classical_info_list[4]
        
same_coeffs_indices = []
for i in range(len(Alice_coeffs_list)):
    if Alice_coeffs_list[i] == Bob_coeffs_list[i]:
        same_coeffs_indices.append(i)
        
Alice_key_init = []
Bob_key_init = []

for i in range(len(Alice_coeffs_list)):
    for j in range(len(same_basis_indices)):
        if i == same_basis_indices[j]:
            Alice_key_init.append(Alice_coeffs_list[i])
            Bob_key_init.append(Bob_coeffs_list[i])
            
sifted_kgr = len(Bob_key_init)/env.now
print(f'The sifted key generation rate is {sifted_kgr} bits/s')
            
same_coeffs_at_same_basis_list = []
for i in range(len(Alice_key_init)):
    if Alice_key_init[i] == Bob_key_init[i]:
        same_coeffs_at_same_basis_list.append(Alice_key_init[i])

# INFORMATION RECONCILIATION        
Alice_key_init = np.array(Alice_key_init)
Bob_key_init = np.array(Bob_key_init)

key_idx_order = [*range(len(Alice_key_init))]
gen = np.random.default_rng(seed = SEED)
gen.shuffle(key_idx_order)
mid = int(0.5*(len(key_idx_order) - 1))
k1 = key_idx_order[0:mid+1]
k2 = key_idx_order[mid+1:len(key_idx_order)]
k2_str = ' '.join(str(idx) for idx in k2)
Alice.send_classical_information('CC',k2_str,Bob)
assert Bob.classical_info == k2_str

Alice.send_classical_information('CC',str(Alice_key_init[k2]),Bob)
assert Bob.classical_info == str(Alice_key_init[k2])
Bob.send_classical_information('CC',str(Bob_key_init[k2]),Alice)
assert Alice.classical_info == str(Bob_key_init[k2])

# QBER ESTIMATION
err = 0
for idx_k2 in k2:
    if Alice_key_init[idx_k2] != Bob_key_init[idx_k2]:
        err += 1
        
Alice.send_classical_information('CC',classical_info_list[5],Bob)
assert Bob.classical_info == classical_info_list[5]

err /= len(k2)
print(f'The estimated QBER is {err}')

if (err < 0.15):
    Alice_key_init = Alice_key_init[k1]
    Bob_key_init = Bob_key_init[k1]
    Alice_key_init = "".join(map(str, Alice_key_init))
    Bob_key_init = "".join(map(str, Bob_key_init))
    Alice.set_key(Alice_key_init)
    Bob.set_key(Bob_key_init)
    
    Alice_key_bit_list = np.array([int(i) for i in Alice.key])
    Bob_key_bit_list = np.array([int(i) for i in Bob.key])
    bit_mismatch_idx_list = np.where(Alice_key_bit_list != Bob_key_bit_list)

    # CASCADE PROTOCOL
    C = Cascade(err+0.02,4,Alice,Bob,'CC',SEED)
    Bob.send_classical_information('CC',classical_info_list[6],Alice)
    assert Alice.classical_info == classical_info_list[6]
    C.run()
    Bob.send_classical_information('CC',classical_info_list[7],Alice)
    assert Alice.classical_info == classical_info_list[7]
    
    reconciled_kgr = len(Bob.key)/env.now
    print(f'The reconciled key generation rate is {reconciled_kgr} bits/s')
    
    Bob_new_key_bit_list = np.array([int(i) for i in Bob.key])
    new_bit_mismatch_idx_list = np.where(Alice_key_bit_list != Bob_new_key_bit_list)
    
    final_key_len = len(Alice.key)//2
    Alice.send_classical_information('CC',classical_info_list[8],Bob)
    assert Bob.classical_info == classical_info_list[8]
    privacy_amplification(Alice,Bob,final_key_len,'CC')
    Alice.send_classical_information('CC',classical_info_list[9],Bob)
    assert Bob.classical_info == classical_info_list[9]
    
    secret_kgr = len(Bob.key)/env.now
    print(f'The secret key generation rate is {secret_kgr} bits/s')
    
else:
    # ABORT QKD
    Alice.send_classical_information('CC',classical_info_list[10],Bob)
    assert Bob.classical_info == classical_info_list[10]