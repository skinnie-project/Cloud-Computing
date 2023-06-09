from flask import Flask, request, jsonify
import numpy as np
from flaskext.mysql import MySQL
import pickle
import pandas as pd

bucket_name = "skinnie-bucket"

app = Flask(__name__)

mysql = MySQL()
# Konfigurasi koneksi MySQL
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'skinnie-db-project'
app.config['MYSQL_DATABASE_DB'] = 'skinnie_database'
app.config['MYSQL_DATABASE_HOST'] = '34.128.86.191'

mysql.init_app(app)

model = None

data = pd.read_csv('dataset/new_dataset.csv', sep=';') 
products = data.to_dict(orient='records')

descriptions = [product['product_name'] + ' ' + product['ingredients'] for product in products]
skin_types = [product['suitable_for'] for product in products]
ratings = [product['rate'] for product in products]

def content_recommendations(user_skin_type):
    with open('model/model.pkl', 'rb') as f:
        model = pickle.load(f)

    with open('model/vectorizer.pkl', 'rb') as f:
        vectorizer = pickle.load(f)

    user_input = vectorizer.transform([user_skin_type])
    model.predict(user_input)

    skin_types_series = pd.Series(skin_types)

    if user_skin_type == 'Normal':
        filtered_indices = np.where(skin_types_series.isin([user_skin_type, 'Semua jenis kulit']))[0]
    elif user_skin_type == 'Kering':
        filtered_indices = np.where(skin_types_series.isin([user_skin_type, 'Semua jenis kulit']))[0]
    elif user_skin_type == 'Berminyak':
        filtered_indices = np.where(skin_types_series.isin([user_skin_type, 'Semua jenis kulit']))[0]
    else:
        filtered_indices = []

    filtered_products = [products[i] for i in filtered_indices]

    # Convert filtered_products to a DataFrame
    df_filtered_products = pd.DataFrame(filtered_products)

    # Create a column to store the priority for sorting
    df_filtered_products['priority'] = df_filtered_products['suitable_for'].apply(lambda x: 0 if x == user_skin_type else 1)

    # Sort the DataFrame by 'priority', 'suitable_for', and 'rate' columns
    sorted_products = df_filtered_products.sort_values(by=['priority', 'suitable_for', 'rate'], ascending=[True, False, False])
    
    recommendations = []

    for _, row in sorted_products.iterrows():
        recommendation = {
            'product_name': row['product_name'],
            'suitable_for': row['suitable_for'],
            'ingredients': row['ingredients'],
            'rate': row['rate'],
            'brand': row['brand'],
            'url_new': row['url_new'],
            'id': row['id'],
            'subcategory': row['subcategory'],
            'recom': row['recom'],
            'reviewed': row['reviewed'],
            'price': row['price'],
            'description': row['description'],
            'how_to_use': row['how_to_use']
            
        }
        recommendations.append(recommendation)
        
        if len(recommendations) == 50:
            break

    return recommendations


def get_predict_result():
    key_ingredients = request.args.get('ingredients')
    predicted_result = request.args.get('predicted')
    filter_by = request.args.get('filter_by')
    subcategory = request.args.get('subcategory')

    # Membuat koneksi MySQL
    conn = mysql.connect()
    cursor = conn.cursor()
    
    if key_ingredients == "Semua ingredients" and subcategory == "Semua subcategory":
        query = "SELECT * FROM list_skincare WHERE (suitable_for LIKE '%" + predicted_result + "%' OR suitable_for = 'Semua jenis kulit')"
    elif key_ingredients == "Semua ingredients":
        query = "SELECT * FROM list_skincare WHERE (suitable_for LIKE '%" + predicted_result + "%' OR suitable_for = 'Semua jenis kulit') AND subcategory = '" + subcategory + "'"
    elif subcategory == "Semua subcategory":
        query = "SELECT * FROM list_skincare WHERE (suitable_for LIKE '%" + predicted_result + "%' OR suitable_for = 'Semua jenis kulit') AND ingredients LIKE '%" + key_ingredients + "%'"
    else:
        query = "SELECT * FROM list_skincare WHERE (suitable_for LIKE '%" + predicted_result + "%' OR suitable_for = 'Semua jenis kulit') AND ingredients LIKE '%" + key_ingredients + "%' AND subcategory = '" + subcategory + "'"
    
    filter_by = request.args.get('filter_by')
    if filter_by == "Review Terbanyak":
        query += " ORDER BY reviewed DESC LIMIT 100"
    elif filter_by == "Harga Tertinggi ":
        query += " ORDER BY price DESC LIMIT 100"
    elif filter_by == "Harga Terendah":
        query += " ORDER BY price ASC LIMIT 100"
    elif filter_by == "Rating Tertinggi":
        query += " ORDER BY rate DESC LIMIT 100"
    else:
        query += " ORDER BY brand ASC"
        
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
    

def get_product_rekomen():
    skin_type = request.args.get('predicted')
    recommendations = content_recommendations(skin_type)
    
    return jsonify(recommendations)
