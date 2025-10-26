"""
Advanced Educational Video Generator with Enhanced Features
- Better timing synchronization
- Scene-by-scene breakdown
- Background music support
- Subtitle generation
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from openai import OpenAI
from typing import Dict, List, Tuple
import re
from dotenv import load_dotenv

load_dotenv()

# Fix encoding for Windows console to support emojis
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        # Python < 3.7
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

class AdvancedVideoGenerator:
    def __init__(self, openai_api_key: str = None, output_dir: str = "outputs"):
        
        openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=openai_api_key)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Add MiKTeX to PATH if on Windows
        if sys.platform == 'win32':
            miktex_path = r"C:\Users\loveh\AppData\Local\Programs\MiKTeX\miktex\bin\x64"
            if os.path.exists(miktex_path) and miktex_path not in os.environ.get('PATH', ''):
                os.environ['PATH'] = miktex_path + os.pathsep + os.environ.get('PATH', '')
        
    def generate_scene_breakdown(self, description: str) -> List[Dict]:
        """
        Generate a detailed scene breakdown with timing
        """
        prompt = f"""You are an educational video planner.

Given this content description:
{description}

Create a detailed scene-by-scene breakdown for a 60-90 second educational video.

For each scene, provide:
1. Scene number
2. Duration (in seconds)
3. Visual description (what should be animated)
4. Narration text (what should be said)
5. Key concepts to emphasize

Return the breakdown as a JSON array with this structure:
[
  {{
    "scene": 1,
    "duration": 10,
    "visual": "Description of what to show",
    "narration": "Text to narrate",
    "key_concepts": ["concept1", "concept2"]
  }},
  ...
]

Return ONLY valid JSON, no additional text."""

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert educational video planner."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        content = response.choices[0].message.content.strip()
        # Extract JSON from markdown code blocks if present
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        return json.loads(content)
    
    def generate_timed_manim_code(self, scenes: List[Dict]) -> str:
        """
        Generate Manim code with precise timing for each scene
        """
        scenes_description = json.dumps(scenes, indent=2)
        
        prompt = f"""You are an expert Manim programmer.

Generate complete Manim code for these timed scenes:
{scenes_description}

Requirements:
- Use Manim Community Edition syntax
- Create ONE Scene class named 'EducationalScene'
- Each scene should match the specified duration exactly using wait() or run_time parameters
- Use self.wait() between scenes for proper pacing
- Include smooth transitions between scenes
- Use engaging colors and animations
- Make sure total video length matches sum of scene durations

Important timing tips:
- Use run_time parameter in animations: self.play(FadeIn(obj), run_time=2)
- Use self.wait(duration) for pauses
- Chain animations appropriately

Return ONLY the Python code, no explanations."""

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert Manim programmer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    def generate_subtitles(self, scenes: List[Dict], output_path: str) -> str:
        """
        Generate SRT subtitle file from scene narrations
        """
        srt_content = []
        current_time = 0
        
        for i, scene in enumerate(scenes, 1):
            start_time = current_time
            end_time = current_time + scene['duration']
            
            # Format time as SRT format (HH:MM:SS,mmm)
            start_srt = self._format_srt_time(start_time)
            end_srt = self._format_srt_time(end_time)
            
            # Add subtitle entry
            srt_content.append(f"{i}")
            srt_content.append(f"{start_srt} --> {end_srt}")
            srt_content.append(scene['narration'])
            srt_content.append("")  # Blank line between entries
            
            current_time = end_time
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(srt_content))
        
        return output_path
    
    def _format_srt_time(self, seconds: float) -> str:
        """
        Convert seconds to SRT time format (HH:MM:SS,mmm)
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def generate_scene_audio_files(self, scenes: List[Dict], project_name: str) -> List[str]:
        """
        Generate separate audio files for each scene
        """
        audio_files = []
        
        for i, scene in enumerate(scenes, 1):
            audio_path = self.output_dir / f"{project_name}_scene_{i}_audio.mp3"
            
            response = self.client.audio.speech.create(
                model="tts-1-hd",
                voice="alloy",
                input=scene['narration'],
                speed=1.0
            )
            
            response.stream_to_file(str(audio_path))
            audio_files.append(str(audio_path))
        
        return audio_files
    
    def concatenate_audio_files(self, audio_files: List[str], output_path: str) -> str:
        """
        Concatenate multiple audio files into one
        """
        # Create a file list for ffmpeg
        list_file = self.output_dir / "audio_list.txt"
        with open(list_file, 'w') as f:
            for audio_file in audio_files:
                f.write(f"file '{audio_file}'\n")
        
        # Concatenate using ffmpeg
        subprocess.run([
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", str(list_file),
            "-c", "copy",
            "-y",
            output_path
        ], check=True)
        
        return output_path
    
    def add_background_music(self, video_path: str, music_path: str, output_path: str, music_volume: float = 0.1) -> str:
        """
        Add background music to the video
        """
        subprocess.run([
            "ffmpeg",
            "-i", video_path,
            "-i", music_path,
            "-filter_complex",
            f"[1:a]volume={music_volume}[music];[0:a][music]amix=inputs=2:duration=first[a]",
            "-map", "0:v",
            "-map", "[a]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-y",
            output_path
        ], check=True)
        
        return output_path
    
    def add_subtitles_to_video(self, video_path: str, subtitle_path: str, output_path: str) -> str:
        """
        Burn subtitles into the video
        """
        subprocess.run([
            "ffmpeg",
            "-i", video_path,
            "-vf", f"subtitles={subtitle_path}:force_style='FontSize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2'",
            "-c:a", "copy",
            "-y",
            output_path
        ], check=True)
        
        return output_path
    
    def render_manim_animation(self, manim_code: str, output_name: str) -> str:
        """
        Render the Manim animation
        """
        # Extract code from markdown if present
        if "```python" in manim_code:
            manim_code = manim_code.split("```python")[1].split("```")[0].strip()
        elif "```" in manim_code:
            manim_code = manim_code.split("```")[1].split("```")[0].strip()
        
        temp_file = self.output_dir / f"{output_name}_manim.py"
        
        with open(temp_file, 'w') as f:
            f.write(manim_code)
        
        try:
            subprocess.run([
                "manim",
                "-qh",
                "--format=mp4",
                "--disable_caching",
                "--media_dir", str(self.output_dir / "manim_media"),
                str(temp_file),
                "EducationalScene"
            ], capture_output=True, text=True, check=True)
            
            video_dir = self.output_dir / "manim_media" / "videos" / f"{output_name}_manim" / "1080p60"
            video_file = video_dir / "EducationalScene.mp4"
            
            if video_file.exists():
                return str(video_file)
            else:
                raise FileNotFoundError(f"Video not found at {video_file}")
                
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Manim rendering failed: {e.stderr}")
    
    def sync_video_and_audio(self, video_path: str, audio_path: str, output_path: str) -> str:
        """
        Combine video and audio with speed adjustment
        """
        # Get durations
        audio_duration = self._get_duration(audio_path)
        video_duration = self._get_duration(video_path)
        
        speed_factor = video_duration / audio_duration
        
        print(f"Audio duration: {audio_duration:.2f}s")
        print(f"Video duration: {video_duration:.2f}s")
        print(f"Speed adjustment: {speed_factor:.2f}x")
        
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
    
    def _get_duration(self, file_path: str) -> float:
        """
        Get duration of media file
        """
        result = subprocess.run([
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            file_path
        ], capture_output=True, text=True)
        
        return float(result.stdout.strip())
    
    def generate_video(self, description: str, project_name: str = "educational_video", 
                      add_subtitles: bool = True) -> Dict[str, str]:
        """
        Complete advanced workflow
        """
        print(f"🎬 Starting advanced video generation: {project_name}")
        print(f"📝 Description: {description}\n")
        
        # Step 1: Generate scene breakdown
        print("1️⃣ Generating scene breakdown...")
        scenes = self.generate_scene_breakdown(description)
        scenes_file = self.output_dir / f"{project_name}_scenes.json"
        with open(scenes_file, 'w') as f:
            json.dump(scenes, f, indent=2)
        print(f"✅ {len(scenes)} scenes planned\n")
        
        # Step 2: Generate timed Manim code
        print("2️⃣ Generating timed Manim animation code...")
        manim_code = self.generate_timed_manim_code(scenes)
        manim_file = self.output_dir / f"{project_name}_manim.py"
        with open(manim_file, 'w') as f:
            f.write(manim_code)
        print(f"✅ Manim code saved\n")
        
        # Step 3: Generate audio for each scene
        print("3️⃣ Generating narration audio...")
        audio_files = self.generate_scene_audio_files(scenes, project_name)
        
        # Concatenate audio files
        full_audio = self.output_dir / f"{project_name}_audio.mp3"
        self.concatenate_audio_files(audio_files, str(full_audio))
        print(f"✅ Audio generated\n")
        
        # Step 4: Generate subtitles
        subtitle_file = None
        if add_subtitles:
            print("4️⃣ Generating subtitles...")
            subtitle_file = self.output_dir / f"{project_name}_subtitles.srt"
            self.generate_subtitles(scenes, str(subtitle_file))
            print(f"✅ Subtitles generated\n")
        
        # Step 5: Render animation
        print("5️⃣ Rendering Manim animation...")
        animation_video = self.render_manim_animation(manim_code, project_name)
        print(f"✅ Animation rendered\n")
        
        # Step 6: Sync video and audio
        print("6️⃣ Syncing animation with audio...")
        synced_video = self.output_dir / f"{project_name}_synced.mp4"
        self.sync_video_and_audio(animation_video, str(full_audio), str(synced_video))
        print(f"✅ Video synced\n")
        
        # Step 7: Add subtitles if requested
        final_video = synced_video
        if add_subtitles and subtitle_file:
            print("7️⃣ Adding subtitles to video...")
            final_video = self.output_dir / f"{project_name}_final.mp4"
            self.add_subtitles_to_video(str(synced_video), str(subtitle_file), str(final_video))
            print(f"✅ Subtitles added\n")
        
        print("🎉 Advanced video generation complete!")
        
        return {
            "scenes": str(scenes_file),
            "manim_code": str(manim_file),
            "audio": str(full_audio),
            "subtitles": str(subtitle_file) if subtitle_file else None,
            "animation": animation_video,
            "final_video": str(final_video)
        }


def main():
    """
    Example usage of advanced generator
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Please set OPENAI_API_KEY environment variable")
    
    generator = AdvancedVideoGenerator(api_key)
    
    description = """
    Explain how photosynthesis works in plants. Show:
    1. Sunlight hitting a leaf
    2. Chloroplasts absorbing light
    3. Water and CO2 being converted to glucose and oxygen
    4. The chemical equation
    Make it colorful and engaging for high school students.
    """
    
    results = generator.generate_video(
        description, 
        "photosynthesis_explained",
        add_subtitles=True
    )
    
    print("\n📦 Generated files:")
    for key, path in results.items():
        if path:
            print(f"  {key}: {path}")


if __name__ == "__main__":
    main()
