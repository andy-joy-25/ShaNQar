# -*- coding: utf-8 -*-

import math
import numpy as np

class Cascade():
    
    """
    Implements the Cascade Protocol 
    
    Reference:
        A. Choudhary and A. Wasan, "Cracking the Curious Case of the Cascade Protocol," IEEE Access, vol. 11, pp. 84709-84733, 2023
    
    Attributes:
        eps (float) = Estimate of the QBER
        k (int) = Block Size
        omega (int) = Total Number of Passes
        A (Node) = Sender Node
        B (Node) = Receiver Node
        cch_uID (str) = uID of the Classical Channel connecting A and B
        gen (numpy.random.Generator) = Random Number Generator
    """
    
    def __init__(self,eps,omega,NodeA,NodeB,cch_uID,SEED): 
        
        """
        Constructor for the Cascade class
        
        Arguments:
            eps (float) = Estimate of the QBER
            omega (int) = Total Number of Passes
            NodeA (Node) = Sender Node
            NodeB (Node) = Receiver Node
            cch_uID (str) = uID of the Classical Channel connecting A and B
            seed (int) = Seed for Random Number Generation
        """
        
        self.A = NodeA
        self.B = NodeB
        self.cch_UID = cch_uID
        self.k = math.floor(0.73/eps)
        self.omega = omega 
        self.chk_blk_idx_list = []
        self.net_blk_idx_lists = {}
        self.gen = np.random.default_rng(seed = SEED)
    
   
    @staticmethod
    def parity(bit_str_int,len_bit_str_int,idx_list_net):
        
        """
        Static Method for implementing the Parity Primitive (Algorithm 1 of the referenced Paper)
        
        Arguments:
            bit_str_int (int) = Integer Equivalent of the Binary Key
            len_bit_str_int (int) = Length of the Binary Key
            idx_list_net (list[list[int]]) = List of Indices corresponding to all the Blocks in the Binary Key
            
        Returned Value:
            p_net (numpy.array or int) = Parity(ies) of all the Blocks in the Binary Key
        """
        
        p_net = np.zeros((len(idx_list_net),1)).astype(dtype = int)
        for k,idx_list in enumerate(idx_list_net):
            idx_list = [len_bit_str_int - 1 - j for j in idx_list]
            for i in idx_list:
                p_net[k] ^= (bit_str_int >> i) & 1
        if p_net.shape == (1,1):
            p_net = p_net[0][0]
        return p_net


    def binary(self):
        
        """
        Static Method for implementing the Binary Primitive (Algorithm 2 of the referenced Paper)
        """
        
        beg = 0
        end = len(self.chk_blk_idx_list) - 1
        while beg < end:
            mid = int(0.5*(beg+end))
            chk_list1 = self.chk_blk_idx_list[beg:mid+1]
            chk_list2 = self.chk_blk_idx_list[mid+1:end+1]
            self.B.send_classical_information(self.cch_UID,str(chk_list1),self.A)
            assert self.A.classical_info == str(chk_list1)
            A_parity = self.parity(self.A.key_int,self.A.key_len,[chk_list1])
            self.A.send_classical_information(self.cch_UID,str(A_parity),self.B)
            assert self.B.classical_info == str(A_parity)
            B_parity = self.parity(self.B.key_int,self.B.key_len,[chk_list1])
            if B_parity != A_parity:
                end = mid
                self.net_blk_idx_lists[self.pass_num].append(chk_list2)
            else:
                beg = mid + 1
                self.net_blk_idx_lists[self.pass_num].append(chk_list1)
        idx_for_bit_flip = self.chk_blk_idx_list[beg]

        self.B.key_int ^= int('0'*idx_for_bit_flip+'1'+'0'*(self.B.key_len - idx_for_bit_flip - 1),2)

        return idx_for_bit_flip
        
    def run(self):
        
        """
        Instance Method for implementing the full Cascade Protocol (Algorithm 3 of the referenced Paper)
        """
        
        key_idx_order = [*range(self.A.key_len)]
        for i in range(1,self.omega+1):
            
            if i > 1:
                self.gen.shuffle(key_idx_order)
            self.pass_num = i
            self.net_blk_idx_lists[i] = []
            blk_idx_lists = []
            
            for l in range(1,math.ceil(self.A.key_len/self.k)+1):
                blk_idx_lists.append(key_idx_order[(l-1)*self.k:min(l*self.k,self.A.key_len)])
            
            self.B.send_classical_information(self.cch_UID,str(blk_idx_lists),self.A)
            assert self.A.classical_info == str(blk_idx_lists)
            A_parity_list = self.parity(self.A.key_int,self.A.key_len,blk_idx_lists)
            self.A.send_classical_information(self.cch_UID,str(A_parity_list),self.B)
            assert self.B.classical_info == str(A_parity_list)
            B_parity_list = self.parity(self.B.key_int,self.B.key_len,blk_idx_lists)
            odd_error_parity_blk_idx_list = np.where(A_parity_list != B_parity_list)[0]
            even_error_parity_blk_idx_list = np.where(A_parity_list == B_parity_list)[0]
            
            for j in even_error_parity_blk_idx_list:
                self.net_blk_idx_lists[i].append(blk_idx_lists[j])
            net_idx_for_bit_flip = []
            complete_idx_set_for_bit_flip = []
            
            for chk_blk_idx in odd_error_parity_blk_idx_list:
                self.chk_blk_idx_list = blk_idx_lists[chk_blk_idx]
                bit_flip_index = self.binary()
                net_idx_for_bit_flip.append(bit_flip_index)
                complete_idx_set_for_bit_flip.append(bit_flip_index)
                
            if i > 1:
                chk_blk_idx_lists = []
                for bflip_idx in net_idx_for_bit_flip:
                    for k in range(i-1,0,-1):
                        for sublist in self.net_blk_idx_lists[k]:
                            if bflip_idx in sublist:
                                if sublist not in chk_blk_idx_lists:
                                    chk_blk_idx_lists.append(sublist)
                                    
                while (len(chk_blk_idx_lists) != 0):
                    chk_blk_idx_lists.sort(key=len)
                    self.chk_blk_idx_list = chk_blk_idx_lists[0]
                    values = list(self.net_blk_idx_lists.values())
                    for val in values:
                        if self.chk_blk_idx_list in val:
                            chk_blk_pass_num = values.index(val) + 1
                    chk_blk_idx_lists.remove(self.chk_blk_idx_list)
                    parity_check = 0 
                    for error_idx in complete_idx_set_for_bit_flip:
                        if error_idx in self.chk_blk_idx_list:
                            parity_check += 1
                    if parity_check%2 != 0:  
                        self.net_blk_idx_lists[chk_blk_pass_num].remove(self.chk_blk_idx_list)
                        self.pass_num = chk_blk_pass_num
                        bit_flip_index = self.binary()
                        complete_idx_set_for_bit_flip.append(bit_flip_index)
                        chk_blk_new_additions = []
                        for k in range(i,0,-1):
                            if k != chk_blk_pass_num:
                                for sublist in self.net_blk_idx_lists[k]:
                                    if bit_flip_index in sublist:
                                        chk_blk_new_additions.append(sublist)
                        if len(chk_blk_new_additions) != 0:
                            for new_add in chk_blk_new_additions:
                                if new_add not in chk_blk_idx_lists:
                                    chk_blk_idx_lists.append(new_add) 
                        
                                    
            self.k = 2*self.k
        
        B_key_new = bin(self.B.key_int)[2:]
        self.B.key = '0'*(self.A.key_len - len(B_key_new)) + B_key_new