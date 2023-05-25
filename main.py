import os
from google.cloud import storage
from flask import Flask, request, jsonify
import base64
from PIL import Image
import numpy as np
import tensorflow as tf
from tensorflow.keras.regularizers import l2

model = None
classPred = ['incorrect_mask', 'with_mask', 'without_mask']

def make_model():
    model = tf.keras.models.Sequential([
        tf.keras.layers.Conv2D(32, (3,3), activation='relu', input_shape=(150, 150, 3)),
        tf.keras.layers.MaxPooling2D(2, 2),
        tf.keras.layers.Conv2D(64, (3,3), activation='relu'),
        tf.keras.layers.MaxPooling2D(2,2),
        tf.keras.layers.Conv2D(128, (3,3), activation='relu'),
        tf.keras.layers.MaxPooling2D(2,2),
        tf.keras.layers.Conv2D(128, (3,3), activation='relu'),
        tf.keras.layers.MaxPooling2D(2,2),
        tf.keras.layers.Conv2D(512, (3,3), activation='relu'),
        tf.keras.layers.MaxPooling2D(2,2),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(512, activation='relu', kernel_regularizer=l2(0.01)),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(128, activation='relu', kernel_regularizer=l2(0.01)),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(3, activation='softmax')
    ])
    return model

bucket_name = "skinnie-bucket"

def download_model():
    model_file = "models/no-tl-3.h5"  # Replace with your model file name
    destination_path = "/tmp/no-tl-3.h5"  # Path to store the downloaded model file

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(model_file)
    blob.download_to_filename(destination_path)

def load_model():
    global model
    if not os.path.isfile("/tmp/no-tl-3.h5"):
        download_model()
    model = make_model()
    model.load_weights("/tmp/no-tl-3.h5")

def hello_world(request):
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
        test_image_resized = img.resize((150, 150))
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