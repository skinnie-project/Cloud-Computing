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

def get_popular():
    conn = mysql.connect()
    cursor = conn.cursor()

    query = 'SELECT * FROM list_skincare ORDER BY reviewed DESC LIMIT 30'
    cursor.execute(query)

    try:
        rows = cursor.fetchall()
        results = []
        for row in rows:
            result = {
                'id': row[0],
                'product_name': row[1],
                'brand': row[2],
                'subcategory': row[3],
                'rate': row[4],
                'reviewed': row[5],
                'recom': row[6],
                'price': row[7],
                'description': row[8],
                'how_to_use': row[9],
                'ingredients': row[10],
                'suitable_for': row[11],
                'url_new': row[12]
            }
            results.append(result)

        return jsonify(results)
    
    except Exception as e:
        conn.close()
        response = {
            'status': 'error',
            'message': 'Terjadi kesalahan saat mengambil data',
            'error': str(e)
        }
        return jsonify(response)


def get_product_detail():
    product_id = request.args.get('id')

    # Koneksi MySQL
    conn = mysql.connect()
    cursor = conn.cursor()

    query = "SELECT * FROM list_skincare WHERE id = '" + product_id + "'"
    cursor.execute(query)
    
    try:
        rows = cursor.fetchall()
        results = []
        for row in rows:
            result = {
                'id': row[0],
                'product_name': row[1],
                'brand': row[2],
                'subcategory': row[3],
                'rate': row[4],
                'reviewed': row[5],
                'recom': row[6],
                'price': row[7],
                'description': row[8],
                'how_to_use': row[9],
                'ingredients': row[10],
                'suitable_for': row[11],
                'url_new': row[12]
            }
            results.append(result)

        return jsonify(results)

    except Exception as e:
        conn.close()
        response = {
            'status': 'error',
            'message': 'Terjadi kesalahan saat mengambil data',
            'error': str(e)
        }
        return jsonify(response)
    
    
def search_product():
    brand = request.args.get('product')

    # Koneksi MySQL
    conn = mysql.connect()
    cursor = conn.cursor()

    query = "SELECT * FROM list_skincare WHERE brand LIKE '%" + brand + "%'"
    cursor.execute(query)
    
    try:
        rows = cursor.fetchall()
        results = []
        for row in rows:
            result = {
                'id': row[0],
                'product_name': row[1],
                'brand': row[2],
                'subcategory': row[3],
                'rate': row[4],
                'reviewed': row[5],
                'recom': row[6],
                'price': row[7],
                'description': row[8],
                'how_to_use': row[9],
                'ingredients': row[10],
                'suitable_for': row[11],
                'url_new': row[12]
            }
            results.append(result)

        return jsonify(results)

    except Exception as e:
        conn.close()
        response = {
            'status': 'error',
            'message': 'Terjadi kesalahan saat mengambil data',
            'error': str(e)
        }
        return jsonify(response)