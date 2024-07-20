# -*- coding: utf-8 -*-

import numpy as np

#TODO: Define SEED
SEED = 0

def toeplitz(r,init_bit_str_len,compressed_bit_str_len):
    
    """
    Constructs the Toeplitz Matrix
    
    Arguments:
        r (numpy.array) = Binary Random Vector
        init_bit_str_len (int) = Length of the Reconciled Key String
        compressed_bit_str_len (int) = Length of the Secret Key String
        
    Returned Value:
        T (numpy.array) = Toeplitz Matrix
    """
    
    T = np.ndarray((compressed_bit_str_len,init_bit_str_len))
    
    for i in range(compressed_bit_str_len):
        for j in range(init_bit_str_len):
            T[i,j] = r[i-j]
    
    return T

def privacy_amplification(NodeA,NodeB,final_key_len,cch_uID):
    
    """
    Performs Privacy Amplification 
    
    Arguments:
        NodeA (Node) = Sender Node
        NodeB (Node) = Receiver Node
        final_key_len (int) = Length of the Secret Key String
        cch_uID (str) = uID of the Classical Channel connecting the Sender and Receiver Nodes
    """
    
    global SEED
    
    toeplitz_gen = np.random.default_rng(seed = SEED)
    y = toeplitz_gen.integers(0,2,size = NodeA.key_len + final_key_len - 1)
    
    # Alice needs to send y to Bob via CC
    NodeA.send_classical_information(cch_uID,str(y),NodeB)
    assert NodeB.classical_info == str(y)
    
    T = toeplitz(y,NodeA.key_len,final_key_len)
    
    NodeA_key_bit_list = np.array([int(i) for i in NodeA.key])
    NodeB_key_bit_list = np.array([int(i) for i in NodeB.key])
    
    NodeA_key_bit_list = np.mod(T@NodeA_key_bit_list,2,casting = 'unsafe',dtype = np.int32)
    NodeB_key_bit_list = np.mod(T@NodeB_key_bit_list,2,casting = 'unsafe',dtype = np.int32)
    
    NodeA.key = "".join(map(str, NodeA_key_bit_list))
    NodeB.key = "".join(map(str, NodeB_key_bit_list))
    
    NodeA.key_int = int(NodeA.key,2)
    NodeA.key_len = final_key_len
    
    NodeB.key_int = int(NodeB.key,2)
    NodeB.key_len = final_key_len
    