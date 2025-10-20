from flask import Flask, render_template
import sqlite3
import subprocess
import os

app = Flask(__name__)

@app.route("/")
def index():
    conn = sqlite3.connect("drunk_log.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, timestamp, value, message FROM log ORDER BY id ASC")
    data = cursor.fetchall()
    conn.close()
    return render_template("index.html", data=data)

if __name__ == "__main__":
    script_path = os.path.join(os.path.dirname(__file__), "Prototype_Test.py")
    
    process = subprocess.Popen(["python3", script_path])

    try:
        app.run(host="0.0.0.0", port=5000, debug=False)
    finally:
        process.terminate()

