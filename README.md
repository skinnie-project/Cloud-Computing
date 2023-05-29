# Cloud Computing
Use api-endpoint-python. This program using Google Cloud Run

## URL

https://skinnie.my.id/{endpoint}

### Register

* Endpoint  : /register
* Method    : POST
* Request body :

```
username  as string
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

### Predict

* Endpoint  : /predict
* Method    : POST
* Request body :

```
image     as base64
filename  as string
```

* Referensi: https://github.com/zarkiya/vision-api
