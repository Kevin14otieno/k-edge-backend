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
        # 🔥 FIX: LET YT-DLP HANDLE AUDIO + VIDEO MERGING
        ydl_opts = {
            "quiet": True,
            "noplaylist": True,
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4"
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        return jsonify({
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "duration": info.get("duration"),

            # 🔥 FIXED: proper playable stream
            "video_url": info.get("url")
        })

    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
