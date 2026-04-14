from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)  # 🔥 allow frontend access

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

        # 🔥 FIX: Extract video properly
        video_url = None

        # Case 1: direct url exists
        if info.get("url"):
            video_url = info.get("url")

        # Case 2: use formats (IMPORTANT)
        elif info.get("formats"):
            formats = info.get("formats")

            # filter valid formats
            valid_formats = [f for f in formats if f.get("url")]

            if valid_formats:
                # pick best quality (last one usually best)
                video_url = valid_formats[-1]["url"]

        return jsonify({
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "duration": info.get("duration"),
            "video_url": video_url
        })

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
