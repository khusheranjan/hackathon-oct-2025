# AI Educational Video Generator

An automated workflow that transforms natural language descriptions into complete educational videos with animations, narration, and synchronization.

## 🌟 Features

- **Natural Language Input**: Describe your educational content in plain English
- **Manim Animations**: Automatically generates mathematical and visual animations
- **AI Script Generation**: Creates engaging narration scripts
- **Text-to-Speech**: Converts scripts to natural-sounding speech
- **Auto-Synchronization**: Syncs animation timing with narration
- **Subtitle Generation**: Optional subtitle overlay
- **Scene-by-Scene Control**: Advanced version with precise timing control
- **REST API**: HTTP API for integration with other services

## 📋 Prerequisites

### System Requirements
- Python 3.8+
- FFmpeg (for video processing)
- LaTeX (for Manim mathematical rendering)
- OpenAI API key

### Installation

1. **Install System Dependencies**

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y ffmpeg texlive texlive-latex-extra texlive-fonts-extra texlive-science

# macOS
brew install ffmpeg
brew install --cask mactex

# Windows
# Download and install FFmpeg from https://ffmpeg.org/download.html
# Download and install MiKTeX from https://miktex.org/download
```

2. **Install Python Dependencies**

```bash
pip install -r requirements.txt --break-system-packages
```

3. **Set OpenAI API Key**

```bash
export OPENAI_API_KEY='your-api-key-here'
```

## 🚀 Quick Start

### Basic Usage

```python
from video_generator import EducationalVideoGenerator

# Initialize with your API key
generator = EducationalVideoGenerator(
    openai_api_key="your-api-key"
)

# Describe your educational content
description = """
Explain the concept of compound interest.
Show how money grows over time with a visual graph.
Include the formula A = P(1 + r/n)^(nt) and a concrete example.
"""

# Generate the complete video
results = generator.generate_video(
    description=description,
    project_name="compound_interest"
)

print(f"Video ready: {results['final_video']}")
```

### Command Line Usage

```bash
python video_generator.py
```

## 🔧 Advanced Features

### Scene-by-Scene Generation

For more control over timing and content:

```python
from advanced_generator import AdvancedVideoGenerator

generator = AdvancedVideoGenerator(
    openai_api_key="your-api-key"
)

description = """
Explain Newton's Laws of Motion:
1. First law (inertia)
2. Second law (F=ma)
3. Third law (action-reaction)
Use real-world examples for each law.
"""

results = generator.generate_video(
    description=description,
    project_name="newtons_laws",
    add_subtitles=True  # Enable subtitles
)
```

### Using the REST API

1. **Start the API Server**

```bash
python api_server.py
```

2. **Submit a Video Generation Request**

```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Explain the water cycle with diagrams",
    "project_name": "water_cycle",
    "openai_api_key": "your-api-key"
  }'
```

Response:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "message": "Video generation started"
}
```

3. **Check Status**

```bash
curl http://localhost:5000/api/status/550e8400-e29b-41d4-a716-446655440000
```

4. **Download Video**

```bash
curl -o video.mp4 http://localhost:5000/api/download/550e8400-e29b-41d4-a716-446655440000
```

## 🏗️ Architecture

### Workflow Pipeline

```
User Input (Natural Language)
         ↓
    [OpenAI GPT-4]
         ↓
   Manim Code Generation
         ↓
   Script Generation
         ↓
   [OpenAI TTS]
         ↓
    Audio Generation
         ↓
   [Manim Renderer]
         ↓
  Animation Rendering
         ↓
    [FFmpeg]
         ↓
  Video-Audio Sync
         ↓
   Final Video Output
```

### Component Breakdown

1. **Manim Code Generator** (`generate_manim_code`)
   - Converts description to Manim animation code
   - Uses GPT-4 to understand visual requirements
   - Generates executable Python code

2. **Script Generator** (`generate_script`)
   - Creates narration that matches animation
   - Considers timing and pacing
   - Educational and engaging tone

3. **Audio Generator** (`generate_audio`)
   - Uses OpenAI TTS (Text-to-Speech)
   - High-quality voice synthesis
   - Natural-sounding narration

4. **Manim Renderer** (`render_manim_animation`)
   - Executes Manim code
   - Renders high-quality animations
   - Outputs 1080p60 video

5. **Synchronizer** (`sync_video_and_audio`)
   - Adjusts video speed to match audio length
   - Combines animation and narration
   - Produces final output

## 📁 Project Structure

```
.
├── video_generator.py      # Basic video generator
├── advanced_generator.py   # Advanced with scene control
├── api_server.py           # Flask REST API
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── outputs/               # Generated videos (created automatically)
    ├── {project_name}_manim.py
    ├── {project_name}_script.txt
    ├── {project_name}_audio.mp3
    ├── {project_name}_animation.mp4
    └── {project_name}_final.mp4
```

## 🎨 Customization Options

### Voice Selection

Change the TTS voice in the generator:

```python
# Available voices: alloy, echo, fable, onyx, nova, shimmer
response = self.client.audio.speech.create(
    model="tts-1-hd",
    voice="nova",  # Change this
    input=script
)
```

### Video Quality

Adjust Manim rendering quality:

```python
# Options: -ql (low), -qm (medium), -qh (high), -qk (4K)
subprocess.run([
    "manim",
    "-qk",  # 4K quality
    "--format=mp4",
    # ... rest of command
])
```

### Animation Style

Customize the Manim generation prompt to control style:

```python
prompt = f"""
Generate Manim code with:
- Dark background theme
- Bright, contrasting colors
- Minimal text, focus on visuals
- Smooth, slow transitions

{description}
"""
```

## 🐛 Troubleshooting

### Common Issues

1. **Manim not found**
   ```bash
   # Ensure Manim is in PATH
   which manim
   # Reinstall if needed
   pip install manim --break-system-packages
   ```

2. **LaTeX errors in Manim**
   ```bash
   # Install complete LaTeX distribution
   sudo apt install texlive-full
   ```

3. **FFmpeg errors**
   ```bash
   # Verify FFmpeg installation
   ffmpeg -version
   ```

4. **OpenAI API errors**
   - Check API key is set correctly
   - Verify you have API credits
   - Check rate limits

### Debug Mode

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 💡 Usage Tips

### Best Practices for Descriptions

1. **Be Specific**: Include what visuals you want
   ```
   ✅ "Show a red triangle rotating 360 degrees"
   ❌ "Show a shape"
   ```

2. **Structure Your Content**: Break into logical sections
   ```
   "First, introduce the concept.
    Then, show the formula with an example.
    Finally, summarize the key points."
   ```

3. **Mention Colors/Styles**: Guide the visual design
   ```
   "Use blue for positive numbers and red for negative.
    Include a graph with smooth curves."
   ```

4. **Specify Duration**: Help with pacing
   ```
   "Create a 60-second video explaining..."
   ```

### Optimizing Generation Time

- Use `gpt-3.5-turbo` for faster (but less accurate) generation
- Reduce video quality for drafts (`-ql` flag)
- Cache Manim scenes when iterating
- Generate audio separately and reuse

## 🔐 Security Notes

- Never commit your OpenAI API key
- Use environment variables for sensitive data
- Implement rate limiting for production API
- Validate user inputs to prevent code injection
- Run in isolated containers for multi-tenant use

## 📊 Performance

Typical generation times:
- Manim code generation: 10-30 seconds
- Script generation: 5-15 seconds
- Audio generation: 5-10 seconds
- Manim rendering: 30-180 seconds (varies by complexity)
- Video synchronization: 5-15 seconds

**Total: 1-5 minutes per video**

## 🛣️ Roadmap

- [ ] Support for multiple animation engines (Three.js, D3.js)
- [ ] Background music generation
- [ ] Interactive quiz overlays
- [ ] Multi-language support
- [ ] Real-time preview during generation
- [ ] Template library for common topics
- [ ] Batch processing for curriculum creation
- [ ] Integration with LMS platforms

## 📝 License

MIT License - feel free to use and modify for your projects.

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Better timing synchronization algorithms
- More animation templates
- Enhanced error handling
- Performance optimizations
- Additional TTS voice options
- Custom background music integration

## 📞 Support

For issues and questions:
- GitHub Issues: [Create an issue](#)
- Documentation: [Read the docs](#)
- Examples: See `examples/` directory

## 🙏 Acknowledgments

- **Manim Community**: For the amazing animation engine
- **OpenAI**: For GPT-4 and TTS capabilities
- **FFmpeg**: For video processing
- **3Blue1Brown**: For inspiring educational content

---

Made with ❤️ for educators and content creators
