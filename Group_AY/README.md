# AI Educational Video Generator

An automated workflow that transforms natural language descriptions into complete educational videos with animations, narration, and synchronization.

## Problem Statement

Creating high-quality educational videos with synchronized visuals, narration, and animations typically requires expertise in scripting, video editing, and animation software. This process is time-consuming, costly, and inaccessible to most educators and learners who lack technical or design skills. The challenge is to develop an **AI-driven system** that can automatically generate complete educational videos from simple natural language input — including **animated visualizations**, **AI-generated scripts**, **text-to-speech narration**, and **scene synchronization** — making the content creation process faster, more affordable, and more scalable.

## Features

- **Natural Language Input**: Describe your educational content in plain English
- **Manim Animations**: Automatically generates mathematical and visual animations
- **AI Script Generation**: Creates engaging narration scripts
- **Text-to-Speech**: Converts scripts to natural-sounding speech
- **Auto-Synchronization**: Syncs animation timing with narration
- **Subtitle Generation**: Optional subtitle overlay
- **Scene-by-Scene Control**: Advanced version with precise timing control
- **REST API**: HTTP API for integration with other services

## Prerequisites

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

## Architecture

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

---

