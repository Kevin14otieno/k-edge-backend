from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import os

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

    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "noplaylist": True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        video_url = None

        # direct url
        if info.get("url"):
            video_url = info.get("url")

        # fallback formats
        elif info.get("formats"):
            formats = [f for f in info["formats"] if f.get("url")]

            if formats:
                video_url = max(formats, key=lambda x: x.get("height", 0)).get("url")

        return jsonify({
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "duration": info.get("duration"),
            "video_url": video_url
        })

    except Exception as e:
        return jsonify({"error": str(e)})

# 🔥 IMPORTANT FOR RENDER
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
