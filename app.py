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

    # OPTIONAL: YouTube cookies support (if file exists)
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "noplaylist": True,
    }

    if os.path.exists("cookies.txt"):
        ydl_opts["cookiefile"] = "cookies.txt"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        formats = info.get("formats", [])
        video_url = None

        # -----------------------------
        # 1. Progressive formats (BEST: audio + video)
        # -----------------------------
        progressive = [
            f for f in formats
            if f.get("url")
            and f.get("acodec") != "none"
            and f.get("vcodec") != "none"
        ]

        if progressive:
            video_url = max(
                progressive,
                key=lambda x: x.get("height") or 0
            ).get("url")

        # -----------------------------
        # 2. Fallback: video-only formats
        # -----------------------------
        elif formats:
            video_only = [
                f for f in formats
                if f.get("url") and f.get("vcodec") != "none"
            ]

            if video_only:
                video_url = max(
                    video_only,
                    key=lambda x: x.get("height") or 0
                ).get("url")

        # -----------------------------
        # 3. Final fallback (last resort)
        # -----------------------------
        if not video_url:
            video_url = info.get("url")

        return jsonify({
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "duration": info.get("duration"),
            "video_url": video_url
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        })

# -----------------------------
# RENDER ENTRY POINT
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
