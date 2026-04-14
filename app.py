from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import uuid
import subprocess

app = Flask(__name__)
CORS(app)

# =========================
# HOME
# =========================
@app.route("/")
def home():
    return "K-Edge SaaS Backend Running ✅"


# =========================
# VIDEO INFO + HD/SD
# =========================
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

        formats = info.get("formats", [])

        video_formats = [
            f for f in formats
            if f.get("url") and f.get("vcodec") != "none"
        ]

        video_formats = sorted(
            video_formats,
            key=lambda x: x.get("height") or 0,
            reverse=True
        )

        hd_video = video_formats[0]["url"] if len(video_formats) > 0 else None
        sd_video = video_formats[-1]["url"] if len(video_formats) > 1 else hd_video

        return jsonify({
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "duration": info.get("duration"),
            "hd_video": hd_video,
            "sd_video": sd_video
        })

    except Exception as e:
        return jsonify({"error": str(e)})


# =========================
# 🎧 MP3 CONVERSION (FFMPEG)
# =========================
@app.route("/api/mp3")
def mp3():
    url = request.args.get("url")

    if not url:
        return jsonify({"error": "No URL provided"})

    try:
        file_id = str(uuid.uuid4())
        output_file = f"/tmp/{file_id}.mp3"

        # STEP 1: FORCE BEST AUDIO ONLY (IMPORTANT FIX)
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": f"/tmp/{file_id}.%(ext)s",
            "quiet": True,
            "noplaylist": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        # get downloaded file path
        input_file = ydl.prepare_filename(info)

        # STEP 2: FORCE FFMPEG CONVERSION (CLEAN)
        command = [
            "ffmpeg",
            "-y",
            "-i", input_file,
            "-vn",
            "-acodec", "libmp3lame",
            "-ab", "192k",
            output_file
        ]

        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # DEBUG (VERY IMPORTANT)
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
# FILE DOWNLOAD SERVER
# =========================
@app.route("/download/<filename>")
def download_file(filename):
    file_path = f"/tmp/{filename}"

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found or expired"})

    return send_file(file_path, as_attachment=True)


# =========================
# RENDER ENTRY POINT
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
