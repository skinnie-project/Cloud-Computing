import os
from google.cloud import storage
from flask import Flask, request, jsonify
import base64
from PIL import Image
import numpy as np
import tensorflow as tf
from tensorflow.keras import regularizers
from flaskext.mysql import MySQL

model = None
classPred = ['dry_data', 'normal_data', 'oily_data']

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

def download_model():
    model_file = "models/efficientnetb3_98.h5"  # Replace with your model file name
    destination_path = "/tmp/efficientnetb3_98.h5"  # Path to store the downloaded model file

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(model_file)
    blob.download_to_filename(destination_path)

def load_model():
    global model
    if not os.path.isfile("/tmp/efficientnetb3_98.h5"):
        download_model()
    model = make_model()
    model.load_weights("/tmp/efficientnetb3_98.h5")
    

app = Flask(__name__)

mysql = MySQL()

# Konfigurasi koneksi MySQL
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'skinnie-db-project'
app.config['MYSQL_DATABASE_DB'] = 'skinnie_database'
app.config['MYSQL_DATABASE_HOST'] = '34.128.86.191'

mysql.init_app(app)

#=============================================================================

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


@app.route('/predict', methods=['POST'])
def predict():
    if not request.json or 'image' not in request.json or 'filename' not in request.json:
        return jsonify({"error": "Invalid request payload"}), 400

    image_base64 = request.json['image']
    filename = request.json['filename']

    try:
        # Decode base64 image
        image_bytes = base64.b64decode(image_base64)

        # Determine the file extension
        file_extension = os.path.splitext(filename)[1].lower()

        # Validate file extension
        if file_extension not in ['.jpg', '.jpeg', '.png']:
            return jsonify({"error": "Invalid file format. Only JPG, JPEG, and PNG are supported."}), 400
        

        # Upload image to Cloud Storage
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob('uploaded-photos/' + filename)
        blob.upload_from_string(image_bytes, content_type=f'image/{file_extension[1:]}')

        # Get the public URL of the uploaded image
        public_url = f"https://storage.googleapis.com/{bucket_name}/photos/{filename}"

        # Predict the latest image in Cloud Storage
        load_model()
        blobs = bucket.list_blobs(prefix='uploaded-photos/')
        latest_blob = max(blobs, key=lambda x: x.time_created)
        latest_blob.download_to_filename("/tmp/latest_image.jpg")

        img = Image.open("/tmp/latest_image.jpg")
        test_image_resized = img.resize((224, 224))
        img_array = np.array(test_image_resized) / 255.0
        img_test = np.expand_dims(img_array, axis=0)

        predict = model.predict(img_test)
        y_pred_test_classes_single = np.argmax(predict, axis=1)
        hasil_prediksi = classPred[y_pred_test_classes_single[0]]

        return jsonify({
            'annotatedImageUrl': public_url,
            'label': hasil_prediksi
        }), 200
    except Exception as e:
        return str(e), 500
    
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
    load_model()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
