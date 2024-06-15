from flask import Flask, request, jsonify, send_file
from PIL import Image
from rembg import remove
from flask_cors import cross_origin
import io
from firebase_admin.auth import verify_id_token
from firebase_admin import initialize_app, credentials
from firebase_credentials import cert_dict

app = Flask(__name__)


@app.route("/auth", methods=["POST"])
@cross_origin()
def auth():
    body = request.get_json()
    id_token = body["idToken"]
    decoded_token = verify_id_token(id_token)
    return jsonify({"uid": decoded_token["uid"]})


@app.route("/removebg", methods=["POST"])
@cross_origin()
def remove_bg():
    if "image" not in request.files:
        return jsonify({"error": "No image found in request"}), 400

    file = request.files["image"]

    if file.filename == "":
        return jsonify({"error": "No selected image"}), 400

    try:
        input_image = Image.open(file.stream)
        output_image = remove(input_image)
        img_byte_arr = io.BytesIO()
        output_image.save(img_byte_arr, format="PNG")
        img_byte_arr.seek(0)
        return send_file(img_byte_arr, mimetype="image/png")
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    initialize_app(credentials.Certificate(cert_dict))
    app.run(host="0.0.0.0", port=8000, debug=True)
