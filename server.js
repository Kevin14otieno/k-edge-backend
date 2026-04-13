import express from "express";
import cors from "cors";
import { exec } from "child_process";

const app = express();
app.use(cors());

app.get("/api/download", (req, res) => {
    const url = req.query.url;

    if (!url) {
        return res.json({ error: "No URL provided" });
    }

    const command = `npx yt-dlp -j "${url}"`;

    exec(command, (error, stdout) => {
        if (error) {
            return res.json({ error: "Failed to fetch video" });
        }

        try {
            const data = JSON.parse(stdout);

            res.json({
                title: data.title,
                thumbnail: data.thumbnail,
                duration: data.duration,
                video_url: data.url
            });

        } catch (e) {
            res.json({ error: "Invalid response" });
        }
    });
});

app.listen(3000, () => {
    console.log("K-Edge backend running");
});
