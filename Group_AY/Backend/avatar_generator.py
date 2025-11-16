"""
Avatar Video Generator using D-ID API
Creates talking head avatars that can be overlaid on educational videos
"""

import os
import time
import requests
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class AvatarGenerator:
    """
    Generate talking avatar videos using D-ID API
    Alternative to Sora (which is not yet publicly available)
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("DID_API_KEY")
        if not self.api_key:
            raise ValueError("D-ID API key not found. Please set DID_API_KEY in .env file")

        self.base_url = "https://api.d-id.com"
        self.headers = {
            "Authorization": f"Basic {self.api_key}",
            "Content-Type": "application/json"
        }

    def create_avatar_video(
        self,
        audio_path: str,
        output_path: str,
        presenter_id: str = "amy-jcwCkr1grs",  # Default presenter
        driver_id: str = "Vcq0R4a8F0"  # Default driver for expressions
    ) -> str:
        """
        Create a talking avatar video from audio file

        Args:
            audio_path: Path to the audio file (MP3, WAV)
            output_path: Where to save the generated avatar video
            presenter_id: D-ID presenter ID (different avatars available)
            driver_id: Expression driver ID

        Returns:
            Path to the generated video file
        """

        # Step 1: Upload audio file
        print("📤 Uploading audio to D-ID...")
        audio_url = self._upload_audio(audio_path)

        # Step 2: Create talking video
        print("🎭 Creating avatar video...")
        video_url = self._create_talk(audio_url, presenter_id, driver_id)

        # Step 3: Download the video
        print("⬇️ Downloading avatar video...")
        self._download_video(video_url, output_path)

        print(f"✅ Avatar video saved to {output_path}")
        return output_path

    def _upload_audio(self, audio_path: str) -> str:
        """Upload audio file to D-ID and get URL"""
        with open(audio_path, 'rb') as audio_file:
            files = {'audio': audio_file}
            response = requests.post(
                f"{self.base_url}/audios",
                headers={"Authorization": f"Basic {self.api_key}"},
                files=files
            )

            if response.status_code != 201:
                raise Exception(f"Failed to upload audio: {response.text}")

            return response.json()['url']

    def _create_talk(self, audio_url: str, presenter_id: str, driver_id: str) -> str:
        """Create talking video using D-ID API"""
        payload = {
            "source_url": f"https://d-id-public-bucket.s3.amazonaws.com/alice.jpg",  # Default avatar image
            "script": {
                "type": "audio",
                "audio_url": audio_url
            },
            "config": {
                "driver_expressions": {
                    "expressions": [
                        {"start_frame": 0, "expression": "happy", "intensity": 0.5}
                    ]
                },
                "stitch": True  # Smooth stitching
            }
        }

        response = requests.post(
            f"{self.base_url}/talks",
            headers=self.headers,
            json=payload
        )

        if response.status_code not in [200, 201]:
            raise Exception(f"Failed to create talk: {response.text}")

        talk_id = response.json()['id']

        # Poll for completion
        return self._wait_for_completion(talk_id)

    def _wait_for_completion(self, talk_id: str, max_wait: int = 300) -> str:
        """Wait for video generation to complete"""
        start_time = time.time()

        while time.time() - start_time < max_wait:
            response = requests.get(
                f"{self.base_url}/talks/{talk_id}",
                headers=self.headers
            )

            if response.status_code != 200:
                raise Exception(f"Failed to get status: {response.text}")

            data = response.json()
            status = data.get('status')

            if status == 'done':
                return data['result_url']
            elif status == 'error':
                raise Exception(f"Video generation failed: {data.get('error')}")

            print(f"Status: {status}... waiting")
            time.sleep(5)

        raise TimeoutError("Video generation timed out")

    def _download_video(self, video_url: str, output_path: str):
        """Download the generated video"""
        response = requests.get(video_url, stream=True)

        if response.status_code != 200:
            raise Exception(f"Failed to download video: {response.status_code}")

        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)


def overlay_avatar_on_video(
    main_video: str,
    avatar_video: str,
    output_path: str,
    position: str = "bottom-right",
    size: float = 0.35  # 35% of main video height (increased from 25%)
) -> str:
    """
    Overlay avatar video on the main educational video

    Args:
        main_video: Path to main video (Manim animation)
        avatar_video: Path to avatar talking head video
        output_path: Output path for final video
        position: Where to place avatar (bottom-right, bottom-left, top-right, top-left)
        size: Size of avatar relative to main video height (0.0-1.0)
    """
    import subprocess

    # Position mapping
    positions = {
        "bottom-right": "main_w-overlay_w-20:main_h-overlay_h-20",
        "bottom-left": "20:main_h-overlay_h-20",
        "top-right": "main_w-overlay_w-20:20",
        "top-left": "20:20"
    }

    pos = positions.get(position, positions["bottom-right"])

    # Create filter complex for overlay
    # Scale avatar to be 25% of main video height
    filter_complex = (
        f"[1:v]scale=-1:ih*{size}[avatar];"
        f"[0:v][avatar]overlay={pos}[outv]"
    )

    # Combine videos with ffmpeg
    subprocess.run([
        "ffmpeg",
        "-i", main_video,
        "-i", avatar_video,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", "0:a",  # Use audio from main video
        "-c:v", "libx264",
        "-c:a", "aac",
        "-shortest",  # End when shortest input ends
        "-y",
        output_path
    ], check=True)

    return output_path


# Simple fallback: Use OpenAI DALL-E + static image animation
class SimpleAvatarGenerator:
    """
    Fallback avatar generator using static image with simple animations
    Uses OpenAI DALL-E to generate avatar image
    """

    def __init__(self, openai_api_key: Optional[str] = None):
        from openai import OpenAI
        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)

    def create_avatar_image(self, output_path: str, style: str = "professional") -> str:
        """Generate a static avatar image using DALL-E"""

        prompts = {
            "professional": "A friendly professional teacher avatar, front-facing portrait, neutral background, photorealistic, high quality",
            "cartoon": "A friendly cartoon teacher character, front-facing, colorful, animated style",
            "minimal": "A simple, minimalist avatar icon of a teacher, clean design, professional"
        }

        prompt = prompts.get(style, prompts["professional"])

        response = self.client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )

        image_url = response.data[0].url

        # Download the image
        import requests
        img_response = requests.get(image_url)
        with open(output_path, 'wb') as f:
            f.write(img_response.content)

        return output_path

    def create_static_avatar_video(
        self,
        avatar_image: str,
        duration: float,
        output_path: str
    ) -> str:
        """
        Create a video from static avatar image with subtle animations
        """
        import subprocess

        # Create video from image with subtle zoom animation
        subprocess.run([
            "ffmpeg",
            "-loop", "1",
            "-i", avatar_image,
            "-vf", f"scale=400:-1,zoompan=z='min(zoom+0.0005,1.05)':d={int(duration*30)}:fps=30",
            "-t", str(duration),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-y",
            output_path
        ], check=True)

        return output_path
