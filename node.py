from uuid import uuid4

from verication import Verification
from blockchain import Blockchain


class Node:
    def __init__(self):
        """
            class constructor
            Arguments:
            :self: Automatically passed by Python
        """
        # self.id = str(uuid4())
        self.id = "Mountakha"
        self.blockchain = Blockchain(self.id)

    def print_blockchain_elements(self):
        """ Prints each block of the Blockchain """
        counter = 0
        print("\n-----Outputting blocks-----: \n")
        for block in self.blockchain.chain():
            if counter > 0:
                print("Block #{}: {}".format(counter, block))
            print("Block genesis: {}".format(block))
            counter += 1
        else:
            print("\n------End of outputting-----\n")

    def get_user_choice(self):
        """ Return the user's choice """
        user_choice = input("Your choice: ")
        return user_choice

    def get_transaction_value(self):
        """ Return the user data needed to make a valid transaction"""
        try:
            tx_recipient = input("Please, enter the recipient to send coins: ")
            if len(tx_recipient) < 2:
                tx_recipient = input(
                    "Please, enter a valid recipient name to send the coins: ")
            else:
                pass
            tx_amount = float(
                input("Please, enter the amount of coins to sends: "))
            if tx_amount <= 0:
                tx_amount = float(input(
                    "The amount to send must be greater than 0.\n Please, enter a valid amount of coins to send: "))
            else:
                pass
            return (tx_recipient, tx_amount)
        except ValueError:
            print("/!\: Please, enter a correct value !!!")
            tx_recipient = input("Please, enter the recipient to send coins: ")
            tx_amount = float(
                input("Please, enter the amount of coins to sends: "))
            return (tx_recipient, tx_amount)

    def listent_to_user_input(self):
        waiting_for_input = True
        # A while loop for the user input interface
        # It's a loop that exits once waiting_for_input becomes False after or when break is called
        while waiting_for_input:
            print("Please, make a choice: ")
            print("1: Add a new transaction value to the Blockchain")
            print("2: Mined a Block")
            print("3: Output the Blockchain blocks")
            print("4: Check transactions validity")
            print("q: Quit the program")
            user_choice = self.get_user_choice()
            if user_choice == '1':
                tx_data = self.get_transaction_value()
                tx_recipient, tx_amount = tx_data
                # Add the transaction amount to the blockchain
                if self.blockchain.add_transaction(tx_recipient, self.id, amount=tx_amount):
                    print("Transaction succeed!")
                else:
                    print("Transaction Failed!")
            elif user_choice == '2':
                self.blockchain.mine_block()
            elif user_choice == '3':
                # print_blockchain_elements()
                pass
            elif user_choice == '4':
                if Verification.verify_transactions(self.blockchain.get_open_transactions(), self.blockchain.get_balance):
                    print("All transactions are valid")
                else:
                    print("There are some invalid transactions.")
            elif user_choice == 'q':
                # This will lead to the loop to exist because it's running condition becomes False
                waiting_for_input = False
            else:
                print("Input was invalid. Please, pick a value in the list.")
            if not Verification.verify_chain(self.blockchain.chain):
                print_blockchain_elements(self.blockchain.chain)
                print("Invalid Blockchain!")
                # Break out of the loop
                break
            print("Balance of {}: {:6.2f}".format(
                self.id, self.blockchain.get_balance()))
        else:
            print("User Left")

        print("Done!")


node = Node()
node.listent_to_user_input()
