import hmac
import os
import time

import cloudinary
import cloudinary.uploader
import cloudinary.utils
from flask import Flask, jsonify, request

app = Flask(__name__)


def configure_cloudinary() -> bool:
    cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME")
    api_key = os.environ.get("CLOUDINARY_API_KEY")
    api_secret = os.environ.get("CLOUDINARY_API_SECRET")
    if not all([cloud_name, api_key, api_secret]):
        return False
    cloudinary.config(cloud_name=cloud_name, api_key=api_key, api_secret=api_secret, secure=True)
    return True


def check_password() -> bool:
    """Compares the X-Site-Password header against the SITE_PASSWORD env var.
    Fails closed (returns False) if SITE_PASSWORD isn't set at all."""
    site_password = os.environ.get("SITE_PASSWORD")
    if not site_password:
        return False
    supplied = request.headers.get("X-Site-Password", "")
    return hmac.compare_digest(supplied, site_password)


@app.route("/api/sign-upload", methods=["POST"])
def sign_upload():
    if not check_password():
        return jsonify({"error": "Unauthorized"}), 401
    if not configure_cloudinary():
        return jsonify({"error": "Server missing Cloudinary credentials"}), 500

    data = request.get_json(force=True, silent=True) or {}
    public_id = (data.get("public_id") or "").strip()
    overwrite = bool(data.get("overwrite"))

    if not public_id:
        return jsonify({"error": "videoId is required"}), 400

    timestamp = int(time.time())
    params_to_sign = {
        "timestamp": timestamp,
        "public_id": public_id,
        "overwrite": str(overwrite).lower(),
    }
    signature = cloudinary.utils.api_sign_request(params_to_sign, os.environ["CLOUDINARY_API_SECRET"])

    return jsonify(
        {
            "signature": signature,
            "timestamp": timestamp,
            "api_key": os.environ["CLOUDINARY_API_KEY"],
            "cloud_name": os.environ["CLOUDINARY_CLOUD_NAME"],
            "public_id": public_id,
            "overwrite": str(overwrite).lower(),
        }
    )


@app.route("/api/rename", methods=["POST"])
def rename():
    if not check_password():
        return jsonify({"error": "Unauthorized"}), 401
    if not configure_cloudinary():
        return jsonify({"error": "Server missing Cloudinary credentials"}), 500

    data = request.get_json(force=True, silent=True) or {}
    old_id = (data.get("old_id") or "").strip()
    new_id = (data.get("new_id") or "").strip()
    overwrite = bool(data.get("overwrite"))

    if not old_id or not new_id:
        return jsonify({"error": "Both the current and new videoId are required"}), 400

    try:
        result = cloudinary.uploader.rename(old_id, new_id, resource_type="video", overwrite=overwrite)
        return jsonify({"public_id": result.get("public_id"), "secure_url": result.get("secure_url")})
    except cloudinary.exceptions.Error as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/check-password", methods=["POST"])
def check_password_route():
    """Lets the frontend verify a password attempt without doing anything else."""
    if check_password():
        return jsonify({"ok": True})
    return jsonify({"ok": False}), 401
