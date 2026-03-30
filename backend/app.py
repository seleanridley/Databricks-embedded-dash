import os
import time
import json
import base64
import urllib.parse
from datetime import datetime

import requests
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv(".env")

app = Flask(__name__)
CORS(app)

def mint_databricks_token():
    workspace_url = os.environ.get("DATABRICKS_WORKSPACE_URL")
    client_id = os.environ.get("DATABRICKS_CLIENT_ID")
    client_secret = os.environ.get("DATABRICKS_CLIENT_SECRET")
    dashboard_id = os.environ.get("DATABRICKS_DASHBOARD_ID")

    if not all([workspace_url, client_id, client_secret, dashboard_id]):
        raise Exception("Missing required Databricks environment variables.")

    basic_auth = base64.b64encode(
        f"{client_id}:{client_secret}".encode()
    ).decode()

    oidc_response = requests.post(
        f"{workspace_url}/oidc/v1/token",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {basic_auth}",
        },
        data=urllib.parse.urlencode({
            "grant_type": "client_credentials",
            "scope": "all-apis",
        }),
    )
    oidc_response.raise_for_status()
    oidc_token = oidc_response.json()["access_token"]

    token_info_response = requests.get(
        f"{workspace_url}/api/2.0/lakeview/dashboards/"
        f"{dashboard_id}/published/tokeninfo"
        f"?external_viewer_id=embedded-app-user",
        headers={"Authorization": f"Bearer {oidc_token}"},
    )
    token_info_response.raise_for_status()
    token_info = token_info_response.json()

    params = token_info.copy()
    authorization_details = params.pop("authorization_details", None)
    params.update({
        "grant_type": "client_credentials",
        "authorization_details": json.dumps(authorization_details),
    })

    scoped_response = requests.post(
        f"{workspace_url}/oidc/v1/token",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {basic_auth}",
        },
        data=urllib.parse.urlencode(params),
    )
    scoped_response.raise_for_status()
    scoped_token_data = scoped_response.json()

    return {
        "access_token": scoped_token_data["access_token"],
        "expires_in": scoped_token_data.get("expires_in", 3600),
        "created_at": int(time.time()),
    }

@app.route("/api/dashboard/embed-config", methods=["GET"])
def get_embed_config():
    token_data = mint_databricks_token()

    return jsonify({
        "workspace_url": os.environ.get("DATABRICKS_WORKSPACE_URL"),
        "workspace_id": os.environ.get("DATABRICKS_WORKSPACE_ID"),
        "dashboard_id": os.environ.get("DATABRICKS_DASHBOARD_ID"),
        "warehouse_id": os.environ.get("DATABRICKS_WAREHOUSE_ID"),
        "embed_token": token_data["access_token"],
        "token_expires_in": token_data["expires_in"],
    })

@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
