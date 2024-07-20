#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import numpy as np
import simpy
from ..src.components.node import Node
from ..src.components.detector import Detector
from ..src.components.quantum_channel import QuantumChannel
from ..src.components.weaklaser import Weaklaser
from ..src.components.non_polarizing_beam_splitter import NonPolarizingBeamSplitter
from ..src.components.polarizing_beam_splitter import PolarizingBeamSplitter
from ..src.components.classical_channel import ClassicalChannel
from ..src.components.SPDC import EntangledPhotonsSourceSPDC
from ..src.utils.classical_info_list import classical_info_list

ENV = simpy.Environment()
UID = 'N1'

def test_init():
    N = Node(UID,ENV)
    assert N.uID == UID
    assert N.env == ENV
    
def test_add_components():
    N = Node(UID,ENV)
    QuCh = QuantumChannel('QC',ENV,1000,0.2e-3,1.47,0.90,17e-6,0.3)
    PBS = PolarizingBeamSplitter('PBS_HV',ENV,1000)
    Det = Detector('D',ENV,1e-8,0.90,100e6,55e-12,0)
    N.add_components([QuCh,PBS,Det])
    assert N.all_components['QC'] == QuCh
    assert N.all_components['PBS_HV'] == PBS
    assert N.all_components['D'] == Det
    
def test_set_coupling_efficiencies():
    N = Node(UID,ENV)
    QuCh = QuantumChannel('QC',ENV,1000,0.2e-3,1.47,0.90,17e-6,0.3)
    Det = Detector('D',ENV,1e-8,0.90,100e6,55e-12,0)
    N.add_components([QuCh,Det])
    CE_DICT = {'QC':0.90,'D':0.80}
    N.set_coupling_efficiencies(CE_DICT)
    assert QuCh.coupling_eff == CE_DICT['QC']
    assert Det.coupling_eff == CE_DICT['D']
    
def test_set_input_port_connections_for_beam_splitters():
    N = Node(UID,ENV)
    NPBS = NonPolarizingBeamSplitter('NPBS',ENV,0.50)
    PBS1 = PolarizingBeamSplitter('PBS_HV',ENV,1000)
    PBS2 = PolarizingBeamSplitter('PBS_DA',ENV,1000)
    N.add_components([NPBS,PBS1,PBS2])
    IP_CONNECTION_DICT = {'NPBS':[2],'PBS_HV':2,'PBS_DA':1}
    N.set_input_port_connections_for_beam_splitters(IP_CONNECTION_DICT)
    assert N.all_components['NPBS'].input_port_net == IP_CONNECTION_DICT['NPBS']
    assert N.all_components['PBS_HV'].input_port == IP_CONNECTION_DICT['PBS_HV']
    assert N.all_components['PBS_DA'].input_port == IP_CONNECTION_DICT['PBS_DA']
    
def test_set_measured_qstate_coeffs_for_detectors():
    N = Node(UID,ENV)
    Det1 = Detector('D1',ENV,1e-8,0.90,100e6,55e-12,0)
    Det2 = Detector('D2',ENV,1e-8,0.90,100e6,55e-12,1)
    N.add_components([Det1,Det2])
    M_QS_COEFFS_1 = np.array([[complex(1)],[complex(0)]])
    M_QS_COEFFS_2 = np.array([[complex(0)],[complex(1)]])
    M_QS_COEFFS_DICT = {'D1':M_QS_COEFFS_1,'D2':M_QS_COEFFS_2}
    N.set_measured_qstate_coeffs_for_detectors(M_QS_COEFFS_DICT)
    assert np.allclose(Det1.measured_qs_coeffs,M_QS_COEFFS_DICT['D1'])
    assert np.allclose(Det2.measured_qs_coeffs,M_QS_COEFFS_DICT['D2'])
    
def test_connect_classical_channels():
    Node1 = Node(UID,ENV)
    Node2 = Node('N2',ENV)
    CCh1 = ClassicalChannel('CC1',ENV,1000,1.47)
    CCh2 = ClassicalChannel('CC2',ENV,1500,1.52)
    Node1.add_components([CCh1,CCh2])
    Node2.add_components([CCh1,CCh2])
    Node1.connect_classical_channels({'CC1':Node2})
    Node2.connect_classical_channels({'CC2':Node1})
    assert CCh1.endpt1 == Node1 and CCh1.endpt2 == Node2
    assert CCh2.endpt1 == Node2 and CCh2.endpt2 == Node1
    
def test_connect_one_way_components():
    Node1 = Node(UID,ENV)
    ENV1 = simpy.Environment()
    ENV2 = simpy.Environment()
    EPhS = EntangledPhotonsSourceSPDC('EPS',ENV,76e6,775e-9,0.01e-9,200e-15,1e6,'Polarization',0.01,0.3,0.45,2,[ENV1,ENV2],1e-6)
    WeakLaser = Weaklaser('WL',ENV,76e6,1550e-9,0.01e-9,200e-15,1e5,'Polarization',0.01,0.3,0.45,0,4,5,calc_mu_photons_after_attenuation = False)
    QCh_EPS1 = QuantumChannel('QC_EPS1',ENV,100,0.2e-3,1.47,0.90,17e-6,0.3)
    QCh_EPS2 = QuantumChannel('QC_EPS2',ENV,1000,0.2e-3,1.47,0.90,17e-6,0.3) 
    QCh_WL = QuantumChannel('QC_WL',ENV,100,0.2e-3,1.47,0.90,17e-6,0.3)
    Node1.add_components([EPhS,WeakLaser,QCh_EPS1,QCh_EPS2,QCh_WL])
    ONE_WAY_CONNECTIONS = {'WL':'QC_WL','EPS':['QC_EPS1','QC_EPS2']}
    Node1.connect_one_way_components(ONE_WAY_CONNECTIONS)
    assert Node1.all_components['WL'].receiver == Node1.all_components[ONE_WAY_CONNECTIONS['WL']]
    assert Node1.all_components['EPS'].receivers[0] == Node1.all_components[ONE_WAY_CONNECTIONS['EPS'][0]]
    assert Node1.all_components['EPS'].receivers[1] == Node1.all_components[ONE_WAY_CONNECTIONS['EPS'][1]]
    
    
def test_connect_two_way_internode_components():
    Node1 = Node(UID,ENV)
    Node2 = Node('N2',ENV)
    WeakLaser = Weaklaser('WL',ENV,76e6,1550e-9,0.01e-9,200e-15,1e5,'Polarization',0.01,0.3,0.45,0,4,5,calc_mu_photons_after_attenuation = False)
    QuCh = QuantumChannel('QC',ENV,1000,0.2e-3,1.47,0.90,17e-6,0.3)
    NPBS = NonPolarizingBeamSplitter('NPBS',ENV,0.50)
    QC_NPBS_Connection1 = QuantumChannel('QC_NPBS1',ENV,0.5,0.2e-3,1.47,0.90,17e-6,0.3)
    QC_NPBS_Connection2 = QuantumChannel('QC_NPBS2',ENV,0.5,0.2e-3,1.47,0.90,17e-6,0.3)
    Node1.add_components([WeakLaser,QuCh])
    Node2.add_components([QuCh,NPBS,QC_NPBS_Connection1,QC_NPBS_Connection2])
    NODE1_TWO_WAY_INTER_NODE_CONNECTIONS_DICT = {'QC':[[Node1,'WL'],[Node2,'NPBS']]}
    Node1.connect_two_way_internode_components(NODE1_TWO_WAY_INTER_NODE_CONNECTIONS_DICT)
    NODE2_TWO_WAY_INTER_NODE_CONNECTIONS_DICT = {'NPBS':[[Node1,'QC'],[Node2,'QC_NPBS1',Node2,'QC_NPBS2']]}
    Node2.connect_two_way_internode_components(NODE2_TWO_WAY_INTER_NODE_CONNECTIONS_DICT)
    assert Node1.all_components['QC'].sender == NODE1_TWO_WAY_INTER_NODE_CONNECTIONS_DICT['QC'][0][0].all_components[NODE1_TWO_WAY_INTER_NODE_CONNECTIONS_DICT['QC'][0][1]]
    assert Node1.all_components['QC'].receiver == NODE1_TWO_WAY_INTER_NODE_CONNECTIONS_DICT['QC'][1][0].all_components[NODE1_TWO_WAY_INTER_NODE_CONNECTIONS_DICT['QC'][1][1]]
    assert Node2.all_components['NPBS'].senders[0] == NODE2_TWO_WAY_INTER_NODE_CONNECTIONS_DICT['NPBS'][0][0].all_components[NODE2_TWO_WAY_INTER_NODE_CONNECTIONS_DICT['NPBS'][0][1]]
    assert Node2.all_components['NPBS'].receivers[0] == NODE2_TWO_WAY_INTER_NODE_CONNECTIONS_DICT['NPBS'][1][0].all_components[NODE2_TWO_WAY_INTER_NODE_CONNECTIONS_DICT['NPBS'][1][1]]
    assert Node2.all_components['NPBS'].receivers[1] == NODE2_TWO_WAY_INTER_NODE_CONNECTIONS_DICT['NPBS'][1][2].all_components[NODE2_TWO_WAY_INTER_NODE_CONNECTIONS_DICT['NPBS'][1][3]]
    
def test_connect_two_way_intranode_components():
    Node1 = Node(UID,ENV)
    QuCh = QuantumChannel('QC',ENV,1000,0.2e-3,1.47,0.90,17e-6,0.3)
    NPBS = NonPolarizingBeamSplitter('NPBS',ENV,0.50)
    PBS = PolarizingBeamSplitter('PBS_HV',ENV,1000)
    QCh_PBS1 = QuantumChannel('QC_PBS1',ENV,0.5,0.2e-3,1.47,0.90,17e-6,0.3)
    QCh_PBS2 = QuantumChannel('QC_PBS2',ENV,0.5,0.2e-3,1.47,0.90,17e-6,0.3) 
    Node1.add_components([QuCh,NPBS,PBS,QCh_PBS1,QCh_PBS2])
    TWO_WAY_INTRA_NODE_CONNECTIONS = {'QC':['NPBS','PBS_HV'], 'PBS_HV':['QC',['QC_PBS1','QC_PBS2']]}
    Node1.connect_two_way_intranode_components(TWO_WAY_INTRA_NODE_CONNECTIONS)
    assert Node1.all_components['QC'].sender == Node1.all_components[TWO_WAY_INTRA_NODE_CONNECTIONS['QC'][0]]
    assert Node1.all_components['QC'].receiver == Node1.all_components[TWO_WAY_INTRA_NODE_CONNECTIONS['QC'][1]]
    assert Node1.all_components['PBS_HV'].sender == Node1.all_components[TWO_WAY_INTRA_NODE_CONNECTIONS['PBS_HV'][0]]
    assert Node1.all_components['PBS_HV'].receivers[0] == Node1.all_components[TWO_WAY_INTRA_NODE_CONNECTIONS['PBS_HV'][1][0]]
    assert Node1.all_components['PBS_HV'].receivers[1] == Node1.all_components[TWO_WAY_INTRA_NODE_CONNECTIONS['PBS_HV'][1][1]]
    
def test_send_classical_information():
    Node1 = Node(UID,ENV)
    Node2 = Node('N2',ENV)
    CCh = ClassicalChannel('CC',ENV,1000,1.47)
    Node1.add_components([CCh])
    Node2.add_components([CCh])
    Node1.connect_classical_channels({'CC':Node2})
    Node1.send_classical_information('CC',classical_info_list[0],Node2)
    assert Node2.classical_info == classical_info_list[0]
    
def test_set_key():
    Node1 = Node(UID,ENV)
    KEY = '01011'
    Node1.set_key(KEY)
    assert Node1.key == KEY
    assert Node1.key_int == 11
    assert Node1.key_len == 5
    
def test_identify_detectors():
    Node1 = Node(UID,ENV)
    QuCh = QuantumChannel('QC',ENV,1000,0.2e-3,1.47,0.90,17e-6,0.3)
    NPBS = NonPolarizingBeamSplitter('NPBS',ENV,0.50)
    PBS = PolarizingBeamSplitter('PBS_HV',ENV,1000)
    Det1 = Detector('D1',ENV,1e-8,0.90,100e6,55e-12,0)
    Det2 = Detector('D2',ENV,1e-8,0.90,100e6,55e-12,1)
    Node1.add_components([QuCh,Det1,NPBS,PBS,Det2])
    Node1.identify_detectors()
    assert Node1.detectors['D1'] == Det1
    assert Node1.detectors['D2'] == Det2