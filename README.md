# Cloud Computing
Use api-endpoint-python. This program using Google Cloud Run

API Doc: https://docs.google.com/document/d/1wVXSzpBjuUVRqfHh6AFD8sjnknrv_X4iSuyU-dqs4mY/edit?usp=sharing
## URL
Landing Page: https://skinnie.my.id

https://skinnie.my.id/{endpoint}

## Deploy

* Clone this repository or Copy to the Google Cloud Console via Terminal or Editor
* We need to prepare this 2 services before, Cloud SQL, Cloud Storage
  * Cloud SQL, we named it skinnie_database, after created, there will be public ip address that we should noted it
  * Cloud Storage, we named it skinnie-bucket, this storage used for save skincare photos and uploaded photos
* After prepared all those services, don't forget to edit some code (in folder auth, predict, product) to make sure it will run well
* Then, we create the containerimage to deploy to Cloud Run, you can use this code (make sure that you are in correct directory in terminal for example xxxxxxxxxxx@cloudshell:~/api-endpoint)

```
docker build -t <name> .
docker tag api-endpoint gcr.io/<name_of_google_project>/<name>
docker push gcr.io/<name_of_google_project>/<name>
```

* After finish building the containerimage, open the Cloud Run, Create Service, and for Container Image URL, click Select, Container Registry, expand gcr.io/<name_of_google_project>/<name>, then you will find the latest containerimage, choose it and click Select
* Then you just to configure your Cloud Run with Container Port 3000. We recommend to use minimum 2 GiB of memory.

## Reference

* https://www.youtube.com/watch?v=vieoHqt7pxo&pp=ygUTY2xvdWQgcnVuIGFpIGRlcGxveQ%3D%3D
* https://www.youtube.com/watch?v=xcODUk0o6tU&t=619s&pp=ygUTY2xvdWQgcnVuIGFpIGRlcGxveQ%3D%3D
* https://www.python-engineer.com/posts/cloud-run-deployment/
* https://github.com/Santhoshkumard11/image-classification-and-deployed-using-flask
* https://ojs.unpkediri.ac.id/index.php/intensif/article/view/12792
 
## Endpoint
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

### Login Google

* Endpoint  : /login/google
* Method    : POST
* Request body :

```
name      as string
nickname  as string
email     as string
```

### Product Popular Homepage

* Endpoint  : /data/popular
* Method    : GET
* Request   : https://skinnie.my.id/data/popular

### Product Detail

* Endpoint  : /data/detail
* Method    : GET
* Parameter : product
* Request   : https://skinnie.my.id/data/search?product=wardah

### Product Search

* Endpoint  : /data/search
* Method    : GET
* Parameter : id
* Request   : https://skinnie.my.id/data/detail?id=1

### Show Article

* Endpoint  : /article
* Method    : GET

```
Request (URL)

Tampil semua artikel:
https://skinnie.my.id/article

Ambil Detail:
https://skinnie.my.id/article?id=1
```

### Predict Image

* Endpoint  : /predict
* Method    : POST
* Request body :

```
image     as request.files
filename  as request.form
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
