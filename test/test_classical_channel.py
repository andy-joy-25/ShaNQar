# -*- coding: utf-8 -*-

import pytest
import simpy
from ..src.components.classical_channel import ClassicalChannel

UID = 'CC1'
ENV = simpy.Environment()
LENGTH = 1000
N_CORE = 1.50

INFO = 'START_QKD'

class FakeNode():
    
    def __init__(self):
        pass
    
    def receive_classical_information(self,uID,info):
        self.c_info = info

def test_init():
    CC1 = ClassicalChannel(UID,ENV,LENGTH,N_CORE)
    assert CC1.uID == UID
    assert CC1.length == LENGTH
    assert CC1.n_core == N_CORE
    
def test_set_environment():
    ENV_TEST = simpy.Environment()
    CC1 = ClassicalChannel(UID,ENV,LENGTH,N_CORE)
    CC1.set_environment(ENV_TEST)
    assert CC1.env == ENV_TEST
    
def test_connect():
    CC1 = ClassicalChannel(UID,ENV,LENGTH,N_CORE)
    E1 = FakeNode()
    E2 = FakeNode()
    CC1.connect(E1,E2)
    assert CC1.endpt1 == E1
    assert CC1.endpt2 == E2
    
def test_set_sender_and_receiver():
    CC1 = ClassicalChannel(UID,ENV,LENGTH,N_CORE)
    E1 = FakeNode()
    E2 = FakeNode()
    CC1.connect(E1,E2)
    CC1.set_sender_and_receiver(E2,E1)
    assert CC1.sender == E2
    assert CC1.receiver == E1
    
def test_transmit():
    CC1 = ClassicalChannel(UID,ENV,LENGTH,N_CORE)
    E1 = FakeNode()
    E2 = FakeNode()
    CC1.connect(E1,E2)
    CC1.set_sender_and_receiver(E2,E1)
    t_i = ENV.now
    CC1.transmit(INFO)
    t_f = ENV.now
    c = 3e8
    assert E1.c_info == INFO
    assert abs((t_f - t_i) - (LENGTH/(c/N_CORE))) < 1e-7