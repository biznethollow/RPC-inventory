import xmlrpc.client

rpc = xmlrpc.client.ServerProxy(
    "http://127.0.0.1:8000"
)

data = rpc.tampil_user()

print(data)