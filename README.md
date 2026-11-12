# Jakarta What If — Stylized Realistic 3D

## GitHub Actions render (Blender 5 compatible)
1. Upload the contents of this folder to the root of a GitHub repository.
2. Open **Actions** → **Render Jakarta What If** → **Run workflow**.
3. Download the `jakarta-whatif-video` artifact when the job succeeds.

Blender renders a numbered PNG image sequence first. FFmpeg then encodes the frames into H.264 MP4 and adds `assets/voiceover.mp3`. This avoids Blender's optional built-in FFmpeg video-output support, which is absent in some Blender 5 Linux builds.

Output: `output/jakarta_whatif.mp4` (vertical 1080×1920, 30 FPS).
