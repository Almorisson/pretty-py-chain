from time import time

from utility.printable import Printable


class Block(Printable):
    def __init__(self, index, previous_hash, transactions, proof, time=time()):
        """
            class constructor
            Arguments:
            :self: Automatically passed by Python
            :index: The index of a given Block
            :previous_hash: Previous hash of a given Block
            :transactions: List of transactions
            :proof: The Proof(none) number for the proof-of-work algorithm
            :time: The current timestamp when instianting a new Block
        """
        self.index = index
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.proof = proof
        self.timestamp = time
