from collections import OrderedDict

from printable import Printable

class Transaction(Printable):
    def __init__(self, sender, recipient, amount):
        """
            class constructor
            Arguments:
            :self: Automatically passed by Python
            :sender: The transaction's sender
            :recipient: The transaction's recipient
            :amount: The transaction's amount
        """
        self.sender = sender
        self.recipient = recipient
        self.amount = amount

    def to_ordered_dict(self):
        """ Converts a list of tuples onto an oredered dict. """
        return OrderedDict([('sender', self.sender), ('recipient', self.recipient), ('amount', self.amount)])
