import os, time
from datetime import datetime, timezone
from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
VERSION = os.getenv("SERVICE_VERSION", "v1")
DB = dict(host=os.getenv("DB_HOST", "database"), port=int(os.getenv("DB_PORT", "3306")),
          user=os.getenv("DB_USER", "safedeploy"), password=os.getenv("DB_PASSWORD", "safedeploy_dev_password"),
          database=os.getenv("DB_NAME", "safedeploy"), connection_timeout=3)

def connect(retries=12):
    error = None
    for _ in range(retries):
        try: return mysql.connector.connect(**DB)
        except Error as exc:
            error = exc
            time.sleep(2)
    raise error

def event(version, status, message):
    db = connect()
    try:
        cur = db.cursor()
        cur.execute("INSERT INTO deployment_events(version,status,message) VALUES(%s,%s,%s)",
                    (version, status, message))
        db.commit()
        cur.close()
    finally: db.close()

@app.get("/")
def home():
    return jsonify(service="SafeDeploy AI Python Service", version=VERSION, status="running")

@app.get("/health")
def health():
    try:
        db = connect(1); db.close()
        return jsonify(status="healthy", service="python-service", database="connected", version=VERSION)
    except Error:
        return jsonify(status="unhealthy", service="python-service", database="unavailable"), 503

@app.get("/version")
def version():
    return jsonify(service="python-service", version=VERSION)

@app.get("/api/events")
def events():
    db = connect()
    try:
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT id,version,status,message,created_at FROM deployment_events ORDER BY id DESC LIMIT 100")
        result = cur.fetchall(); cur.close()
        return jsonify(result)
    finally: db.close()

@app.post("/api/deploy")
def deploy():
    data = request.get_json(silent=True) or {}
    version = data.get("version")
    fail = data.get("simulate_failure", False)
    if not isinstance(version, str) or not version.strip() or len(version.strip()) > 80:
        return jsonify(error="version must be a non-empty string up to 80 characters"), 400
    if not isinstance(fail, bool):
        return jsonify(error="simulate_failure must be true or false"), 400
    version = version.strip()
    if fail:
        event(version, "FAILED", "Simulated deployment health check failed")
        event(os.getenv("CURRENT_ACTIVE_VERSION", "v1"), "ROLLED_BACK",
              f"Rollback recorded after {version} failed; use deployment/rollback.sh for container rollback")
        return jsonify(deployment="FAILED", rollback="RECORDED",
                       message="Failure and rollback events recorded; container switching is handled by deployment scripts.")
    event(version, "ACTIVE", "Deployment event recorded; container rollout is handled by deployment scripts")
    return jsonify(deployment="RECORDED", version=version), 202

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
