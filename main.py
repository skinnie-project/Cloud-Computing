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
from tensorflow.keras import regularizers
from flaskext.mysql import MySQL
import io


img_size = (224, 224)
channels = 3
img_shape = (img_size[0], img_size[1], channels)

base_model = tf.keras.applications.efficientnet.EfficientNetB3(include_top= False, weights= "imagenet", input_shape= img_shape, pooling= 'max')

def make_model():
    model = tf.keras.models.Sequential([
        base_model,
        tf.keras.layers.BatchNormalization(axis= -1, momentum= 0.99, epsilon= 0.001),
        tf.keras.layers.Dense(256, kernel_regularizer= regularizers.l2(l= 0.016), activity_regularizer= regularizers.l1(0.006),
                bias_regularizer= regularizers.l1(0.006), activation= 'relu'),
        tf.keras.layers.Dropout(rate= 0.45, seed= 123),
        tf.keras.layers.Dense(3, activation= 'softmax')
    ])
    return model

bucket_name = "skinnie-bucket"

# model = None

app = Flask(__name__)

mysql = MySQL()

# Konfigurasi koneksi MySQL
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'skinnie-db-project'
app.config['MYSQL_DATABASE_DB'] = 'skinnie_database'
app.config['MYSQL_DATABASE_HOST'] = '34.128.86.191'

mysql.init_app(app)

def download_model():
    model_file = "models/efficientnetb3_98.h5"  # Replace with your model file name
    weights_file = "models/efficientnetb3_98_weights.h5"  # Replace with your weights file name
    
    destination_path = "/tmp/efficientnetb3_98.h5"  # Path to store the downloaded model file
    weights_path = "/tmp/efficientnetb3_98_weights.h5"  # Path to store the downloaded weights file

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    model_blob = bucket.blob(model_file)
    weights_blob = bucket.blob(weights_file)
    model_blob.download_to_filename(destination_path)
    weights_blob.download_to_filename(weights_path)

def load_model():
    global model
    global weights_file_path
    if not os.path.isfile("/tmp/efficientnetb3_98.h5") or not os.path.isfile("/tmp/efficientnetb3_98_weights.h5"):
        download_model()
    model = make_model()  # Buat model terlebih dahulu
    model.load_weights("/tmp/efficientnetb3_98_weights.h5")

def predict_image(image_path):
    load_model()
    img = image.load_img(image_path, target_size=(224, 224))
    img = image.img_to_array(img)
    img = np.expand_dims(img, axis=0)
    img = preprocess_input(img)
    pred = model.predict(img)
    classes = ['dry', 'normal', 'oily']
    predicted_class = {class_name: float(pred[0][i]) for i, class_name in enumerate(classes)}
    predicted = classes[np.argmax(pred)]
    return predicted_class, predicted

@app.route('/predict', methods=['POST'])
def predict():
    file = request.files['image']
    file.save('uploaded_image.jpg')
    predicted_class = predict_image('uploaded_image.jpg')
    return jsonify({'prediction': predicted_class})


@app.route('/register', methods=['POST'])
def register():
    # Mendapatkan data dari permintaan POST
    data = request.get_json()
    username = data['username']
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
        cursor.execute("INSERT INTO login_normal (username, nama, password) VALUES (%s, %s, %s)", (username, nama, password))
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
    # load_model()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))