
from flask import Flask, render_template, request, jsonify
import requests
import asyncio
import edge_tts
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
import os

app = Flask(__name__)

HF_TOKEN = "YOUR_HUGGINGFACE_TOKEN"

# Styles dictionary
STYLE_PROMPTS = {
    "3d_pixar": "3D Pixar animation style, cute expressive character, cinematic lighting, 8k render",
    "anime": "Makoto Shinkai anime style, vibrant colors, detailed 2D cel-shaded artwork",
    "yarn": "Detailed felted yarn stop-motion style, wool texture, handmade craft aesthetic",
    "2d_cartoon": "Classic 2D cartoon animation, bold outlines, vector style"
}

# Free HuggingFace Inference Model
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

def generate_image(prompt, style_choice, output_path):
    full_prompt = f"{prompt}, {STYLE_PROMPTS.get(style_choice, '')}"
    response = requests.post(API_URL, headers=headers, json={"inputs": full_prompt})
    with open(output_path, "wb") as f:
        f.write(response.content)

async def generate_voice(text, output_audio):
    communicate = edge_tts.Communicate(text, "hi-IN-MadhurNeural") # Hindi Voice
    await communicate.save(output_audio)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    story = data.get("story")
    style = data.get("style")

    # 1. Generate Voice
    audio_path = "output.mp3"
    asyncio.run(generate_voice(story, audio_path))

    # 2. Generate Image Frame
    image_path = "scene.jpg"
    generate_image(story, style, image_path)

    # 3. Stitch with MoviePy
    audio_clip = AudioFileClip(audio_path)
    video_clip = ImageClip(image_path).set_duration(audio_clip.duration)
    video_clip = video_clip.set_audio(audio_clip)
    
    final_output = "static/final_video.mp4"
    video_clip.write_videofile(final_output, fps=24)

    return jsonify({"status": "success", "video_url": "/" + final_output})

if __name__ == "__main__":
    app.run(debug=True)
