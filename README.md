# Cloud Computing
Use api-endpoint-python. This program using Google Cloud Run

Up-to-date API Doc: https://docs.google.com/document/d/1wVXSzpBjuUVRqfHh6AFD8sjnknrv_X4iSuyU-dqs4mY/edit?usp=sharing
## URL

https://skinnie.my.id/{endpoint}

### Register

* Endpoint  : /register
* Method    : POST
* Request body :

```
username  as string
email     as string
nama      as string
password  as string
```

### Login

* Endpoint  : /login
* Method    : POST
* Request body :

```
username  as string
password  as string
```

### Forgot Password

* Endpoint  : /forgot
* Method    : POST
* Request body :

```
username  as string
new_password  as string
```

### Register Google

* Endpoint  : /register/google
* Method    : POST
* Request body :

```
name      as string
nickname  as string
email     as string
```

### Product Popular Homepage

* Endpoint  : /article
* Method    : GET
* Request   : https://skinnie.my.id/article?id=1

### Product Detail

* Endpoint  : /data/detail
* Method    : GET
* Request   : https://skinnie.my.id/data/detail?id=1

### Show Article

* Endpoint  : /data/popular
* Method    : GET
* Request body : None

### Predict Image (Terpakai)

* Endpoint  : /predict
* Method    : POST
* Request body :

```
image     as request.files
filename  as request.form
```

### Predict base64

* Endpoint  : /predict/base64
* Method    : POST
* Request body :

```
image     as string
filename  as string
```
### Predict Result Ingredients

* Endpoint      : /predict/filter
* Method        : GET
* Request body  : https://skinnie.my.id/predict/filter?ingredients=Semua ingredients&subcategory=Semua subcategory&predicted=normal

```
ingredients   as string
predicted     as string (ambil dari hasil predict sebelumnya)
subcategory   as string
filter_by     as string (opsional)
```

### Product Recommend

* Endpoint      : /predict/recommend
* Method        : GET
* Request body  : https://skinnie.my.id/predict/recommend?predicted=Normal

```
predicted     as string (ambil dari hasil predict sebelumnya)
```
