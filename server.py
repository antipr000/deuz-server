from flask import Flask, request, jsonify, send_file
from PIL import Image
from rembg import remove
from flask_cors import cross_origin
import io
from firebase_admin.auth import verify_id_token
from firebase_admin import initialize_app, credentials
from firebase_credentials import cert_dict
from super_image import EdsrModel, ImageLoader
import requests
import os

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 6 * 1024 * 1024  # 6 MB limit


@app.route("/auth", methods=["POST"])
@cross_origin()
def auth():
    body = request.get_json()
    id_token = body["idToken"]
    decoded_token = verify_id_token(id_token)
    return jsonify({"uid": decoded_token["uid"]})


@app.route("/geolocation", methods=["GET"])
@cross_origin()
def get_geolocation():
    ip = request.args.get("ip")
    print(ip)
    response = requests.get("http://ip-api.com/json/" + ip)
    data = response.json()
    return jsonify(data)


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


@app.route("/upscale", methods=["POST"])
@cross_origin()
def upscale():
    if "image" not in request.files:
        return jsonify({"error": "No image found in request"}), 400

    file = request.files["image"]

    if file.filename == "":
        return jsonify({"error": "No selected image"}), 400
    file_name = file.filename
    print("Here", file_name)
    try:
        scale_factor = request.form.get("scale", default=2, type=int)
        input_image = Image.open(file.stream)
        model = EdsrModel.from_pretrained("eugenesiow/edsr-base", scale=scale_factor)
        inputs = ImageLoader.load_image(input_image)
        preds = model(inputs)
        file_name = file_name.split(".")[0] + ".png"
        ImageLoader.save_image(preds, file_name)
        img_byte_arr = io.BytesIO()
        pil_image = Image.open(file_name)
        pil_image.save(img_byte_arr, format="PNG")
        img_byte_arr.seek(0)
        os.remove(file_name)
        return send_file(img_byte_arr, mimetype="image/png")
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    initialize_app(credentials.Certificate(cert_dict))
    app.run(host="0.0.0.0", port=8000, debug=True)
