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

def forgot():
    data = request.get_json()
    username = data['username']
    new_password = data['new_password']

    # Membuat koneksi MySQL
    conn = mysql.connect()
    cursor = conn.cursor()

    try:
        # Mengecek apakah username sudah terdaftar
        cursor.execute("SELECT * FROM login_normal WHERE username = %s", (username,))
        result = cursor.fetchone()

        if not result:
            conn.close()
            response = {
                'status': 'error',
                'message': 'Username tidak terdaftar'
            }
            return jsonify(response)

        else:
            query = "UPDATE login_normal SET `password` = '" + new_password + "' WHERE `username` = '" + username + "'"
            cursor.execute(query)
            conn.commit()
            conn.close()

            response = {
                'status': 'success',
                'message': 'Berhasil ganti password'
            }

            return jsonify(response)
    except Exception as e:
        conn.rollback()
        conn.close()
        response = {
            'status': 'error',
            'message': 'Terjadi kesalahan',
            'error': str(e)
        }
        return jsonify(response)