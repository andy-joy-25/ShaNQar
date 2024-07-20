# -*- coding: utf-8 -*-

from ..components.component import Component

class ClassicalChannel(Component):
    
    """
    Models a Classical Channel (Fiber for the transmission of Classical Information)
    
    Attributes:
        uID (str) = Unique ID
        env (simpy.Environment) = Simpy Environment for Simulation
        gen (numpy.random.Generator) = Random Number Generator
        length (float) = Length
        n_core (float) = Refractive Index of the Core 
        endpt1 (Node) = Node at the 1st End Point of the Channel
        endpt2 (Node) = Node at the 2nd End Point of the Channel
        sender (Node) = Sender Node 
        receiver (Node) = Receiver Node
    """

    def __init__(self,uID,env,length,n_core):
        
        """
        Constructor for the Classical Channel class
        
        Arguments:
            uID (str) = Unique ID
            env (simpy.Environment) = Simpy Environment for Simulation
            length (float) = Length
            n_core (float) = Refractive Index of the Core
        """
        
        Component.__init__(self,uID,env)
        self.length = length
        self.n_core = n_core   

    def set_environment(self,env):
        
        """
        Instance method to set the environment of a classical channel
        
        Arguments:
            env (Simpy.Environment) = Simpy Environment for Timing Control and Synchronisation 
        """
        
        self.env = env            
        
    def connect(self,endpt1,endpt2):
        
        """
        Instance method to connect a classical channel with its end point nodes
        
        Arguments:
            endpt1 (Node) = Node at the 1st End Point of the Channel
            endpt2 (Node) = Node at the 2nd End Point of the Channel
            
        Details:
            A classical channel is a two way communication channel and hence, this function just sets the end points of the channel
        """
        
        self.endpt1 = endpt1
        self.endpt2 = endpt2
        
    def set_sender_and_receiver(self,sender,receiver):
        
        """
        Instance method to set the sender and the receiver of the classical channel
        
        Arguments:
            source (Node) = Sender of the Information to be transmitted 
            receiver (Node) = Receiver of the transmitted Information
            
        Details:
            The sender and the receiver must necessarily be the previously specified end points of the channel
        """
        if sender == self.endpt1:
            assert receiver == self.endpt2,"Wrong Channel Configuration!"
        elif sender == self.endpt2:
            assert receiver == self.endpt1,"Wrong Channel Configuration!"
        else:
            assert sender == self.endpt1,"Wrong Channel Configuration!"
            
        self.sender = sender
        self.receiver = receiver

    def transmit(self,info):
        
        """
        Instance method to transmit the received information 
        
        Details:
            Transmission of information via a classical channel is assumed to be a lossless process
        
        Arguments:
            info (str) = Classical Information to be transmitted
        """
        
        c = 3e8
        transmission_time = self.length/(c/self.n_core)
        self.env.timeout(transmission_time)
        self.env.run()
        self.receiver.receive_classical_information(self.uID,info)
