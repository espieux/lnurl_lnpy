import requests
from pyln.client import LightningRpc

BASE_URL = "http://127.0.0.1:5000"  # URL for the LNURL server

def get_client():
    node = LightningRpc("/home/aespieux/.lightning/regtest/lightning-rpc")

    return node

def lnurl_channel():
    url = f"{BASE_URL}/lnurl2"
    response = requests.get(url)
    if response.status_code == 200:
        client = get_client()
        # connect
        res = client.connect(response.json()['uri'])
        print(res)
        res = client.getinfo()
        node_id = res['id']
        k1 = response.json()['k1']
        private = 1
        callback = response.json()['callback']
        url = f"{BASE_URL}/{callback}?k1={k1}&remote_id={node_id}&private={private}"
        response = requests.get(url)
        print(response)
    else:
        print("Failed to connect to LNURL-pay endpoint.")

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
    lnurl_channel()
   # lnurl_pay(1000)      # Pay 1000 msats
   # lnurl_withdraw(5000)  # Withdraw 5000 msats
   # lnurl_auth()          # Authenticate

