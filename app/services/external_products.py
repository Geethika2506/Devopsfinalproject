import requests

FAKESTORE_API = "https://fakestoreapi.com/products"

def fetch_external_products():
    r = requests.get(FAKESTORE_API)
    r.raise_for_status()
    return r.json()
