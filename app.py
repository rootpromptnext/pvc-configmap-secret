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
