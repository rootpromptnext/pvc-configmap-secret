# Kubernetes ConfigMap + Secret + PVC + MySQL + Python App

This project demonstrates a **complete Kubernetes application deployment** using:

* **ConfigMap** for application configuration
* **Secret** for sensitive data
* **PersistentVolumeClaim (PVC)** backed by **AWS EBS**
* **MySQL database**
* **Python Flask application**
* **Kubernetes Services**
* Deployment on **Amazon EKS**

The Python application reads database connection parameters from **ConfigMap and Secret**, connects to **MySQL**, and displays the connection status.

---

# Architecture

```
              ConfigMap
        (DB_HOST | DB_NAME DB_USER)
                 |
                 v
            Python App
                 |
                 v
              Service
                 |
                 v
               MySQL
                 |
                 v
               PVC
                 |
                 v
         AWS EBS Volume (gp2)

                 ^
                 |
               Secret
            DB_PASSWORD
```

---

# Prerequisites

* AWS account
* EKS cluster
* kubectl configured
* Docker installed
* eksctl installed

---

# Install EBS CSI Driver (Required for PVC)

Install the AWS EBS CSI driver addon:

```bash
eksctl create addon \
  --name aws-ebs-csi-driver \
  --cluster my-cluster2 \
  --region us-east-1
```

This enables **dynamic EBS volume provisioning** for Kubernetes PVCs.

---

# Application Code

## app.py

```python
import os
import mysql.connector
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():

    db_host = os.getenv("DB_HOST")
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME")

    try:
        conn = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_pass,
            database=db_name
        )

        return f"""
        <h1>MySQL Connection Successful</h1>
        <p>Host: {db_host}</p>
        <p>Database: {db_name}</p>
        <p>User: {db_user}</p>
        """

    except Exception as e:
        return f"<h1>Connection Failed</h1><p>{e}</p>"


app.run(host="0.0.0.0", port=5000)
```

---

# requirements.txt

```
flask
mysql-connector-python
```

---

# Install Docker

```bash
sudo dnf install -y docker
sudo usermod -aG docker $USER
sudo systemctl restart docker
sudo systemctl enable docker
```

---

# Build Docker Image

```bash
docker build -t app:v1 .
docker images
```

---

# Run Container Locally (Without Environment Variables)

```bash
docker run -d -p 5000:5000 app:v1
```

Test:

```bash
curl localhost:5000
```

Expected output:

```
Connection Failed
Can't connect to MySQL server
```

This is expected because **no database configuration was provided**.

---

# Push Image to Docker Hub

Tag the image:

```bash
docker tag app:v1 rootpromptnext/app:v1
```

Login:

```bash
docker login -u rootpromptnext
```

Push:

```bash
docker push rootpromptnext/app:v1
```

---

# Kubernetes Resources

This project uses the following Kubernetes resources:

| Resource   | Purpose                      |
| ---------- | ---------------------------- |
| ConfigMap  | Store DB configuration       |
| Secret     | Store DB passwords           |
| PVC        | Persistent storage for MySQL |
| Deployment | Run MySQL and Python app     |
| Service    | Expose MySQL and App         |

---

# Deploy MySQL (ConfigMap + Secret + PVC)

Apply MySQL deployment:

```bash
kubectl apply -f mysql-deploy.yaml
```

Verify:

```bash
kubectl get pods
kubectl get pvc
kubectl get svc
```

Example output:

```
NAME        STATUS   CAPACITY
mysql-pvc   Bound    5Gi
```

The PVC dynamically creates an **EBS volume** using the `gp2` storage class.

---

# Deploy Python Application

```bash
kubectl apply -f app-deploy.yaml
```

Verify resources:

```bash
kubectl get all
```

Example:

```
pod/mysql-xxxx
pod/python-app-xxxx

service/mysql
service/python-app
```

---

# Verify PVC

```bash
kubectl get pvc
```

Example:

```
NAME        STATUS   CAPACITY
app-pvc     Bound    1Gi
mysql-pvc   Bound    5Gi
```

These PVCs are backed by **AWS EBS volumes**.

---

# Test Application

Find the NodePort service:

```bash
kubectl get svc python-app
```

Example:

```
python-app NodePort 80:30080
```

Access:

```
http://NODE_IP:30080
```

Expected output:

```
MySQL Connection Successful
Host: mysql
Database: myappdb
User: myappuser
```

---

# Test Inside Pod

You can also test the application from inside the container:

```bash
kubectl exec -it pod/python-app-XXXX -- /bin/bash
```

Then run:

```bash
curl python-app
```

Output:

```
MySQL Connection Successful
Host: mysql
Database: myappdb
User: myappuser
```

---

# Persistent Storage Verification

Check PVC:

```bash
kubectl get pvc
```

You should see **Bound volumes**, meaning Kubernetes dynamically created **EBS disks**.

These volumes persist data even if the **MySQL pod is recreated**.

