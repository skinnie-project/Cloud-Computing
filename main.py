import os
from flask import Flask
from auth.login import login
from auth.register import register, register_google
from auth.forgot import forgot
from product.show import get_popular, get_product_detail
from product.article import get_article
from product.filterIngredients import filterIngredients, filterSubcategory
from product.filterProduct import filterProducts, filterSubcategoryRekomen
from predict.predict import predict, predict_base64
from predict.recommend import get_predict_result, get_product_rekomen

app = Flask(__name__)

#=============================================================================
# Auth
@app.route('/login', methods=['POST'])
def login_route():
    return login()

@app.route('/register', methods=['POST'])
def register_route():
    return register()

@app.route('/register/google', methods=['POST'])
def register_google_route():
    return register_google()

@app.route('/forgot', methods=['POST'])
def forgot_route():
    return forgot()

#=============================================================================
# Product Popular Homepage and Detail
@app.route('/data/popular', methods=['GET'])
def get_popular_route():
    return get_popular()

@app.route('/data/detail', methods=['GET'])
def get_product_detail_route():
    return get_product_detail()

#=============================================================================
# Proses Predict
@app.route('/predict', methods=['POST'])
def predict_route():
    return predict()

@app.route('/predict/base64', methods=['POST'])
def predict_base64_route():
    return predict_base64()

#=============================================================================
# Ingredients
@app.route('/predict/result', methods=['GET'])
def get_predict_result_route():
    return get_predict_result()

@app.route('/predict/result/filter', methods=['GET'])
def get_ingredients_filter_route():
    return filterIngredients()

@app.route('/predict/result/filter/subcategory', methods=['GET'])
def get_ingredients_filter_subcategory_route():
    return filterSubcategory()

#=============================================================================
# Produk
@app.route('/predict/recommend', methods=['GET'])
def get_product_rekomen_route():
    return get_product_rekomen()

@app.route('/predict/recommend/filter', methods=['GET'])
def get_product_filter_route():
    return filterProducts()

@app.route('/predict/recommend/filter/subcategory', methods=['GET'])
def get_product_filter_subcategory_route():
    return filterSubcategoryRekomen()

#=============================================================================

@app.route('/article', methods=['GET'])
def get_article_route():
    return get_article()
    
if __name__ == '__main__':
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "auth/key.json" 
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
