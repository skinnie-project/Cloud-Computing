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

def register():
    data = request.get_json()
    username = data['username']
    email = data['email']
    nama = data['nama']
    password = data['password']

    # Koneksi MySQL
    conn = mysql.connect()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM login_normal WHERE username = %s", (username,))
        result = cursor.fetchone()

        if result:
            conn.close()
            response = {
                'status': 'error',
                'message': 'Username sudah terdaftar'
            }
            return jsonify(response)

        cursor.execute("INSERT INTO login_normal (username, email, nama, password) VALUES (%s, %s, %s, %s)", (username, email, nama, password))
        conn.commit()
        conn.close()

        response = {
            'status': 'success',
            'message': 'Akun berhasil dibuat'
        }

        return jsonify(response)
    except Exception as e:
        conn.rollback()
        conn.close()
        response = {
            'status': 'error',
            'message': 'Terjadi kesalahan saat membuat akun',
            'error': str(e)
        }
        return jsonify(response)
    
def login_google():
    data = request.get_json()
    fullname = data['name']
    nickname = data['nickname']
    email = data['email']

    # Koneksi MySQL
    conn = mysql.connect()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO login_google (fullname, nickname, email) VALUES (%s, %s, %s)", (fullname, nickname, email))
        conn.commit()
        conn.close()

        response = {
            'status': 'success',
            'message': 'Data akun berhasil ditambahkan'
        }

        return jsonify(response)
    except Exception as e:
        conn.rollback()
        conn.close()
        response = {
            'status': 'error',
            'message': 'Terjadi kesalahan saat menambahkan data akun',
            'error': str(e)
        }
        return jsonify(response)
