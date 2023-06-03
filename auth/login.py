from flask import Flask, request, jsonify
from flaskext.mysql import MySQL

app = Flask(__name__)

mysql = MySQL()
# Konfigurasi koneksi MySQL
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'skinnie-db-project'
app.config['MYSQL_DATABASE_DB'] = 'skinnie_database'
app.config['MYSQL_DATABASE_HOST'] = '34.128.86.191'

mysql.init_app(app)

def login():
    # Mendapatkan data dari permintaan POST
    data = request.get_json()
    username = data['username']
    password = data['password']

    # Membuat koneksi MySQL
    conn = mysql.connect()
    cursor = conn.cursor()

    try:
        # Mengecek kecocokan username dan password di database
        cursor.execute("SELECT * FROM login_normal WHERE username = %s AND password = %s", (username, password))
        result = cursor.fetchone()

        if result:
            # Jika data ditemukan, mengembalikan nama dan username
            nama = result[1]

            response = {
                'status': 'success',
                'message': 'Login berhasil',
                'username': username,
                'nama': nama
            }

            return jsonify(response)
        else:
            conn.close()
            response = {
                'status': 'error',
                'message': 'Username atau Password Salah'
            }
            return jsonify(response)
    except Exception as e:
        conn.close()
        response = {
            'status': 'error',
            'message': 'Terjadi kesalahan saat login',
            'error': str(e)
        }
        return jsonify(response)