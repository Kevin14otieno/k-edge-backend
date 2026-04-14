from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__)
CORS(app)

# =========================
# HOME
# =========================
@app.route("/")
def home():
    return "K-Edge Backend Running ✅"


# =========================
# VIDEO DOWNLOAD (FIXED AUDIO ISSUE)
# =========================
@app.route("/api/download")
def download():
    url = request.args.get("url")

    if not url:
        return jsonify({"error": "No URL provided"})

    try:
        ydl_opts = {
            "quiet": True,
            "noplaylist": True,

            # 🔥 KEY FIX: MERGE VIDEO + AUDIO
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4"
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        return jsonify({
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "duration": info.get("duration"),

            # 🎯 FIXED: now returns proper merged stream
            "video_url": info.get("url")
        })

    except Exception as e:
        return jsonify({"error": str(e)})


# =========================
# MP3 CONVERSION (OPTIONAL BUT INCLUDED)
# =========================
@app.route("/api/mp3")
def mp3():
    url = request.args.get("url")

    if not url:
        return jsonify({"error": "No URL provided"})

    try:
        import uuid
        import subprocess

        file_id = str(uuid.uuid4())
        output_file = f"/tmp/{file_id}.mp3"

        # STEP 1: download best audio
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": f"/tmp/{file_id}.%(ext)s",
            "quiet": True,
            "noplaylist": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            input_file = ydl.prepare_filename(info)

        # STEP 2: convert to MP3 using ffmpeg
        command = [
            "ffmpeg",
            "-y",
            "-i", input_file,
            "-vn",
            "-acodec", "libmp3lame",
            "-ab", "192k",
            output_file
        ]

        result = subprocess.run(command, capture_output=True)

        if result.returncode != 0:
            return jsonify({
                "error": "FFmpeg conversion failed",
                "details": result.stderr.decode()
            })

        return jsonify({
            "download_url": f"https://k-edge-backend.onrender.com/download/{file_id}.mp3"
        })

    except Exception as e:
        return jsonify({"error": str(e)})


# =========================
# FILE SERVER
# =========================
@app.route("/download/<filename>")
def download_file(filename):
    file_path = f"/tmp/{filename}"

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"})

    from flask import send_file
    return send_file(file_path, as_attachment=True)


# =========================
# START SERVER
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
