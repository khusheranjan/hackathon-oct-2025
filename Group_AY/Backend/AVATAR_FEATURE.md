# Avatar Feature Documentation

## Overview
You can now add an AI-generated avatar in the corner of your educational videos, similar to YouTube lecture videos! The avatar appears in a small window and can explain concepts while the Manim animation plays.

## Two Avatar Options

### 1. Simple Avatar (Default) ✨
- Uses OpenAI's DALL-E to generate a professional avatar image
- Creates a static avatar with subtle zoom animation
- **No additional API keys required** (uses your existing OpenAI key)
- Recommended for quick setup

### 2. Advanced Talking Avatar (Optional) 🎭
- Uses D-ID API to create realistic talking head videos
- Avatar lips sync with the narration
- Requires D-ID API key (get one at https://www.d-id.com/)
- More realistic but requires additional setup

## How to Use

### API Request Format

```json
POST http://localhost:5000/api/generate

{
  "description": "Explain the Pythagorean theorem with visual examples",
  "project_name": "pythagorean_lesson",
  "add_avatar": true,
  "avatar_position": "bottom-right",
  "use_simple_avatar": true
}
```

### Parameters

- **add_avatar** (boolean): Set to `true` to enable avatar feature
- **avatar_position** (string): Position of avatar
  - `"bottom-right"` (default)
  - `"bottom-left"`
  - `"top-right"`
  - `"top-left"`
- **use_simple_avatar** (boolean):
  - `true` = Use simple DALL-E avatar (default, no extra setup)
  - `false` = Use D-ID talking avatar (requires D-ID API key)

## Setup Instructions

### For Simple Avatar (No Extra Setup)
1. Just set `add_avatar: true` in your API request
2. The system will use your existing OpenAI API key
3. Done! 🎉

### For Advanced Talking Avatar
1. Sign up at https://www.d-id.com/ and get an API key
2. Add to your `.env` file:
   ```
   DID_API_KEY=your_did_api_key_here
   ```
3. Set `use_simple_avatar: false` in your API request
4. Rebuild Docker container:
   ```bash
   cd Backend
   docker-compose down
   docker-compose up -d --build
   ```

## Examples

### Example 1: Simple Avatar (Quick Start)
```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Teach the concept of gravity with examples",
    "add_avatar": true,
    "use_simple_avatar": true
  }'
```

### Example 2: Talking Avatar (Advanced)
```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Explain photosynthesis step by step",
    "add_avatar": true,
    "use_simple_avatar": false,
    "avatar_position": "bottom-left"
  }'
```

### Example 3: No Avatar (Original Behavior)
```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Demonstrate the water cycle",
    "add_avatar": false
  }'
```

## Technical Details

### What Happens Behind the Scenes

1. **Video Generation**: Manim creates the educational animation
2. **Narration**: ElevenLabs generates voiceover
3. **Avatar Creation**:
   - Simple: DALL-E generates avatar image → FFmpeg creates video with subtle animation
   - Advanced: D-ID creates talking head video from audio
4. **Video Compositing**: FFmpeg overlays avatar video on main video
5. **Output**: Final video with avatar in corner

### File Structure
```
outputs/
  {job_id}/
    {project_name}_avatar.png          # Generated avatar image (simple mode)
    {project_name}_avatar_video.mp4    # Avatar video
    {project_name}_synced.mp4          # Main video without avatar
    {project_name}_final.mp4           # Final video with avatar
```

## Troubleshooting

### Avatar generation fails
- **Simple Mode**: Check that your OpenAI API key has access to DALL-E 3
- **Advanced Mode**: Verify your D-ID API key is correct in `.env`

### Avatar appears too large/small
- Avatar size is set to 25% of video height by default
- Modify `size` parameter in `overlay_avatar_on_video()` function in `avatar_generator.py`

### Video sync issues
- The avatar video duration matches the audio duration automatically
- If issues persist, check FFmpeg logs in Docker container

## Cost Considerations

### Simple Avatar
- ~$0.04 per image (DALL-E 3 standard quality)
- Very cost-effective

### Advanced Talking Avatar (D-ID)
- Check D-ID pricing at https://www.d-id.com/pricing/
- Typically ~$0.03-0.05 per video second
- More expensive but more realistic

## Future Enhancements
- [ ] Multiple avatar styles (teacher, scientist, cartoon character)
- [ ] Custom avatar upload support
- [ ] Avatar gestures and expressions
- [ ] Multiple avatars for dialogue-style teaching

---

**Note**: Sora (OpenAI's text-to-video model) is not yet publicly available. We use D-ID as the best alternative for realistic talking avatars.
