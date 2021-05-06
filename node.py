from flask import Flask, jsonify
from flask_cors import CORS

from wallet import Wallet
from blockchain import Blockchain

app = Flask(__name__)
wallet = Wallet()
blockchain = Blockchain(wallet.public_key)
CORS(app)


@app.route('/', methods=['GET'])
def get_ui():
    return 'It works!'


@app.route('/mine', methods=['POST'])
def mine():
    block = blockchain.mine_block()
    if block != None:
        block_snapshot = block.__dict__.copy()
        block_snapshot['transactions'] = [
            tx.__dict__ for tx in block_snapshot['transactions']]
        response = {
            'message': "Mining a new block failed!",
            'block': block_snapshot
        }
        return jsonify(response), 201
    else:
        response = {
            'message': "Mining a new block failed!",
            'wallet_set_up': block != None
        }
        return jsonify(response), 500


@app.route('/chain', methods=['GET'])
def get_chain():
    chain_snapshot = [block.__dict__.copy() for block in blockchain.chain]
    for block in chain_snapshot:
        block['transactions'] = [tx.__dict__ for tx in block['transactions']]
    return (jsonify(chain_snapshot), 200)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
