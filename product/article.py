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

def get_article():
    article_id = request.args.get('id')

    # Membuat koneksi MySQL
    conn = mysql.connect()
    cursor = conn.cursor()

    if article_id is None:
        query = "SELECT * FROM artikel"
    else:
        query = "SELECT * FROM artikel WHERE id = '" + article_id + "'"
    
    try:
        # Mendapatkan hasil query
        cursor.execute(query)
        rows = cursor.fetchall()
        results = []
        for row in rows:
            result = {
                'id': row[0],
                'ditinjau': row[1],
                'tanggal': row[2],
                'judul': row[3],
                'sumber': row[4]
            }
            results.append(result)

        # Mengembalikan hasil dalam format JSON
        return jsonify(results)

    except Exception as e:
        conn.close()
        response = {
            'status': 'error',
            'message': 'Terjadi kesalahan saat mengambil data',
            'error': str(e)
        }
        return jsonify(response)