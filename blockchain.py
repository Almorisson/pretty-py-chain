# python standard imports
from functools import reduce
import hashlib as hl
from json import dumps, loads
# from pickle import dumps, loads

# file project imports
from hash_util import hash_string_256, hash_block
from block import Block
from transaction import Transaction
from verication import Verification

# The reward to send to a miner for each complete new mining block
MINING_REWARD = 10


class Blockchain:
    def __init__(self, hosting_node):
        """
            class constructor
            Arguments:
            :self: Automatically passed by Python
            :hosting_node: The Node(Machine) witch will be added to the Blockchain network
        """
        # Create the genesis Block of the Blockchain and Initializing the Blockchain list
        genesis_block = Block(0, "", [], 2008)
        self.chain = [genesis_block]
        self.hosting_node = hosting_node
        # Unhandled transactions
        self.__open_transactions = []
        # Load the previos state of the blochain
        self.load_data()
    @property
    def chain(self):
        """ The getter of the chain property """
        # we return a copy ao the Blockchain Object and not the Object itself
        # Don't use this getter inside this class but only outside to avoid unpredictable behaviors
        return self.__chain[:]
    
    @chain.setter
    def chain(self, value):
        """ The setter of the chain property """
        self.__chain = value

    def get_open_transactions(self):
        return self.__open_transactions[:]

    def load_data(self):
        try:
            with open('blockchain.txt', mode='r') as f:
                file_content = f.readlines()
                # blockchain = loads(file_content['chain'])
                # open_transactions = loads(file_content['ot'])
                blockchain = loads(file_content[0][:-1])
                updated_blockchain = []
                for block in blockchain:
                    converted_tx = [Transaction(
                        tx['sender'], tx['recipient'], tx['amount']) for tx in block['transactions']]
                    # converted_tx = [OrderedDict([('sender', tx['sender']), ('recipient', tx['recipient']), (
                    #     'amount', tx['amount'])]) for tx in block['transactions']]
                    updated_block = Block(
                        block['index'], block['previous_hash'], converted_tx, block['proof'], block['timestamp'])
                    updated_blockchain.append(updated_block)
                self.chain = updated_blockchain
                open_transactions = loads(file_content[1])
                updated_transactions = []
                for tx in open_transactions:
                    updated_transaction = Transaction(
                        tx['sender'], tx['recipient'], tx['amount'])
                    # updated_transaction = OrderedDict(
                    # [('sender', tx['sender']), ('recipient', tx['recipient']), ('amount', tx['amount'])])
                    updated_transactions.append(updated_transaction)
                self.__open_transactions = updated_transactions
        except (IOError, IndexError):
            pass
        finally:
            print("clean up!")

    def save_data(self):
        """ Save the blockchain data in a file """
        try:
            with open('blockchain.txt', mode='w') as f:
                saveable_chain = [block.__dict__ for block in [Block(block_el.index, block_el.previous_hash, [tx.to_ordered_dict(
                ) for tx in block_el.transactions], block_el.proof, block_el.timestamp) for block_el in self.__chain]]
                f.write(dumps(saveable_chain))
                f.write('\n')
                saveable_transactions = [
                    open_tx.__dict__ for open_tx in self.__open_transactions]
                f.write(dumps(saveable_transactions))
                # data = dumps({
                #     'chain': blockchain,
                #     'ot': open_transactions
                # })
                # f.write(data)
        except IOError:
            print("File saving failed!")

    def get_last_blockchain_value(self):
        """ Return the last blockchain value """
        if len(self.__chain) < 1:
            return None
        return self.__chain[-1]

    def get_balance(self):
        """
            Calculate and return the balance for a participant.
        """
        participant = self.hosting_node
        # Fetch a list of all sent coin amounts for the given person (empty lists are returned if the person was NOT the sender)
        # This fetches sent amounts of transactions that were already included in blocks of the blockchain
        tx_sender = [[tx.amount for tx in block.transactions
                      if tx.sender == participant] for block in self.__chain]
        # Fetch a list of all sent coin amounts for the given person (empty lists are returned if the person was NOT the sender)
        # This fetches sent amounts of open transactions (to avoid double spending)
        tx_open_sender = [
            tx.amount for tx in self.__open_transactions if tx.sender == participant]
        tx_sender.append(tx_open_sender)
        print("Sender Transaction: ", tx_sender)
        amount_sent = reduce(
            lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum, tx_sender, 0)
        # This fetches received coin amounts of transactions that were already included in blocks of the blockchain
        # We ignore open transactions here because you shouldn't be able to spend coins before the transaction was confirmed + included in a block
        tx_recipient = [[tx.amount for tx in block.transactions
                        if tx.recipient == participant] for block in self.__chain]
        amount_received = reduce(
            lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum, tx_recipient, 0)

        return amount_received - amount_sent

    # This function accepts two arguments.
    # One required one (transaction_amount) and one optional one (last_transaction)
    # The optional one is optional because it has a default value => [1]

    def add_transaction(self, recipient, sender, amount=1.0):
        """ Add each new transaction amount in the blockchain

            Arguments:
                :sender: The sender of the transaction
                :recipient: The recipient of the transaction
                :amount: The amount of coins to send. default(amount=1.0)
        """
        transaction = Transaction(sender, recipient, amount)
        # Check first if the transaction is valid
        if Verification.verify_transaction(transaction, self.get_balance):
            self.__open_transactions.append(transaction)
            self.save_data()
            return True

        return False

    def proof_of_work(self):
        """
            Proof of Work mechanism that ensure that transactions are securely validate
        """
        last_block = self.__chain[-1]
        last_hash = hash_block(last_block)
        proof = 0
        while not Verification.valid_proof(self.__open_transactions, last_hash, proof):
            proof += 1
        return proof

    def mine_block(self):
        """
            Mines a new block (and its transactions) and add it to the Blockchain
        """
        last_block = self.__chain[-1]
        hashed_block = hash_block(last_block)
        proof = self.proof_of_work()
        tx_reward = Transaction("Miner", self.hosting_node, MINING_REWARD)
        # Copy transactions instead of manipulating the original open_transactions
        # This ensure that if the mining fail for some reason, we don't have errors
        copied_transactions = self.__open_transactions[:]
        copied_transactions.append(tx_reward)
        block = Block(len(self.__chain), hashed_block,
                      copied_transactions, proof)
        self.__chain.append(block)
        self.__open_transactions = []
        self.save_data()
        return True
