"""
AI Educational Video Generator
Orchestrates the complete workflow from description to final video
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from openai import OpenAI
from elevenlabs import ElevenLabs
from typing import Dict, List
import tempfile
import shutil
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fix encoding for Windows console to support emojis
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        # Python < 3.7
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

class EducationalVideoGenerator:
    def __init__(self, openai_api_key: str = None, elevenlabs_api_key: str = None, output_dir: str = "outputs"):
        # Load API keys from environment if not provided
        openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        elevenlabs_api_key = elevenlabs_api_key or os.getenv("ELEVENLABS_API_KEY")

        if not openai_api_key:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY in .env file or pass it as parameter.")
        if not elevenlabs_api_key:
            raise ValueError("ElevenLabs API key not found. Please set ELEVENLABS_API_KEY in .env file or pass it as parameter.")

        self.client = OpenAI(api_key=openai_api_key)
        self.elevenlabs_client = ElevenLabs(api_key=elevenlabs_api_key)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Add MiKTeX to PATH if on Windows
        if sys.platform == 'win32':
            miktex_path = r"C:\Users\loveh\AppData\Local\Programs\MiKTeX\miktex\bin\x64"
            if os.path.exists(miktex_path) and miktex_path not in os.environ.get('PATH', ''):
                os.environ['PATH'] = miktex_path + os.pathsep + os.environ.get('PATH', '')
        
    def generate_manim_code(self, description: str) -> str:
        """
        Step 1: Generate Manim animation code from natural language description
        """
        prompt = f"""You are an expert Manim (Mathematical Animation Engine) programmer.

Given this educational content description:
{description}

Generate complete, executable Manim code that creates an engaging 60-90 second animation for this content.

CRITICAL REQUIREMENTS:
- Use Manim Community Edition v0.19+ syntax (NOT old manim!)
- Create a single Scene class named 'EducationalScene'
- The animation MUST be 60-90 seconds long total
- Use self.wait() liberally between animations (2-4 seconds per pause)
- Use run_time parameters to make animations slower (2-5 seconds each)
- Show each concept for at least 5-10 seconds before moving on
- Include smooth transitions and animations
- Use appropriate colors, text sizes, and positioning
- Add visual elements that enhance understanding
- Code should be self-contained and runnable
- DO NOT rush - make the animation slow and clear for educational purposes
- Use Create() NOT ShowCreation()
- Use Write() for text, FadeIn() for objects
- Use Text() for regular text, MathTex() for ALL math formulas (equations, variables with superscripts/subscripts)
- NEVER use Tex() for mathematical expressions - always use MathTex() for formulas
- Use regular Tex() only for plain text without math symbols
- Available shapes: Circle, Square, Rectangle, Triangle, Polygon, Line, Arrow

Example of proper timing:
```python
# Show text for 5 seconds
self.play(Write(text), run_time=3)
self.wait(2)

# Transform slowly
self.play(Transform(obj1, obj2), run_time=4)
self.wait(3)
```

Return ONLY the Python code, no explanations or instructions whatsoever."""

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert Manim programmer who creates clear, educational animations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip().replace("```python", "").replace("```", "")
    
    def generate_script(self, description: str, manim_code: str) -> str:
        """
        Step 2: Generate narration script that matches the animation
        """
        prompt = f"""You are a skilled educational content writer.

Given this content description:
{description}

And this Manim animation code:
{manim_code}

Write a clear, engaging narration script that:
- Explains the concept step by step
- Syncs with the animation timing
- Uses simple, accessible language
- Is approximately 60-90 seconds long
- Includes natural pauses where appropriate

Return ONLY the script text, no stage directions or timestamps."""

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert educational content writer who creates clear, engaging scripts."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    def generate_audio(self, script: str, output_path: str) -> str:
        """
        Step 3: Convert script to speech using ElevenLabs TTS
        """
        # Generate audio using ElevenLabs
        audio = self.elevenlabs_client.text_to_speech.convert(
            voice_id="EXAVITQu4vr4xnSDxMaL",  # Rachel voice ID
            text=script,
            model_id="eleven_multilingual_v2"
        )

        # Save audio to file
        with open(output_path, 'wb') as f:
            for chunk in audio:
                f.write(chunk)

        return output_path
    
    def render_manim_animation(self, manim_code: str, output_name: str) -> str:
        """
        Step 4: Render the Manim animation to video
        """
        # Create temporary Python file with the Manim code
        temp_file = self.output_dir / f"{output_name}_manim.py"
        
        with open(temp_file, 'w') as f:
            f.write(manim_code)
        
        # Render with Manim using Docker
        try:
            # Get absolute paths
            work_dir = Path.cwd()
            abs_temp_file = temp_file.resolve()
            abs_media_dir = (self.output_dir / "manim_media").resolve()
            rel_temp_file = abs_temp_file.relative_to(work_dir)
            rel_media_dir = abs_media_dir.relative_to(work_dir)

            # Convert Windows paths to POSIX (forward slashes) for Docker
            rel_temp_file_posix = rel_temp_file.as_posix()
            rel_media_dir_posix = rel_media_dir.as_posix()

            # Set environment to prevent Git Bash path conversion on Windows
            env = os.environ.copy()
            env['MSYS_NO_PATHCONV'] = '1'

            result = subprocess.run([
                "docker", "run", "--rm",
                "-v", f"{work_dir}:/manim",
                "-w", "/manim",
                "ai-video-generator:latest",
                "manim",
                "-qh",  # High quality
                "--format=mp4",
                "--media_dir", rel_media_dir_posix,
                rel_temp_file_posix,
                "EducationalScene"
            ], capture_output=True, text=True, encoding='utf-8', errors='replace',
               env=env, check=True)
            
            # Find the generated video
            video_dir = self.output_dir / "manim_media" / "videos" / f"{output_name}_manim" / "1080p60"
            video_file = video_dir / "EducationalScene.mp4"
            
            if video_file.exists():
                return str(video_file)
            else:
                raise FileNotFoundError(f"Manim video not found at {video_file}")
                
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Manim rendering failed: {e.stderr}")
    
    def get_audio_duration(self, audio_path: str) -> float:
        """
        Get duration of audio file using ffprobe
        """
        result = subprocess.run([
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            audio_path
        ], capture_output=True, text=True)
        
        return float(result.stdout.strip())
    
    def sync_video_and_audio(self, video_path: str, audio_path: str, output_path: str) -> str:
        """
        Step 5: Combine animation and narration, adjusting video speed to match audio
        """
        # Get audio duration
        audio_duration = self.get_audio_duration(audio_path)

        # Get video duration
        video_result = subprocess.run([
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path
        ], capture_output=True, text=True)
        video_duration = float(video_result.stdout.strip())

        print(f"Audio duration: {audio_duration:.2f}s")
        print(f"Video duration: {video_duration:.2f}s")

        # Calculate speed adjustment factor
        # For setpts: >1.0 slows down, <1.0 speeds up
        # We need to stretch/compress video to match audio duration
        speed_factor = audio_duration / video_duration

        # If video needs to be slowed down more than 3x, loop it instead
        if speed_factor > 3.0:
            print(f"Warning: Video too short ({speed_factor:.2f}x). Looping video to match audio length.")
            # Calculate how many loops needed
            loops = int(audio_duration / video_duration) + 1

            # Create a looped video first
            temp_looped = output_path.replace('.mp4', '_temp_looped.mp4')
            subprocess.run([
                "ffmpeg",
                "-stream_loop", str(loops),
                "-i", video_path,
                "-t", str(audio_duration),
                "-c:v", "libx264",
                "-y",
                temp_looped
            ], check=True)

            # Now combine looped video with audio
            subprocess.run([
                "ffmpeg",
                "-i", temp_looped,
                "-i", audio_path,
                "-c:v", "copy",
                "-c:a", "aac",
                "-shortest",
                "-y",
                output_path
            ], check=True)

            # Clean up temp file
            import os
            os.remove(temp_looped)
        else:
            # Normal case: adjust video speed
            if speed_factor > 2.0 or speed_factor < 0.5:
                print(f"Warning: Significant speed adjustment ({speed_factor:.2f}x)")

            # Combine video and audio with speed adjustment
            subprocess.run([
                "ffmpeg",
                "-i", video_path,
                "-i", audio_path,
                "-filter_complex",
                f"[0:v]setpts={speed_factor}*PTS[v]",
                "-map", "[v]",
                "-map", "1:a",
                "-c:v", "libx264",
                "-c:a", "aac",
                "-shortest",
                "-y",
                output_path
            ], check=True)

        return output_path
    
    def generate_video(self, description: str, project_name: str = "educational_video") -> Dict[str, str]:
        """
        Complete workflow: description -> final video
        """
        print(f"🎬 Starting video generation for: {project_name}")
        print(f"📝 Description: {description}\n")
        
        # Step 1: Generate Manim code
        print("1️⃣ Generating Manim animation code...")
        manim_code = self.generate_manim_code(description)
        manim_file = self.output_dir / f"{project_name}_manim.py"
        with open(manim_file, 'w') as f:
            f.write(manim_code)
        print(f"✅ Manim code saved to {manim_file}\n")
        
        # Step 2: Generate script
        print("2️⃣ Generating narration script...")
        script = self.generate_script(description, manim_code)
        script_file = self.output_dir / f"{project_name}_script.txt"
        with open(script_file, 'w') as f:
            f.write(script)
        print(f"✅ Script saved to {script_file}\n")
        
        # Step 3: Generate audio
        print("3️⃣ Converting script to speech...")
        audio_file = self.output_dir / f"{project_name}_audio.mp3"
        self.generate_audio(script, str(audio_file))
        print(f"✅ Audio saved to {audio_file}\n")
        
        # Step 4: Render Manim animation
        print("4️⃣ Rendering Manim animation (this may take a while)...")
        video_file = self.render_manim_animation(manim_code, project_name)
        print(f"✅ Animation rendered to {video_file}\n")
        
        # Step 5: Sync video and audio
        print("5️⃣ Syncing animation with narration...")
        final_video = self.output_dir / f"{project_name}_final.mp4"
        self.sync_video_and_audio(video_file, str(audio_file), str(final_video))
        print(f"✅ Final video saved to {final_video}\n")
        
        print("🎉 Video generation complete!")
        
        return {
            "manim_code": str(manim_file),
            "script": str(script_file),
            "audio": str(audio_file),
            "animation": video_file,
            "final_video": str(final_video)
        }


def main():
    """
    Example usage
    """
    # Set your OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Please set OPENAI_API_KEY environment variable")
    
    # Initialize generator
    generator = EducationalVideoGenerator(api_key)
    
    # Example: Generate video about the Pythagorean theorem
    description = """
    Explain the Pythagorean theorem (a² + b² = c²) visually.
    Show a right triangle, label the sides, and demonstrate how
    the squares of the two shorter sides equal the square of the hypotenuse.
    Use colors to make it engaging and include a simple example with numbers.
    """
    
    # Generate the complete video
    results = generator.generate_video(description, "pythagorean_theorem")
    
    print("\n📦 Generated files:")
    for key, path in results.items():
        print(f"  {key}: {path}")


if __name__ == "__main__":
    main()
