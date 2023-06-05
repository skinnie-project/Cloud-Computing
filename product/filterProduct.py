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

def filterProducts():
    conn = mysql.connect()
    cursor = conn.cursor()
    
    predicted = request.args.get('predicted')
    
    query = "SELECT * FROM list_skincare where suitable_for LIKE '%" + predicted + "%'"
    filter_by = request.args.get('filter_by')
    if filter_by == "most_reviewed":
        query += " ORDER BY reviewed DESC"
    elif filter_by == "harga_tertinggi":
        query += " ORDER BY price DESC"
    elif filter_by == "harga_terendah":
        query += " ORDER BY price ASC"
    elif filter_by == "rating_tertinggi":
        query += " ORDER BY rate DESC"
    else:
        query += " ORDER BY brand ASC"
        
    cursor.execute(query)
    
    try:
        # Mendapatkan hasil query
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
    

def filterSubcategoryRekomen():
    conn = mysql.connect()
    cursor = conn.cursor()
    
    predicted = request.args.get('predicted')
    subcategory = request.args.get('subcategory')
    
    query = "SELECT * FROM list_skincare where suitable_for LIKE '%" + predicted + "%' and subcategory = '" + subcategory + "' ORDER BY reviewed DESC"
    cursor.execute(query)
    
    try:
        # Mendapatkan hasil query
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