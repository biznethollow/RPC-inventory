from flask import Flask, jsonify, request
import mysql.connector

app = Flask(__name__)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="inventory"
)

@app.route("/api/tampil_barang", methods=["GET"])
def get_barang():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM barang")
    data = cursor.fetchall()
    cursor.close()
    return jsonify(data)

@app.route("/api/tampil_user", methods=["GET"])
def get_user():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user")
    data = cursor.fetchall()
    cursor.close()
    return jsonify(data)

@app.route("/api/tampil_diambil", methods=["GET"])
def get_diambil():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM diambil")
    data = cursor.fetchall()
    cursor.close()
    return jsonify(data)

@app.route("/api/tambah_barang", methods=["POST"])
def tambah_barang():
    data = request.get_json()
    nama = data["nama"]
    jumlah = data["jumlah"]
    cursor = db.cursor()
    sql = """
        INSERT INTO barang (nama_barang, jumlah)
        VALUES (%s, %s)
    """
    cursor.execute(sql, (nama, jumlah))
    db.commit()
    cursor.close()

@app.route("/api/hapus_barang", methods=["POST"])
def hapus_barang():
    data = request.get_json()
    id_barang = data["id_barang"]
    cursor = db.cursor()
    sql = """
        DELETE FROM barang 
        where id = %s 
    """
    cursor.execute(sql, (id_barang))
    db.commit()
    cursor.close()

@app.route("/api/tambah_user", methods=["POST"])
def tambah_user():
    data = request.get_json()
    nama = data["nama"]
    role = data["role"]
    cursor = db.cursor()
    sql = """
        INSERT INTO user (nama_user, role)
        VALUES (%s, %s)
    """
    cursor.execute(sql, (nama, role))
    db.commit()
    cursor.close()

@app.route("/api/hapus_user", methods=["POST"])
def hapus_user():
    data = request.get_json()
    id_user = data["id_user"]
    cursor = db.cursor()
    sql = """
        DELETE FROM user 
        where id = %s
    """
    cursor.execute(sql, (id_user))
    db.commit()
    cursor.close()

@app.route("/api/ambil_barang", methods=["POST"])
def ambil_barang():
    data = request.get_json()
    id_user = data["id_user"]
    id_barang = data["id_barang"]
    jumlah = data["jumlah"]
    cursor = db.cursor()
    sql = """
        CALL ambil_barang(%s, %s, %s)
    """
    cursor.execute(sql, (id_user, id_barang, jumlah))
    db.commit()
    cursor.close()

@app.route("/api/batal_ambil_barang", methods=["POST"])
def batal_ambil_barang():
    data = request.get_json()
    id_ambil = data["id_ambil"]
    cursor = db.cursor()
    sql = """
        CALL batalkan_pengambilan(%s)
    """
    cursor.execute(sql, (id_ambil))
    db.commit()
    cursor.close()

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000
    )
