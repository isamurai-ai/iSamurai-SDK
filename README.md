# iSamurai Python SDK

The official Python client for the [iSamurai Face Swap Platform](https://isamur.ai).

[Documentation](https://isamur.ai/documentation) | [Face Swap](https://isamur.ai/face-swap) | [Slow Motion](https://isamur.ai/slowmotion) | [Blog](https://isamur.ai/blog) | [Community](https://www.reddit.com/r/iSamurai_FaceSwap/)

---

## 🚀 Overview

The **iSamurai SDK** provides a complete pythonic interface for all iSamurai AI tools:
*   **Face Swap**: Single and Multi-face processing.
*   **Media Tools**: Slow Motion interpolation and Image Restoration.
*   **Gallery**: Asset management for heavy workload optimization.
*   **Utilities**: Automatic Polling and Error Handling.

## 🛠️ Installation

```bash
pip install git+https://github.com/isamurai-ai/iSamurai-SDK.git
```

## 🔐 Authentication

Generate your key in your [Developer Profile](https://isamur.ai/profile).

```python
from isamurai import Isamurai

client = Isamurai(api_key="isk_YOUR_API_KEY")
```

---

## 🎭 Face Swap

### Quick Preview
Generate a single-frame preview before burning credits on a full video.

```python
# Returns base64 image dict
preview = client.create_preview(
    source_path="face.jpg", 
    target_path="video_frame.jpg"
)
```

### Full Video Processing
Process high-quality video swaps (up to 1080p).

```python
job_id = client.process_face_swap(
    source_path="face.jpg",
    target_path="movie.mp4",
    quality="1080p",
    enhance=True
)

# Wait for result
result = client.wait_for_job(job_id)
print(result['output_media_url'])
```

### Multi-Face Swap
Swap multiple faces in the same scene.

1.  **Analyze Frame**: Detect faces in the target video.
2.  **Map Faces**: Assign source images to detected people.
3.  **Process**: Submit the mapping.

```python
# 1. Detect faces
faces = client.analyze_frame("target_frame.jpg")
print(f"Found {len(faces)} faces")

# 2. Create mapping (analysis_results)
# Assign a source image base64 to each detected face you want to swap
mapping = []
for face in faces:
    # Example: Swap every face with 'my_face.jpg'
    face['source_image'] = client._to_base64("my_face.jpg")
    mapping.append(face)

# 3. Process
job_id = client.process_multi_face_swap("movie.mp4", mapping)
result = client.wait_for_job(job_id, multi=True)
```

---

## ⏱️ Slow Motion & FPS Boost
Create cinematic slow motion (up to 8x) from standard footage.

```python
# 1. Create Project
project_id = client.create_slow_motion(
    video_path="action.mp4",
    slowdown_factor=4,   # 2x, 4x, 8x
    mode="slowmo"        # 'slowmo' (slower) or 'fps' (smoother)
)

# 2. Start Processing
client.process_slow_motion(project_id)

# 3. Monitor
# Use API endpoint directly or custom polling for slowmo
```

---

## ✨ Image Restoration
Restore old photos or enhance low-quality faces.

```python
result = client.restore_image("old_photo.jpg", mode="restore")
print(result['url'])
```

---

## 🖼️ Gallery
Upload source images once to reuse them, saving bandwidth.

```python
client.upload_to_gallery(["face1.jpg", "face2.jpg"])
```

## 📚 Resources

*   **[Official Documentation](https://isamur.ai/documentation)**: Full API reference including Slow Motion and Image Restore.
*   **[Github Repository](https://github.com/isamurai-ai/isamurai-api)**: Raw API examples and scripts.
*   **[Community Support](https://www.reddit.com/r/iSamurai_FaceSwap/)**: Join our detailed discussions on Reddit.

## License

MIT License. See [LICENSE](LICENSE) for details.
