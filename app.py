from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import uuid

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "K-Edge Backend Running ✅"


@app.route("/api/download")
def download():
    url = request.args.get("url")

    if not url:
        return jsonify({"error": "No URL provided"})

    try:
        file_id = str(uuid.uuid4())
        output_path = f"/tmp/{file_id}.mp4"

        ydl_opts = {
            "format": "bestvideo+bestaudio/best",
            "outtmpl": output_path,
            "merge_output_format": "mp4",
            "quiet": True,
            "noplaylist": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        return jsonify({
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "duration": info.get("duration"),
            "video_url": f"https://k-edge-backend.onrender.com/file/{file_id}"
        })

    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/file/<file_id>")
def serve_file(file_id):
    path = f"/tmp/{file_id}.mp4"

    if not os.path.exists(path):
        return jsonify({"error": "File not found"})

    return send_file(path, as_attachment=True)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
