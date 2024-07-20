#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import simpy
from ..src.components.component import Component

UID = 'c1'
ENV = simpy.Environment()

def test_init():
    C1 = Component(UID,ENV)
    assert C1.uID == UID
    assert C1.env == ENV