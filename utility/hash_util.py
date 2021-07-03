import hashlib as hl
from json import dumps


def hash_string_256(string):
    """Calculate and return the string representation of a hash
    Arguments:
        :string: The string to hash
    """
    return hl.sha256(string).hexdigest()


def hash_block(block):
    """Calculate and return the hash of a given block
    Arguments:
        :block: The block to hash
    """
    hashable_block = block.__dict__.copy()
    hashable_block["transactions"] = [
        tx.to_ordered_dict() for tx in hashable_block["transactions"]
    ]
    return hash_string_256(dumps(hashable_block, sort_keys=True).encode())
