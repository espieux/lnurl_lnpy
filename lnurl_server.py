from flask import Flask, jsonify, request
from pyln.client import LightningRpc
import logging
import os

app = Flask(__name__)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('app.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Core Lightning node configuration
LIGHTNING_RPC_PATH = "/home/aespieux/.lightning2/regtest/lightning-rpc"
BASE_URL = "http://127.0.0.1:5000"

def get_client():
    logger.info("Getting an instance of the LightningRpc client...")
    """Get an instance of the LightningRpc client."""
    try:
        return LightningRpc(LIGHTNING_RPC_PATH)
    except Exception as e:
        logger.error(f"Error connecting to LightningRpc: {e}")
        raise

def get_node_connect_info():
    logger.info("Getting the node's connection info...")
    """Get the node's connection info."""
    node = get_client()
    node_info = node.getinfo()
    first_address = node_info['address'][0]
    return f"{node_info['id']}@{first_address['address']}:{first_address['port']}"

def get_random_id():
    logger.info("Generating a random k1 identifier...")
    """Generate a random k1 identifier."""
    return os.urandom(12).hex()

def get_callback(tag):
    logger.info("Generating callback URLs...")
    """Generate callback URLs."""
    if tag == "channelRequest":
        return f"lnurl-channel-request"

def generate_invoice(amount):
    logger.info(f"Generating an invoice for {amount} millisatoshis...")
    """Generate a real invoice from the Core Lightning node."""
    node = get_client()
    try:
        invoice = node.invoice(amount, "test", "test")
        return invoice
    except Exception as e:
        logger.error(f"Error generating invoice: {e}")
        return None

@app.route("/lnurl-channel-request", methods=["GET"])
def answer_channel_request():
    logger.info("Handling channel requests...")
    """Handle channel requests."""
    k1 = request.args.get("k1")
    remote_id = request.args.get("remote_id")
    announce = False if request.args.get("private")==1 else True
    amount = int(request.args.get("amount"))
    try:
        client = get_client()
        res = client.fundchannel(node_id=remote_id, amount=amount, announce=announce) 
        return jsonify({"status": "OK", "result": res})
    except Exception as e:
        return jsonify({"status": "ERROR", "reason": str(e)}), 500

@app.route("/lnurl2", methods=["GET"])
def lnurl_channel():
    logger.info("Handling LNURL2 requests...")
    """LNURL-channel endpoint to open channel to client."""
    try:
        tag = "channelRequest"
        node_info = get_node_connect_info()
        logger.info(f"Node info: {node_info}")
        k1 = get_random_id()
        logger.info(f"Generated k1: {k1}")
        callback = get_callback(tag)
        logger.info(f"Callback URL: {callback}")
        return jsonify({
            "status": "OK",
            "tag": tag,
            "uri": node_info,
            "k1": k1,
            "callback": callback,
        })
    except Exception as e:
        logger.error(f"Error in lnurl2: {e}")
        return jsonify({"status": "ERROR", "reason": str(e)}), 500

@app.route("/lnurl-pay", methods=["GET"])
def lnurl_pay():
    logger.info("Handling LNURL-pay requests...")
    """LNURL-pay endpoint to generate invoices."""
    amount = int(request.args.get("amount", 1000))  # Amount in millisatoshis
    invoice = generate_invoice(amount)
    if invoice:
        return jsonify({
            "status": "OK",
            "tag": "payRequest",
            "callback": request.url,
            "minSendable": 1000,
            "maxSendable": 100000,
            "metadata": "Sample LNURL-pay metadata",
            "invoice": invoice["bolt11"]  # Get the BOLT11 invoice string
        })
    else:
        return jsonify({"status": "ERROR", "reason": "Failed to generate invoice"}), 500

if __name__ == "__main__":
    logger.info("Starting LNURL server...")
    app.run(host="0.0.0.0", port=5000)  # Run locally on port 5000
