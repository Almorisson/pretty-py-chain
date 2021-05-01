# python standard imports
from functools import reduce
import hashlib as hl
from collections import OrderedDict
from json import dumps, loads

# file project imports
from hash_util import hash_string_256, hash_block

# The reward to send to a miner for each complete new mining block
MINING_REWARD = 10

# Create the genesis Block of the Blockchain
genesis_block = {
    'previous_hash': "",
    'index': 0,
    'transactions': [],
    'proof': '2008'
}

# Declaring and Initializing the blockchain list
blockchain = [genesis_block]
open_transactions = []
owner = "Mountakha"
participants = {owner}


def load_data():
    with open('blockchain.txt', mode='r') as f:
        file_content = f.readlines()
        global blockchain
        global open_transactions
        blockchain = loads(file_content[0][:-1])
        updated_blockchain = []
        for block in blockchain:
            updated_block = {
                'previous_hash': block['previous_hash'],
                'index': block['index'],
                'proof': block['proof'],
                'transactions': [OrderedDict([('sender', tx['sender']), ('recipient', tx['recipient']), ('amount', tx['amount'])]) for tx in block['transactions']]
            }
            updated_blockchain.append(updated_block)
        blockchain = updated_blockchain
        open_transactions = loads(file_content[1])
        updated_transactions = []
        for tx in open_transactions:
            updated_transaction = OrderedDict(
                [('sender', tx['sender']), ('recipient', tx['recipient']), ('amount', tx['amount'])])
            updated_transactions.append(updated_transaction)
        open_transactions = updated_transactions


load_data()


def save_data():
    """ Save the blockchain data in a file """
    with open('blockchain.txt', mode='w') as f:
        f.write(dumps(blockchain))
        f.write('\n')
        f.write(dumps(open_transactions))


def get_last_blockchain_value():
    """ Return the last blockchain value """
    if len(blockchain) < 1:
        return None
    return blockchain[-1]


def get_balance(participant):
    """
        Calculate and return the balance for a participant.

        Arguments:
            :participant: The person for whom to calculate the balance.
    """
    # Fetch a list of all sent coin amounts for the given person (empty lists are returned if the person was NOT the sender)
    # This fetches sent amounts of transactions that were already included in blocks of the blockchain
    tx_sender = [[tx['amount'] for tx in block['transactions']
                  if tx['sender'] == participant] for block in blockchain]
    # Fetch a list of all sent coin amounts for the given person (empty lists are returned if the person was NOT the sender)
    # This fetches sent amounts of open transactions (to avoid double spending)
    tx_open_sender = [tx['amount']
                      for tx in open_transactions if tx['sender'] == participant]
    tx_sender.append(tx_open_sender)
    print("Sender Transaction: ", tx_sender)
    amount_sent = reduce(
        lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum, tx_sender, 0)
    # This fetches received coin amounts of transactions that were already included in blocks of the blockchain
    # We ignore open transactions here because you shouldn't be able to spend coins before the transaction was confirmed + included in a block
    tx_recipient = [[tx['amount'] for tx in block['transactions']
                     if tx['recipient'] == participant] for block in blockchain]
    amount_received = reduce(
        lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum, tx_recipient, 0)

    return amount_received - amount_sent

# This function accepts two arguments.
# One required one (transaction_amount) and one optional one (last_transaction)
# The optional one is optional because it has a default value => [1]


def add_transaction(recipient, sender=owner, amount=1.0):
    """ Add each new transaction amount in the blockchain

        Arguments:
            :sender: The sender of the transaction
            :recipient: The recipient of the transaction
            :amount: The amount of coins to send. default(amount=1.0)
    """

    # transaction = {
    #     'sender': sender,
    #     'recipient': recipient,
    #     'amount': amount
    # }
    transaction = OrderedDict(
        [('sender', sender), ('recipient', recipient), ('amount', amount)])
    # Check first if the transaction is valid
    if verify_transaction(transaction):
        open_transactions.append(transaction)
        participants.add(recipient)
        participants.add(sender)
        save_data()
        return True

    return False


def verify_transaction(transaction):
    """ Check if the sender has enough amount to sent to a recipient
        Arguments:
            :transaction: The transaction to check
    """
    sender_balance = get_balance(transaction['sender'])
    return sender_balance >= transaction['amount']


def get_transaction_value():
    """ Return the user data needed to make a valid transaction"""
    tx_recipient = input("Please, enter the recipient to send coins: ")
    tx_amount = float(input("Please, enter the amount of coins to sends: "))
    return (tx_recipient, tx_amount)


def get_user_choice():
    """ Return the user's choice """
    user_choice = input("Your choice: ")
    return user_choice


def print_blockchain_elements():
    """ Prints each block of the Blockchain """
    counter = 0;
    for block in blockchain:
        print("Outputting blocks: \n")
        if counter > 0:
            print(f"Block #{counter}: {block}")
        print(f"Block genesis: {block}") 
        counter += 1
    else:   
        print("-" * 20)


def valid_proof(transactions, last_hash, proof):
    """
        Check if a Proof Number is valid or not
        Arguments:
            :transactions: Transactions data
            :last_hash: The lat hash of the current blockhain
            :proof: The proof number that we choose to make each hash unique fom the previous one
    """
    # Create a string with all the hash inputs
    guess = (str(transactions) + str(last_hash) + str(proof)).encode()
    print("Guess String: ", guess)
    # Hash the string
    # IMPORTANT: This is NOT the same hash as will be stored in the previous_hash. It's a not a block's hash. It's only used for the proof-of-work algorithm.
    guess_hash = hash_string_256(guess)
    print("Guess Hash: ", guess_hash)
    # Only a hash (which is based on the above inputs) which starts with two 0s is treated as valid
    # This condition is of course defined by us. It could also require 10 leading 0s - this would take significantly longer (and this allows you to control the speed at which new blocks can be added)
    return guess_hash[0:2] == "00"


def proof_of_work():
    """
        Proof of Work mechanism that ensure that transactions are securely validate
    """
    last_block = blockchain[-1]
    last_hash = hash_block(last_block)
    proof = 0
    while not valid_proof(open_transactions, last_hash, proof):
        proof += 1
    return proof


def mine_block():
    """
        Mines a new block (and its transactions) and add it to the Blockchain
    """
    last_block = blockchain[-1]
    hashed_block = hash_block(last_block)
    print("Hask Block: ", hashed_block)
    proof = proof_of_work()
    # tx_reward = {
    #     'sender': "Miner",
    #     'recipient': owner,
    #     'amount': MINING_REWARD
    # }
    tx_reward = OrderedDict(
        [('sender', 'Miner'), ('recipient', owner), ('amount', MINING_REWARD)])
    # Copy transactions instead of manipulating the original open_transactions
    # This ensure that if the mining fail for some reason, we don't have errors
    copied_transactions = open_transactions[:]
    copied_transactions.append(tx_reward)
    block = {
        'previous_hash': hashed_block,
        'index': len(blockchain),
        'transactions': copied_transactions,
        'proof': proof
    }
    blockchain.append(block)
    return True


def verify_transactions():
    """Verifies all open transactions."""
    return all([verify_transaction(tx) for tx in open_transactions])


def verify_chain():
    """ Verify the current blockchain and return True if it's valid, False otherwise."""
    for (index, block) in enumerate(blockchain):
        if index == 0:
            continue
        if block['previous_hash'] != hash_block(blockchain[index - 1]):
            return False
        if not valid_proof(block['transactions'][:-1], block['previous_hash'], block['proof']):
            print('Proof of work is invalid!')
            return False
    return True


waiting_for_input = True
# A while loop for the user input interface
# It's a loop that exits once waiting_for_input becomes False after or when break is called
while waiting_for_input:
    print("Please, make a choice: ")
    print("1: Add a new transaction value to the Blockchain")
    print("2: Mined a Block")
    print("3: Output the Blockchain blocks")
    print("4: List/Manage participants")
    print("5: Check transactions validity")
    print("h: Manipulate the Blockchain")
    print("q: Quit the program")

    user_choice = get_user_choice()
    if user_choice == '1':
        tx_data = get_transaction_value()
        tx_recipient, tx_amount = tx_data
        # Add the transaction amount to the blockchain
        if add_transaction(tx_recipient, amount=tx_amount):
            print("Transaction succeed!")
        else:
            print("Transaction Failed!")
    elif user_choice == '2':
        if mine_block():
            open_transactions = []
            save_data()
    elif user_choice == '3':
        print_blockchain_elements()
    elif user_choice == '4':
        print("Parpicipants: ", participants)
    elif user_choice == '5':
        if verify_transactions():
            print("All transactions are valid")
        else:
            print("There are some invalid transactions.")
    elif user_choice == 'h':
        if len(blockchain) >= 1:
            blockchain[0] = {
                'previous_hash': '',
                'index': 2,
                'transaction': {'recipient': 'Mamadou', 'sender': 'Baye', 'amount': 2.00}
            }
    elif user_choice == 'q':
        # This will lead to the loop to exist because it's running condition becomes False
        waiting_for_input = False
    else:
        print("Input was invalid. Please, pick a value in the list.")
    if not verify_chain():
        print_blockchain_elements()
        print("Invalid Blockchain!")
        # Break out of the loop
        break
    print("Balance of {}: {:6.2f}".format(owner, get_balance(owner)))
else:
    print("User Left")

print("Done!")
