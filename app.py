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

    try:
        ydl_opts = {
            "quiet": True,
            "noplaylist": True,
            "format": "bestvideo+bestaudio/best"
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        video_url = None

        # 🔥 FIX 1: use yt-dlp resolved URL (NOT raw info["url"])
        if info.get("formats"):
            # pick best combined playable format
            formats = [
                f for f in info["formats"]
                if f.get("url")
            ]

            if formats:
                video_url = max(
                    formats,
                    key=lambda x: (
                        x.get("height") or 0,
                        x.get("tbr") or 0
                    )
                ).get("url")

        # 🔥 FIX 2: fallback only if above fails
        if not video_url:
            video_url = info.get("url")

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
    app.run(host="0.0.0.0", port=port)
