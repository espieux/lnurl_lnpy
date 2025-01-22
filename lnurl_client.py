import requests
from hashlib import sha256
from pyln.client import LightningRpc
import json

# BASE_URL = "http://127.0.0.1:5000"
BASE_URL = "http://192.168.0.239:5000"
LIGHTNING_RPC_PATH = "/home/aespieux/.lightning/regtest/lightning-rpc"

def get_client():
    """Get an instance of the LightningRpc client."""
    try:
        return LightningRpc(LIGHTNING_RPC_PATH)
    except Exception as e:
        print(f"Error connecting to LightningRpc: {e}")
        raise

def display_payment_dialog(lnurl_response, min_amount, max_amount):
    """Simulate a payment dialog with metadata and amount selection."""
    metadata = json.loads(lnurl_response["metadata"])
    text_plain_entry = next((entry[1] for entry in metadata if entry[0] == "text/plain"), None)

    domain = BASE_URL.split("//")[-1]
    print(f"Domain: {domain}")
    print(f"Description: {text_plain_entry}")
    print(f"Minimum amount: {min_amount} msat")
    print(f"Maximum amount: {max_amount} msat")

def verify_invoice(invoice, metadata, expected_amount_msat):
    """
    Verifies the Lightning invoice against metadata and amount.

    Args:
        invoice (str): BOLT 11 Lightning invoice.
        metadata (str): Metadata JSON string.
        expected_amount_msat (int): Amount specified by the user in millisatoshis.

    Returns:
        bool: True if the invoice is valid, False otherwise.
    """
    try:
        # Step 1: Decode the invoice
        client = get_client()
        metadata_hash=sha256(metadata.encode('utf-8')).hexdigest()
        decoded_invoice = client.decodepay(invoice)
        invoice_metadata=decoded_invoice['description']
        if metadata_hash!=invoice_metadata:
            print("Metadata hash mismatch!")
            return False
        invoice_amount=int(decoded_invoice['amount_msat'])
        if invoice_amount!=expected_amount_msat:
            print(f"Amount mismatch! Invoice: {invoice_amount}, Expected: {expected_amount_msat}")
            return False
        return True
    
    except Exception as e:
        print(f"Error verifying invoice: {e}")
        return False

def lnurl_channel():
    """Test LNURL-channel interaction."""
    url = f"{BASE_URL}/lnurl2"
    response = requests.get(url)
    # print("LNURL2 response:", response.json())
    if response.status_code == 200:
        lnurl_response = response.json()
        client = get_client()

        # Connect to the node
        uri = lnurl_response['uri']
        # print(f"Connecting to node {uri}...")
        connect_res = client.connect(uri)
        # print(f"Connection result: {connect_res}")

        # Call the callback to open the channel
        k1 = lnurl_response['k1']
        callback = lnurl_response['callback']
        amount = 1_000_000  # Example: 1,000,000 msatoshis
        node_id = client.getinfo()['id']
        private = 1  # Example: set to 1 for private channel

        url= f"{BASE_URL}/{callback}?amount={amount}&k1={k1}&remote_id={node_id}&private={private}"

        print("Calling channel request callback...")
        response = requests.get(url).json()
        print(f"Channel request response:\n{json.dumps(response, indent=4)}")
    else:
        print("Failed to connect to LNURL2 endpoint.")

def lnurl_pay(amount):
    """Simulate an LNURL-pay interaction."""
    url = f"{BASE_URL}/lnurl6"
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to connect to LNURL-pay endpoint.")
        return
    lnurl_response = response.json()
    # print(f"LNURL-pay response:\n{json.dumps(lnurl_response, indent=4)}")
    # Extract necessary data
    callback = lnurl_response.get("callback")
    max_sendable = lnurl_response.get("maxSendable")
    min_sendable = lnurl_response.get("minSendable")
    metadata = lnurl_response.get("metadata")
    tag = lnurl_response.get("tag")
    # print(f"Callback: {callback}\nMax sendable: {max_sendable}\nMin sendable: {min_sendable}\nMetadata: {metadata}\nTag: {tag}")
    if tag != "payRequest":
        print("Invalid LNURL tag.")
        return
    
    # Step 2: Determine bounds for the amount
    local_wallet_max = 50_000_000  # Example: local max sendable in millisatoshis (adjust based on your wallet)
    local_wallet_min = 1_000      # Example: local min sendable in millisatoshis
    
    max_amount = min(max_sendable, local_wallet_max)
    min_amount = max(min_sendable, local_wallet_min)
    
    if amount < min_amount or amount > max_amount:
        print(f"Amount {amount} is out of bounds. Must be between {min_amount} and {max_amount}.")
        return
    
    # Step 3: Display payment dialog
    display_payment_dialog(lnurl_response, min_amount, max_amount)

    # Step 4: Send amount to callback
    callback_url = f"{BASE_URL}/{callback}?amount={amount}"
    payment_response = requests.get(callback_url)
    if payment_response.status_code != 200:
        print("Failed to send payment request to callback URL.")
        return
    
    payment_data = payment_response.json()
    if payment_data.get("status") == "ERROR":
        print("Payment error:", payment_data.get("reason"))
        return
    
    pr = payment_data.get("pr")
    routes = payment_data.get("routes")

    # # Step 5: Verify h-tag in invoice matches metadata hash
    if not verify_invoice(pr, metadata, amount):
        print("Invoice verification failed.")
        return
    
    # # Step 6: Pay invoice
    try:
        client = get_client()
        client.pay(pr)
        print("Invoice paid successfully!")
    except Exception as e:
        print(f"Error paying invoice: {e}")

def lnurl_withdraw(amount):
    """Simulate an LNURL-withdraw interaction."""
    url = f"{BASE_URL}/lnurl-withdraw?amount={amount}"
    response = requests.get(url)
    if response.status_code == 200:
        print("LNURL-withdraw response:", response.json())
    else:
        print("Failed to connect to LNURL-withdraw endpoint.")

def lnurl_auth():
    """Simulate an LNURL-auth interaction."""
    url = f"{BASE_URL}/lnurl-auth"
    response = requests.get(url)
    if response.status_code == 200:
        print("LNURL-auth response:", response.json())
    else:
        print("Failed to connect to LNURL-auth endpoint.")

def lnurl_static(static):
    """Simulate an LNURL-static interaction."""
    res=static.split("@")
    username=res[0]
    host=res[1]
    url = f"{BASE_URL}/.well-known/lnurlp/{username}"
    response = requests.get(url)
    print("LNURL-static response:", response.json())
    if response.status_code == 200:
        print("LNURL-static response:", response)
    else:
        print("Failed to connect to LNURL-static endpoint.")

if __name__ == "__main__":
    # Test each function with sample values
    # lnurl_channel()  # Test LNURL-channel interaction
    # lnurl_pay(2500)  # Uncomment to test LNURL-pay
    # lnurl_withdraw(5000)  # Uncomment to test LNURL-withdraw
    # lnurl_auth()  # Uncomment to test LNURL-auth
    lnurl_static("sosthene@sosthene.wtf")  # Test LNURL-static interaction