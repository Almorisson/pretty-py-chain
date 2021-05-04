from hash_util import hash_string_256, hash_block

class Verification:
    @staticmethod
    def valid_proof(transactions, last_hash, proof):
        """
        Check if a Proof Number is valid or not
        Arguments:
            :transactions: List of Transaction data
            :last_hash: The lat hash of the current blockhain
            :proof: The proof number that we choose to make each hash unique fom the previous one
        """
        # Create a string with all the hash inputs
        guess = (str([tx.to_ordered_dict() for tx in transactions]) + str(last_hash) + str(proof)).encode()
        # Hash the string
        # IMPORTANT: This is NOT the same hash as will be stored in the previous_hash. It's a not a block's hash. It's only used for the proof-of-work algorithm.
        guess_hash = hash_string_256(guess)
        # Only a hash (which is based on the above inputs) which starts with two 0s is treated as valid
        # This condition is of course defined by us. It could also require 10 leading 0s - this would take significantly longer (and this allows you to control the speed at which new blocks can be added)
        return guess_hash[0:2] == "00"
    @staticmethod
    def verify_transaction(transaction, get_balance):
        """ Check if the sender has enough amount to sent to a recipient
        Arguments:
            :transaction: The transaction to check
            :get_balace: A method to get the balance of the sender
        """
        sender_balance = get_balance()
        return sender_balance >= transaction.amount
    @classmethod
    def verify_transactions(cls, open_transactions, get_balance):
        """Verifies all open transactions."""   
        return all([cls.verify_transaction(tx, get_balance) for tx in open_transactions])

    @classmethod
    def verify_chain(cls, blockchain):
        """ Verify the current blockchain and return True if it's valid, False otherwise."""
        for (index, block) in enumerate(blockchain):
            if index == 0:
                continue
            if block.previous_hash != hash_block(blockchain[index - 1]):
                return False
            if not cls.valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
                print('Proof of work is invalid!')
                return False
        return True
