import os
from google.cloud import storage
from flask import Flask, request, jsonify

#ini yang baru ka
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.efficientnet import preprocess_input
import base64
from PIL import Image
import numpy as np
import tensorflow as tf
from tensorflow.keras.regularizers import l2
from flaskext.mysql import MySQL
import io
import requests
from io import BytesIO


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

def load_my_model():
    global model
    model = load_model('model1.h5')
    model.load_weights('model1-weights.h5')

def predict_image(image_path):
    # model = load_model('model1.h5')
    # model.load_weights('model1-weights.h5')
    if model is None:
        load_my_model()
    img = image.load_img(image_path, target_size=(224, 224))
    img = image.img_to_array(img)
    img = np.expand_dims(img, axis=0)
    img = preprocess_input(img)
    pred = model.predict(img)
    classes = ['dry', 'normal', 'oily']
    predicted_class = {class_name: float(pred[0][i]) for i, class_name in enumerate(classes)}
    predicted = classes[np.argmax(pred)]
    return predicted_class, predicted

def upload_image_to_storage(image_base64, filename):
    
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)

    directory = "uploaded-photos"
    blob_path = f"{directory}/{filename}"
    file_blob = bucket.blob(blob_path)

    # Decode base64 image data
    image_data = base64.b64decode(image_base64)

    # Upload the image file to Google Cloud Storage
    file_blob.upload_from_string(image_data, content_type='image/jpeg')
    print(f"Image {filename} uploaded to Google Cloud Storage.")

    # filez_blob = bucket.blob(filename)
    # filez_blob.make_public()
    print(f"Image {filename} has been public.")

    image_url = f"https://storage.googleapis.com/{bucket_name}/uploaded-photos/{filename}"
    return image_url

#=============================================================================
#ini yang baru ka

@app.route('/predict', methods=['POST'])
def predict():
    file = request.files['image']
    file.save('uploaded_image.jpg')
    returned_predicted_class, returned_predicted = predict_image('uploaded_images.jpg')
    return jsonify({'prediction_rate': returned_predicted_class, 'predicted': returned_predicted})

@app.route('/predict/base64', methods=['POST'])
def predict_base64():
    # url = request.json['image_url']
    image_base64 = request.json['image']
    filename = request.json['filename']
    olahb64 = upload_image_to_storage(image_base64, filename)
    
    response = requests.get(olahb64)
    image = Image.open(BytesIO(response.content))
    # image = Image.open(BytesIO(olahb64))
    image.save('uploaded_images.jpg')
    # file = request.files['image']
    # file.save('uploaded_image.jpg')
    # predicted_class = predict_image('uploaded_images.jpg')
    returned_predicted_class, returned_predicted = predict_image('uploaded_images.jpg')
    return jsonify({'prediction_rate': returned_predicted_class, 'predicted': returned_predicted})

@app.route('/register', methods=['POST'])
def register():
    # Mendapatkan data dari permintaan POST
    data = request.get_json()
    username = data['username']
    email = data['email']
    nama = data['nama']
    password = data['password']

    # Membuat koneksi MySQL
    conn = mysql.connect()
    cursor = conn.cursor()

    try:
        # Mengecek apakah username sudah terdaftar
        cursor.execute("SELECT * FROM login_normal WHERE username = %s", (username,))
        result = cursor.fetchone()

        if result:
            conn.close()
            response = {
                'status': 'error',
                'message': 'Username sudah terdaftar'
            }
            return jsonify(response)

        # Memasukkan data ke dalam tabel
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

@app.route('/login', methods=['POST'])
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

@app.route('/data/random', methods=['GET'])
def get_random_data():
    # Mendapatkan data dari permintaan POST
    # data = request.get_json()
    # username = data['username']
    # password = data['password']

    # Membuat koneksi MySQL
    conn = mysql.connect()
    cursor = conn.cursor()

    query = 'SELECT * FROM list_skincare ORDER BY RAND() LIMIT 1'

    try:
        # Mengecek kecocokan username dan password di database
        cursor.execute(query)
        result = cursor.fetchall()

        return jsonify(result)

       
    except Exception as e:
        conn.close()
        response = {
            'status': 'error',
            'message': 'Terjadi kesalahan saat mengambil data',
            'error': str(e)
        }
        return jsonify(response)
    
@app.route('/register/google', methods=['POST'])
def register_google():
    # Mendapatkan data dari permintaan POST
    data = request.get_json()
    fullname = data['name']
    nickname = data['nickname']
    email = data['email']

    # Membuat koneksi MySQL
    conn = mysql.connect()
    cursor = conn.cursor()

    try:

        # Memasukkan data ke dalam tabel
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


if __name__ == '__main__':
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key.json"  # Set the service account credentials
    load_my_model()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
