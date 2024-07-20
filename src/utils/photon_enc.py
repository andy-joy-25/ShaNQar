# -*- coding: utf-8 -*-

import numpy as np

"""
This file defines the various quantum information encoding schemes for photons

Supported Encoding Schemes:
    1. Polarization
"""

"""
Polarization Encoding Scheme Bases
"""

"""
Z BASIS (numpy.array(list[list[complex]])) (Horizontal and Vertical [HV] Polarizations) 
"""
HV_Basis = np.array([[complex(1),complex(0)],[complex(0),complex(1)]])

"""
X BASIS (numpy.array(list[list[complex]])) (Diagonal and Anti-Diagonal [DA] Polarizations)
"""
DA_Basis = np.array([[complex(1/np.sqrt(2)),complex(1/np.sqrt(2))],[complex(1/np.sqrt(2)),complex(-1/np.sqrt(2))]])

"""
Y BASIS (numpy.array(list[list[complex]])) (Right Circular and Left Circular Polarizations)
"""
RL_Basis = np.array([[complex(1/np.sqrt(2)),complex(0,(1/np.sqrt(2)))],[complex(1/np.sqrt(2)),complex(0,(-1/np.sqrt(2)))]])

"""
Dictionary (dict['str':list[numpy.array(list[list[complex]])]]) of all the encoding schemes (Key = Type of Encoding; Value = List of Bases)
"""
encoding = {'Polarization': [HV_Basis,DA_Basis,RL_Basis]}