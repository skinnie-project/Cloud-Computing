from google.cloud import storage
from flask import Flask, request, jsonify
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.efficientnet import preprocess_input
import tensorflow as tf
import tensorflow_hub as hub
import base64
from PIL import Image
import numpy as np
import requests
from io import BytesIO
import mimetypes

bucket_name = "skinnie-bucket"

app = Flask(__name__)

model = None

custom_objects = {'KerasLayer': hub.KerasLayer}

def load_my_model():
    global model
    model = tf.keras.models.load_model('model/model2.h5', custom_objects=custom_objects)
    model.load_weights('model/model2-weights.h5')


def predict_image(image_path):
    if model is None:
        load_my_model()
    img = image.load_img(image_path, target_size=(224, 224))
    img = np.array(img) / 255.0 #new
    img = img[np.newaxis, ...] #new
    pred = model.predict(img)
    classes = ['Kering', 'Normal', 'Berminyak']
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

    # Upload to Google Cloud Storage
    file_blob.upload_from_string(image_data, content_type='image/jpeg')
    print(f"Image {filename} uploaded to Google Cloud Storage.")

    print(f"Image {filename} has been public.")

    image_url = f"https://storage.googleapis.com/{bucket_name}/uploaded-photos/{filename}"
    return image_url

def upload_image_to_storage_file(file, filename):
    
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)

    directory = "uploaded-photos"
    blob_path = f"{directory}/{filename}"
    file_blob = bucket.blob(blob_path)

    content_type, _ = mimetypes.guess_type(filename)
    file.seek(0)
    
    # Upload to Google Cloud Storage
    file_blob.upload_from_file(file, content_type=content_type)
    print(f"Image {filename} uploaded to Google Cloud Storage.")

    print(f"Image {filename} has been public.")

    image_url = f"https://storage.googleapis.com/{bucket_name}/uploaded-photos/{filename}"
    return image_url


def predict():
    file = request.files['image']
    filename = request.form['filename']
    file.save('uploaded_images.jpg')
    upload_image_to_storage_file(file, filename)
    returned_predicted_class, returned_predicted = predict_image('uploaded_images.jpg')
    if returned_predicted == "Normal":
        return jsonify(
            {
                'prediction_rate': returned_predicted_class, 
                'predicted': returned_predicted,
                'key_ingredients_1':"Niacinamide",       
                'key_ingredients_2':"Lactic Acid",
                'key_ingredients_3':"Hyaluronic Acid",
                'key_ingredients_4':"Aloe Vera",
                    
             })
    elif returned_predicted == "Berminyak":
        return jsonify(
            {
                'prediction_rate': returned_predicted_class, 
                'predicted': returned_predicted,
                'key_ingredients_1':"Niacinamide",
                'key_ingredients_2':"Salicylic Acid",
                'key_ingredients_3':"Hyaluronic Acid",
                'key_ingredients_4':"Glycolic Acid",
             })
    else:
        return jsonify(
            {
                'prediction_rate': returned_predicted_class, 
                'predicted': returned_predicted,
                'key_ingredients_1':"Glycerin",
                'key_ingredients_2':"Retinol",
                'key_ingredients_3':"Lactic Acid",
                'key_ingredients_4':"Squalane",
             })
    

def predict_base64():
    image_base64 = request.json['image']
    filename = request.json['filename']
    olahb64 = upload_image_to_storage(image_base64, filename)
    
    response = requests.get(olahb64)
    image = Image.open(BytesIO(response.content))
    image.save('predict/uploaded_images.jpg')
    global predicted_result
    returned_predicted_class, returned_predicted = predict_image('predict/uploaded_images.jpg')
    
    predicted_result = returned_predicted
    print(predicted_result)
    return jsonify({'prediction_rate': returned_predicted_class, 'predicted': returned_predicted})
