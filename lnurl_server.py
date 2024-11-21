from flask import Flask, jsonify, request
import requests
from pyln.client import LightningRpc
import os

app = Flask(__name__)

# Core Lightning node configuration
#NODE_URL = "http://localhost:9735"  # URL for the Core Lightning HTTP server
#RUNE_HEADER = "lGztxGDKHtGXn5NIcrkk_WzklS31YGeCmzuXPo0BMMo9MQ=="  # Replace with your actual Rune token

def get_client():
    node  = LightningRpc("/home/aespieux/.lightning/regtest/lightning-rpc")

    return node

def get_node_connect_info():
    node = get_client()

    node_info = node.getinfo()

    first_address = node_info['address'][0]

    res = f"{node_info['id']}@{first_address['address']}:{first_address['port']}"

    return res

def get_random_id():
    rand = os.urandom(12).hex()

    return rand

def get_callback(tag):
    if tag == "channelRequest":
        return "lnurl-channel-request"

def generate_invoice(amount):
    """Generate a real invoice from the Core Lightning node."""
    node = get_client()

    invoice = node.invoice(100, "test", "test")

    print(invoice)

@app.route("/lnurl-channel-request", methods=["GET"])
def answerChannelRequest(node_id, amount):
    client = get_client()

    client.fundchannel()

@app.route("/lnurl2", methods=["GET"])
def lnurl_channel():
    """LNURL-channel endpoint to open channel to client."""
    """{
        "uri": string, // Remote node address of form node_key@ip_address:port_number
        "callback": string, // a second-level URL which would initiate an OpenChannel message from target LN node
        "k1": string, // random or non-random string to identify the user's LN WALLET when using the callback URL
        "tag": "channelRequest" // type of LNURL
    }"""

    tag = "channelRequest"
    node_info = get_node_connect_info()
    k1 = get_random_id()
    callback = get_callback(tag)
    
    if node_info:
        return jsonify({
            "status": "OK",
            "tag": tag,
            "uri": node_info,
            "k1": k1,
            "callback": callback,
        })
    else:
        return jsonify({"status": "ERROR", "reason": "Failed to generate invoice"}), 500

@app.route("/lnurl-pay", methods=["GET"])
def lnurl_pay():
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

@app.route("/lnurl-withdraw", methods=["GET"])
def lnurl_withdraw():
    """LNURL-withdraw endpoint for demo purposes."""
    amount = int(request.args.get("amount", 1000))  # Amount in millisatoshis
    # For LNURL-withdraw, users provide an invoice they’ve created to receive funds
    return jsonify({
        "status": "OK",
        "tag": "withdrawRequest",
        "callback": request.url,
        "maxWithdrawable": 100000,
        "defaultDescription": "Sample LNURL-withdraw",
        "amount": amount
    })

@app.route("/lnurl-auth", methods=["GET"])
def lnurl_auth():
    """Simulated LNURL-auth for basic authentication."""
    # In a real setup, LNURL-auth involves signing a challenge with LNURL keys
    user_id = "user-demo-id"
    return jsonify({
        "status": "OK",
        "tag": "auth",
        "user_id": user_id,
        "message": "Authenticated successfully."
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)  # Run locally on port 5000

