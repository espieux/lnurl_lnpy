import requests
from pyln.client import LightningRpc

BASE_URL = "http://127.0.0.1:5000"
LIGHTNING_RPC_PATH = "/home/aespieux/.lightning/regtest/lightning-rpc"

def get_client():
    """Get an instance of the LightningRpc client."""
    try:
        return LightningRpc(LIGHTNING_RPC_PATH)
    except Exception as e:
        print(f"Error connecting to LightningRpc: {e}")
        raise

def lnurl_channel():
    """Test LNURL-channel interaction."""
    url = f"{BASE_URL}/lnurl2"
    response = requests.get(url)
    if response.status_code == 200:
        lnurl_response = response.json()
        client = get_client()

        # Connect to the node
        uri = lnurl_response['uri']
        print(f"Connecting to node {uri}...")
        connect_res = client.connect(uri)
        print(f"Connection result: {connect_res}")

        # Call the callback to open the channel
        k1 = lnurl_response['k1']
        callback = lnurl_response['callback']
        node_id = client.getinfo()['id']
        private = 1  # Example: set to 1 for private channel

        print("Calling channel request callback...")
        response = requests.get(callback, params={"k1": k1, "remote_id": node_id, "private": private})
        print(f"Channel request response: {response.json()}")
    else:
        print("Failed to connect to LNURL2 endpoint.")

def lnurl_pay(amount):
    """Simulate an LNURL-pay interaction."""
    url = f"{BASE_URL}/lnurl-pay?amount={amount}"
    response = requests.get(url)
    if response.status_code == 200:
        print("LNURL-pay response:", response.json())
    else:
        print("Failed to connect to LNURL-pay endpoint.")

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

if __name__ == "__main__":
    # Test each function with sample values
    lnurl_channel()  # Test LNURL-channel interaction
    # lnurl_pay(1000)  # Uncomment to test LNURL-pay
    # lnurl_withdraw(5000)  # Uncomment to test LNURL-withdraw
    # lnurl_auth()  # Uncomment to test LNURL-auth
