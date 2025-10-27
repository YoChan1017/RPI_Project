from flask import Flask, render_template
import mysql.connector
import subprocess
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

@app.route("/")
def index():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT id, timestamp, value, message FROM drunk_log ORDER BY id ASC")
        data = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
    return render_template("index.html", data=data)

if __name__ == "__main__":
    script_path = os.path.join(os.path.dirname(__file__), "Prototype_Test.py")
    process = subprocess.Popen(["python3", script_path])

    try:
        app.run(host="0.0.0.0", port=5000, debug=False)
    finally:
        process.terminate()

