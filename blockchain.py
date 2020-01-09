# The reward to send to a miner for each complete new mining block
MINING_REWARD = 5.0

# Create the genesis Block of the Blockchain
genesis_block = {
    'previous_hash': "",
    'index': 0,
    'transactions': []
}

# Declaring and Initializing the blockchain list
blockchain = [genesis_block]
open_transactions = []
owner = "Morisson"
participants = {owner}


def get_last_blockchain_value():
    """ Return the last blockchain value """
    if len(blockchain) < 1:
        return None
    return blockchain[-1]


def get_balance(participant):
    """ Return the balance of a participant passed in parameter """
    amount_sent = 0.0
    amount_received = 0.0
    tx_sender = [[tx['amount'] for tx in block['transactions']
                  if tx['sender'] == participant] for block in blockchain]
    tx_open_sender = [tx['amount']
                      for tx in open_transactions if tx['sender'] == participant]
    tx_sender.append(tx_open_sender)
    for tx in tx_sender:
        if len(tx) > 0:
            amount_sent += tx[0]

    tx_recipient = [[tx['amount'] for tx in block['transactions']
                     if tx['recipient'] == participant] for block in blockchain]
    for tx in tx_recipient:
        if len(tx) > 0:
            amount_received += tx[0]

    return amount_received - amount_sent


def verify_transaction(transaction):
    """ Check if the sender has enough amount to sent to a recipient
        Arguments:
            :transaction: The transaction to check
    """
    sender_balance = get_balance(transaction['sender'])
    return sender_balance >= transaction['amount']


def verify_transactions():
    return all([verify_transaction(tx) for tx in open_transactions])


def add_transaction(recipient, sender=owner, amount=1.0):
    """ Add each new transaction amount in the blockchain

        Arguments:
            :sender: The sender of the transaction
            :recipient: The recipient of the transaction
            :amount: The amount of coins to send. default(amount=1.0)
    """

    transaction = {
        'sender': sender,
        'recipient': recipient,
        'amount': amount
    }
    # Check first if the transcation is valid
    if verify_transaction(transaction):
        open_transactions.append(transaction)
        participants.add(recipient)
        participants.add(sender)
        return True

    return False


def get_transaction_value():
    """ Return the user data needed to make a valid transaction"""
    tx_recipient = input("Please, enter the recipient to send coins: ")
    tx_amount = float(input("Please, enter the amount of coins to sends: "))
    return (tx_recipient, tx_amount)


def get_user_choice():
    """ Return the user's choice """
    user_choice = input("Your choice: ")
    return user_choice.lower()


def print_blockchain_elements():
    """ Prints each block of the Blockchain """
    for block in blockchain:
        print("Outputting blocks: ")
        print(block)
    else:
        print("-" * 20)


def hash_block(block):
    """ Return the hash of Block
        Arguments:
            :block: The Block to hash
    """
    return '-'.join([str(block[key]) for key in block])


def mine_block():
    """ Mined a new block (and its transactions) and add it to the Blockchain """
    last_block = blockchain[-1]
    hashed_block = hash_block(last_block)
    tx_reward = {
        'sender': "Miner",
        'recipient': owner,
        'amount': MINING_REWARD
    }
    open_transactions.append(tx_reward)
    block = {
        'previous_hash': hashed_block,
        'index': len(blockchain),
        'transactions': open_transactions
    }
    blockchain.append(block)
    return True


def verify_chain():
    """ Validate each node of the Blockchain """
    for (index, block) in enumerate(blockchain):
        if index == 0:
            continue
        if block['previous_hash'] != hash_block(blockchain[index - 1]):
            return False
    return True


# Get first user input and add it to the Blockchain
#tx_amount = get_transaction_value()
# add_transaction(tx_amount)

waiting_for_input = True
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
        if add_transaction(tx_recipient, amount=tx_amount):
            print("Transaction succeed!")
        else:
            print("'Transaction Failed!")
    elif user_choice == '2':
        if mine_block():
            open_transactions = []
    elif user_choice == '3':
        print_blockchain_elements()
    elif user_choice == '4':
        print(participants)
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
        waiting_for_input = False
    else:
        print("Input was invalid. Please, pick a value in the list.")
    if not verify_chain():
        print_blockchain_elements()
        print("Invalid Blockchain!")
        break
    print(get_balance(owner))
else:
    print("Done!")
