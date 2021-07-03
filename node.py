import json
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from wallet import Wallet
from blockchain import Blockchain

app = Flask(__name__)
wallet = Wallet()
blockchain = Blockchain(wallet.public_key)
CORS(app)


@app.route('/', methods=['GET'])
def get_ui():
    return send_from_directory("ui", "node.html")


@app.route("/wallet", methods=['POST'])
def create_keys():
    wallet.create_keys()
    if wallet.save_keys():
        global blockchain
        blockchain = Blockchain(wallet.public_key)
        response = {
            "public_key": wallet.public_key,
            "private_key": wallet.private_key,
            "balance": blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            "message": "Wallet keys creation failed!"
        }
        return jsonify(response), 500


@app.route("/wallet", methods=['GET'])
def load_keys():
    wallet.load_keys()
    if wallet.load_keys():
        global blockchain
        blockchain = Blockchain(wallet.public_key)
        response = {
            "public_key": wallet.public_key,
            "private_key": wallet.private_key,
            "balance": blockchain.get_balance()
        }
        return jsonify(response), 200
    else:
        response = {
            "message": "Wallet keys loading failed!",
            "wallet_set_up": wallet.public_key != None
        }
        return jsonify(response), 500


@app.route("/balance", methods=["GET"])
def get_balance():
    balance = blockchain.get_balance()
    if balance != None:
        response = {
            "message": "Balance fetched successfully!",
            "balance": balance
        }
        return jsonify(response), 200
    else:
        response = {
            "message": "Balance loading failed.",
            "wallet_set_up": wallet.public_key != None
        }
        return jsonify(response), 500


@app.route("/transaction", methods=["POST"])
def add_transaction():
    if wallet.public_key == None:
        response = {
            "message": "No wallet set up."
        }
        return jsonify(response), 400
    else:
        data = request.get_json()
        if not data:
            response = {
                "message": "Required data are missing or mal formatted."
            }
            return jsonify(response), 400
        else:
            required_fields = ["recipient", "amount"]
            if all(field in data for field in required_fields):
                recipient = data['recipient']
                amount = data['amount']
                signature = wallet.sign_transaction(
                    wallet.public_key, recipient, amount)
                transaction = {
                    "sender": wallet.public_key,
                    "recipient": recipient,
                    "amount": amount
                }

                is_tx_succed = blockchain.add_transaction(
                    recipient, wallet.public_key, signature, amount)
                if is_tx_succed:
                    response = {
                        "message": "Transaction sent successfully!",
                        "transaction": transaction,
                        "balance": blockchain.get_balance()
                    }
                    return jsonify(response), 201
                else:
                    response = {
                        "message": "Adding transaction failed!",
                        "balance": blockchain.get_balance()
                    }
                    return jsonify(response), 400
            else:
                response = {
                    "message": "One or more fields are missing."
                }
            return jsonify(response), 400
        return jsonify(response), 500


@app.route("/transactions", methods=["GET"])
def get_open_transactions():
    open_txs = blockchain.get_open_transactions()
    open_txs_dict = [tx.__dict__ for tx in open_txs]
    return jsonify(open_txs_dict), 200


@app.route('/mine', methods=['POST'])
def mine():
    block = blockchain.mine_block()
    if block != None:
        block_snapshot = block.__dict__.copy()
        block_snapshot['transactions'] = [
            tx.__dict__ for tx in block_snapshot['transactions']]
        response = {
            'message': "Mine a new block successfully!",
            'block': block_snapshot,
            'balance': blockchain.get_balance()
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
