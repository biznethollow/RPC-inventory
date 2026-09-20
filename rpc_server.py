from xmlrpc.server import SimpleXMLRPCServer
import requests

API_URL = "http://127.0.0.1:5000"

def api_get(endpoint):
    try:
        response = requests.get(
            API_URL + endpoint
        )
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "message": str(e)
        }

def api_post(endpoint, data):
    try:
        response = requests.post(
            API_URL + endpoint,
            json=data
        )
        response.raise_for_status()

        if response.content:
            return response.json()
        
        return {
            "success": True,
            "message": "Operasi berhasil"
        }

    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "message": str(e)
        }

class InventoryRPC:
    def tampil_barang(self):
        return api_get("/api/tampil_barang")

    def tambah_barang(self, nama, jumlah):
        data = {
            "nama": nama,
            "jumlah": jumlah
        }

        return api_post(
            "/api/tambah_barang",
            data
        )


    def hapus_barang(self, id_barang):
        data = {
            "id_barang": id_barang
        }

        return api_post(
            "/api/hapus_barang",
            data
        )

    def tampil_user(self):
        return api_get("/api/tampil_user")

    def tambah_user(self, nama, role):
        data = {
            "nama": nama,
            "role": role
        }

        return api_post(
            "/api/tambah_user",
            data
        )

    def hapus_user(self, id_user):
        data = {
            "id_user": id_user
        }

        return api_post(
            "/api/hapus_user",
            data
        )

    def tampil_diambil(self):
        return api_get("/api/tampil_diambil")

    def ambil_barang(self, id_user, id_barang, jumlah):
        data = {
            "id_user": id_user,
            "id_barang": id_barang,
            "jumlah": jumlah
        }

        return api_post(
            "/api/ambil_barang",
            data
        )

    def batal_ambil_barang(self, id_ambil):
        data = {
            "id_ambil": id_ambil
        }

        return api_post(
            "/api/batal_ambil_barang",
            data
        )

server = SimpleXMLRPCServer(
    ("127.0.0.1", 8000),
    allow_none=True
)

server.register_instance(InventoryRPC())
# BUAT DEBUG 
print("RPC Server berjalan...")
print("RPC URL: http://127.0.0.1:8000")
server.serve_forever()