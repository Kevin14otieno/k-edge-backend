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
    "noplaylist": True,
    "cookiefile": "cookies.txt",  #  IMPORTANT
    "format": "best[ext=mp4][height<=720]"
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        video_url = None

        # direct format
        if info.get("url"):
            video_url = info.get("url")

       
        elif info.get("formats"):
            formats = info.get("formats")

            safe_formats = [
                f for f in formats
                if f.get("url")
                and f.get("ext") == "mp4"
                and f.get("acodec") != "none"
                and f.get("vcodec") != "none"
            ]

            if safe_formats:
                video_url = max(
                    safe_formats,
                    key=lambda x: x.get("height") or 0
                ).get("url")

        return jsonify({
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "duration": info.get("duration"),
            "video_url": video_url
        })

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port),  replace here
