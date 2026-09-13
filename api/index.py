from http.server import BaseHTTPRequestHandler
from xmlrpc.server import SimpleXMLRPCDispatcher
import xmlrpc.client


class Inventory:
    def __init__(self):
        self.items = {}

    def add_item(self, name, quantity):
        if not name:
            return {
                "success": False,
                "message": "Nama barang tidak boleh kosong"
            }

        if not isinstance(quantity, int) or quantity <= 0:
            return {
                "success": False,
                "message": "Quantity harus lebih dari 0"
            }

        self.items[name] = self.items.get(name, 0) + quantity

        return {
            "success": True,
            "message": f"Item '{name}' berhasil ditambahkan",
            "name": name,
            "quantity": self.items[name]
        }

    def get_items(self):
        return [
            {
                "name": name,
                "quantity": quantity
            }
            for name, quantity in self.items.items()
        ]

    def take_item(self, name, quantity):
        if name not in self.items:
            return {
                "success": False,
                "message": f"Item '{name}' tidak ditemukan"
            }

        if not isinstance(quantity, int) or quantity <= 0:
            return {
                "success": False,
                "message": "Quantity yang diambil harus lebih dari 0"
            }

        if quantity > self.items[name]:
            return {
                "success": False,
                "message": (
                    f"Stok '{name}' tidak mencukupi. "
                    f"Stok tersedia: {self.items[name]}"
                )
            }

        self.items[name] -= quantity

        if self.items[name] == 0:
            del self.items[name]

            return {
                "success": True,
                "message": (
                    f"Semua stok '{name}' berhasil diambil. "
                    "Barang dihapus dari inventory."
                ),
                "name": name,
                "taken": quantity,
                "remaining": 0
            }

        return {
            "success": True,
            "message": f"Berhasil mengambil {quantity} '{name}'",
            "name": name,
            "taken": quantity,
            "remaining": self.items[name]
        }

    def delete_item(self, name):
        if name not in self.items:
            return {
                "success": False,
                "message": f"Item '{name}' tidak ditemukan"
            }

        del self.items[name]

        return {
            "success": True,
            "message": f"Item '{name}' berhasil dihapus"
        }

    def clear_items(self):
        self.items.clear()

        return {
            "success": True,
            "message": "Semua barang berhasil dihapus"
        }


inventory = Inventory()

dispatcher = SimpleXMLRPCDispatcher(
    allow_none=True,
    encoding=None
)

dispatcher.register_instance(inventory)


class handler(BaseHTTPRequestHandler):

    def _send_response(self, status, content_type, body):
        if isinstance(body, str):
            body = body.encode("utf-8")

        self.send_response(status)

        self.send_header(
            "Content-Type",
            content_type
        )

        self.send_header(
            "Content-Length",
            str(len(body))
        )

        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )

        self.send_header(
            "Access-Control-Allow-Methods",
            "POST, GET, OPTIONS"
        )

        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type"
        )

        self.end_headers()

        self.wfile.write(body)

    def do_GET(self):

        body = b"""
        <html>
        <head>
            <title>XML-RPC Inventory Server</title>
        </head>

        <body>
            <h1>XML-RPC Inventory Server</h1>

            <p>Server aktif.</p>

            <p>
                Gunakan HTTP POST dengan request XML-RPC.
            </p>

            <ul>
                <li>add_item(name, quantity)</li>
                <li>get_items()</li>
                <li>take_item(name, quantity)</li>
                <li>delete_item(name)</li>
                <li>clear_items()</li>
            </ul>
        </body>
        </html>
        """

        self._send_response(
            200,
            "text/html; charset=utf-8",
            body
        )

    def do_OPTIONS(self):
        self._send_response(
            204,
            "text/plain",
            b""
        )

    def do_POST(self):

        try:
            content_length = int(
                self.headers.get(
                    "Content-Length",
                    "0"
                )
            )

            if content_length <= 0:
                self._send_response(
                    400,
                    "text/plain; charset=utf-8",
                    "Request XML-RPC kosong"
                )

                return

            request_body = self.rfile.read(
                content_length
            )

            response = dispatcher._marshaled_dispatch(
                request_body
            )

            self._send_response(
                200,
                "text/xml; charset=utf-8",
                response
            )

        except Exception as exc:

            fault = xmlrpc.client.dumps(
                xmlrpc.client.Fault(
                    1,
                    f"Server error: {exc}"
                ),
                methodresponse=True,
                encoding="utf-8"
            )

            self._send_response(
                500,
                "text/xml; charset=utf-8",
                fault
            )

    def log_message(self, format, *args):
        print(
            f"[XML-RPC] {self.command} "
            f"{self.path} - {format % args}"
        )